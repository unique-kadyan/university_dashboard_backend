from sqlalchemy import JSON, Column, DateTime, Integer, String, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import INET

from configs.db_config import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    entity_name = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(Integer, nullable=False)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    ip_address = Column(INET, nullable=True)
    user_agent = Column(String, nullable=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_audit_logs_user_id", "user_id"),
        Index("idx_audit_logs_entity_type", "entity_type"),
        Index("idx_audit_logs_timestamp", "timestamp"),
    )
