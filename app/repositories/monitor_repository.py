from __future__ import annotations

from sqlalchemy import func, select

from sqlalchemy.orm import Session

from app.db.models import Monitor, MonitorCheck


class MonitorRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> Monitor:
        monitor = Monitor(**data)
        self.db.add(monitor)
        self.db.commit()
        self.db.refresh(monitor)
        return monitor

    def list(self, skip: int = 0, limit: int = 100) -> list[Monitor]:
        return list(self.db.scalars(select(Monitor).order_by(Monitor.id).offset(skip).limit(limit)))

    def get(self, monitor_id: int) -> Monitor | None:
        return self.db.get(Monitor, monitor_id)

    def update(self, monitor: Monitor, data: dict) -> Monitor:
        for key, value in data.items():
            setattr(monitor, key, value)
        self.db.commit()
        self.db.refresh(monitor)
        return monitor

    def delete(self, monitor: Monitor) -> None:
        self.db.delete(monitor)
        self.db.commit()

    def add_check(self, check: MonitorCheck) -> MonitorCheck:
        self.db.add(check)
        self.db.commit()
        self.db.refresh(check)
        return check

    def checks(self, monitor_id: int, skip: int = 0, limit: int = 100) -> list[MonitorCheck]:
        stmt = select(MonitorCheck).where(MonitorCheck.monitor_id == monitor_id).order_by(
            MonitorCheck.checked_at.desc()
        ).offset(skip).limit(limit)
        return list(self.db.scalars(stmt))

    def latest_check(self, monitor_id: int) -> MonitorCheck | None:
        stmt = select(MonitorCheck).where(MonitorCheck.monitor_id == monitor_id).order_by(
            MonitorCheck.checked_at.desc()
        ).limit(1)
        return self.db.scalar(stmt)

    def summary(self) -> dict:
        total = self.db.scalar(select(func.count()).select_from(Monitor)) or 0
        active = self.db.scalar(select(func.count()).select_from(Monitor).where(Monitor.is_active.is_(True))) or 0
        available = self.db.scalar(
            select(func.count()).select_from(MonitorCheck).where(
                MonitorCheck.id.in_(
                    select(func.max(MonitorCheck.id)).group_by(MonitorCheck.monitor_id)
                ),
                MonitorCheck.is_available.is_(True),
            )
        ) or 0
        return {"total_monitors": total, "active_monitors": active, "currently_available": available}
