import ipaddress
import socket
import time
from urllib.parse import urlsplit

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import MonitorCheck
from app.repositories.monitor_repository import MonitorRepository


class MonitorNotFoundError(Exception):
    pass


class UnsafeTargetError(Exception):
    pass


def validate_public_target(url: str) -> None:
    """Reject localhost, private, link-local and reserved IP destinations (basic SSRF defense)."""
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise UnsafeTargetError("Only valid HTTP/HTTPS destinations are allowed")
    host = parsed.hostname.lower().rstrip(".")
    if host in {"localhost", "metadata.google.internal"} or host.endswith(".localhost"):
        raise UnsafeTargetError("Local and metadata destinations are not allowed")
    try:
        addresses = [ipaddress.ip_address(host)]
    except ValueError:
        try:
            addresses = [ipaddress.ip_address(item[4][0]) for item in socket.getaddrinfo(host, None)]
        except socket.gaierror:
            raise UnsafeTargetError("Hostname could not be resolved") from None
    if not addresses or any(not address.is_global for address in addresses):
        raise UnsafeTargetError("Private, local, link-local and reserved destinations are not allowed")


class MonitorService:
    def __init__(self, db: Session):
        self.repo = MonitorRepository(db)

    def get_or_404(self, monitor_id: int):
        monitor = self.repo.get(monitor_id)
        if monitor is None:
            raise MonitorNotFoundError
        return monitor

    def run_check(self, monitor_id: int):
        monitor = self.get_or_404(monitor_id)
        validate_public_target(monitor.url)
        started = time.perf_counter()
        status_code = None
        error_message = None
        available = False
        response_time = None
        try:
            with httpx.Client(timeout=settings.check_timeout_seconds, follow_redirects=False) as client:
                with client.stream("GET", monitor.url) as response:
                    status_code = response.status_code
                    # Read only a bounded amount; monitoring does not need the full body.
                    bytes_read = 0
                    for chunk in response.iter_bytes():
                        bytes_read += len(chunk)
                        if bytes_read > settings.max_response_bytes:
                            break
                    available = 200 <= status_code < 400
        except httpx.TimeoutException:
            error_message = "Request timed out"
        except httpx.RequestError as exc:
            error_message = f"Connection/request error: {type(exc).__name__}"
        finally:
            response_time = round((time.perf_counter() - started) * 1000, 2)

        check = MonitorCheck(
            monitor_id=monitor.id,
            status_code=status_code,
            response_time_ms=response_time,
            is_available=available,
            error_message=error_message,
        )
        return self.repo.add_check(check)
