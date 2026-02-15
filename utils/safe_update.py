from datetime import datetime, timezone

PROTECTED_FIELDS = {"id", "created_at", "created_by"}


def apply_update(entity, update_data: dict) -> None:
    filtered = {
        k: v for k, v in update_data.items() if k not in PROTECTED_FIELDS
    }
    for field, value in filtered.items():
        setattr(entity, field, value)
    if hasattr(entity, "updated_at"):
        entity.updated_at = datetime.now(timezone.utc)
