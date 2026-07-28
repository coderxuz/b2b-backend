from typing import List, TYPE_CHECKING
from db.connection import Base
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from db.models.firm import Firm


class Tariff(Base):
    __tablename__ = "tariffs"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    max_shops: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    firms: Mapped[List["Firm"]] = relationship("Firm", back_populates="tariff")
