import enum
from datetime import datetime

from sqlalchemy import String, Integer, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class EstadoMensaje(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    PROCESANDO = "PROCESANDO"
    EMITIDO = "EMITIDO"


class Mensaje(Base):
    __tablename__ = "mensajes_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    mensaje: Mapped[str] = mapped_column(String(50), nullable=False)
    longitud: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[EstadoMensaje] = mapped_column(
        Enum(EstadoMensaje, native_enum=False, length=20),
        nullable=False,
        default=EstadoMensaje.PENDIENTE,
        index=True,
    )
    velocidad: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    ip_origen: Mapped[str | None] = mapped_column(String(45))
    dispositivo_id: Mapped[str | None] = mapped_column(String(50))
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    fecha_emision: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))