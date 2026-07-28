from typing import List, Optional, TYPE_CHECKING
from db.connection import Base
from sqlalchemy import BigInteger, String, Text, Boolean, ForeignKey, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from db.models.user import User
    from db.models.tariff import Tariff
    from db.models.product import Product


class Firm(Base):
    __tablename__ = "firms"

    owner_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    tariff_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("tariffs.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    inn: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    mfo: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    firm_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    additional_phones: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String(20)), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="t", nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="firm")
    tariff: Mapped[Optional["Tariff"]] = relationship("Tariff", back_populates="firms")
    products: Mapped[List["Product"]] = relationship("Product", back_populates="firm", cascade="all, delete-orphan")
