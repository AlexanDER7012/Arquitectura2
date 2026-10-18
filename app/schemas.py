import html
import unicodedata
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, field_serializer

from app.models import EstadoMensaje


def limpiar_texto(valor: str) -> str:

    normalizado = unicodedata.normalize("NFKD", valor)
    sin_tildes = "".join(c for c in normalizado if not unicodedata.combining(c))
    imprimibles = "".join(c for c in sin_tildes if c.isprintable())
    return " ".join(imprimibles.split())


# ---------- Entrada: Postman API ----------
class MensajeCreate(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=50, examples=["BIENVENIDOS A UMG"])
    velocidad: int = Field(100, ge=20, le=500, description="ms por paso del scroll")

    @field_validator("mensaje")
    @classmethod
    def validar_mensaje(cls, v: str) -> str:
        limpio = limpiar_texto(v)
        if not limpio:
            raise ValueError("El mensaje no puede estar vacio")
        if any(ord(c) < 32 or ord(c) > 126 for c in limpio):
            raise ValueError("Solo letras, numeros y simbolos basicos")
        return limpio


# ---------- Entrada: ESP32  API (ACK) ----------
class ConfirmarRequest(BaseModel):
    id: int = Field(..., gt=0)
    dispositivo_id: str = Field(..., min_length=1, max_length=50, examples=["ESP32_LAB_01"])


# ---------- Salida: historial (sanitizado contra XSS) ----------
class MensajeResponse(BaseModel):
    id: int
    mensaje: str
    longitud: int
    estado: EstadoMensaje
    velocidad: int
    ip_origen: str | None
    dispositivo_id: str | None
    fecha_creacion: datetime
    fecha_emision: datetime | None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("mensaje")
    def escapar_xss(self, v: str) -> str:
        return html.escape(v) 


# ---------- Salida: lo que recibe el ESP32 ----------
class MensajeDispositivo(BaseModel):
    id: int
    mensaje: str
    velocidad: int

    model_config = ConfigDict(from_attributes=True)