from typing import Optional, TYPE_CHECKING
from db.connection import Base
from sqlalchemy import BigInteger, String, Text, Numeric, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from db.models.firm import Firm
    from db.models.product_category import ProductCategory


class Product(Base):
    __tablename__ = "products"

    firm_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("firms.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("product_categories.id", ondelete="SET NULL"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False, default=0.0)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    video: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    firm: Mapped["Firm"] = relationship("Firm", back_populates="products")
    category: Mapped[Optional["ProductCategory"]] = relationship("ProductCategory", back_populates="products")
