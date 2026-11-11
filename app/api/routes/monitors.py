from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.monitor_repository import MonitorRepository
from app.schemas.monitor import MonitorCreate, MonitorRead, MonitorUpdate
from app.schemas.monitor_check import MonitorCheckRead, MonitorStatus
from app.services.monitor_service import MonitorNotFoundError, MonitorService, UnsafeTargetError

router = APIRouter(prefix="/monitors", tags=["Monitors"])


@router.post("", response_model=MonitorRead, status_code=status.HTTP_201_CREATED)
def create_monitor(payload: MonitorCreate, db: Session = Depends(get_db)):
    # URL policy is enforced before any outgoing request; checks perform DNS/IP validation.
    data = payload.model_dump(mode="json")
    data["url"] = str(payload.url)
    return MonitorRepository(db).create(data)


@router.get("", response_model=list[MonitorRead])
def list_monitors(skip: int = 0, limit: int = Query(default=100, ge=1, le=200), db: Session = Depends(get_db)):
    return MonitorRepository(db).list(skip=skip, limit=limit)


@router.get("/{monitor_id}", response_model=MonitorRead)
def get_monitor(monitor_id: int, db: Session = Depends(get_db)):
    try:
        return MonitorService(db).get_or_404(monitor_id)
    except MonitorNotFoundError:
        raise HTTPException(status_code=404, detail="Monitor not found") from None


@router.patch("/{monitor_id}", response_model=MonitorRead)
def update_monitor(monitor_id: int, payload: MonitorUpdate, db: Session = Depends(get_db)):
    repo = MonitorRepository(db)
    monitor = repo.get(monitor_id)
    if monitor is None:
        raise HTTPException(status_code=404, detail="Monitor not found")
    data = payload.model_dump(exclude_unset=True, mode="json")
    if "url" in data and data["url"] is not None:
        data["url"] = str(payload.url)
    return repo.update(monitor, data)


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitor(monitor_id: int, db: Session = Depends(get_db)):
    repo = MonitorRepository(db)
    monitor = repo.get(monitor_id)
    if monitor is None:
        raise HTTPException(status_code=404, detail="Monitor not found")
    repo.delete(monitor)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{monitor_id}/check", response_model=MonitorCheckRead)
def check_monitor(monitor_id: int, db: Session = Depends(get_db)):
    try:
        return MonitorService(db).run_check(monitor_id)
    except MonitorNotFoundError:
        raise HTTPException(status_code=404, detail="Monitor not found") from None
    except UnsafeTargetError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None


@router.get("/{monitor_id}/checks", response_model=list[MonitorCheckRead])
def get_checks(
    monitor_id: int,
    skip: int = 0,
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
):
    repo = MonitorRepository(db)
    if repo.get(monitor_id) is None:
        raise HTTPException(status_code=404, detail="Monitor not found")
    return repo.checks(monitor_id, skip=skip, limit=limit)


@router.get("/{monitor_id}/status", response_model=MonitorStatus)
def get_status(monitor_id: int, db: Session = Depends(get_db)):
    service = MonitorService(db)
    try:
        monitor = service.get_or_404(monitor_id)
    except MonitorNotFoundError:
        raise HTTPException(status_code=404, detail="Monitor not found") from None
    latest = service.repo.latest_check(monitor_id)
    return {"monitor_id": monitor.id, "is_active": monitor.is_active, "last_check": latest}
