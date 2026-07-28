from enum import Enum
import datetime
from typing import Optional, TYPE_CHECKING

from db.connection import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func

if TYPE_CHECKING:
    from db.models.firm import Firm


class UserRole(str, Enum):
    DISTRIBUTOR = "distributor"
    SHOP_OWNER = "shop_owner"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    age: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    phone: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role", create_type=True),
        default=UserRole.SHOP_OWNER,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="t", nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    firm: Mapped[Optional["Firm"]] = relationship("Firm", back_populates="owner", uselist=False)
