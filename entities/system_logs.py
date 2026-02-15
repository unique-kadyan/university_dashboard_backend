from sqlalchemy import Column, DateTime, Enum, Integer, String, ForeignKey, Index, func

from configs.db_config import Base
from enums.log_levels import LogLevel


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    log_level = Column(Enum(LogLevel), nullable=False)
    message = Column(String, nullable=False)
    module = Column(String, nullable=True)
    function = Column(String, nullable=True)
    stack_trace = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    request_id = Column(String, nullable=True)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

    __table_args__ = (
        Index("idx_system_logs_log_level", "log_level"),
        Index("idx_system_logs_timestamp", "timestamp"),
        Index("idx_system_logs_user_id", "user_id"),
        Index("idx_system_logs_request_id", "request_id"),
    )
