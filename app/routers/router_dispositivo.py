from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Mensaje, EstadoMensaje
from app.schemas import ConfirmarRequest, MensajeDispositivo, MensajeResponse
from app.security import verificar_token

# Todas las rutas de este router exigen el token
router = APIRouter(dependencies=[Depends(verificar_token)])


@router.get(
    "/dispositivo",
    response_model=MensajeDispositivo,
    summary="Polling del ESP32: entrega el pendiente más antiguo",
    responses={204: {"description": "No hay mensajes pendientes"}},
)
def obtener_pendiente(
    dispositivo_id: str = Query(..., min_length=1, max_length=50, examples=["ESP32_LAB_01"]),
    db: Session = Depends(get_db),
):
    consulta = (
        select(Mensaje)
        .where(Mensaje.estado == EstadoMensaje.PENDIENTE)
        .order_by(Mensaje.id.asc())          # el más antiguo primero (FIFO)
        .limit(1)
        .with_for_update(skip_locked=True)   # bloquea la fila mientras se procesa
    )
    mensaje = db.scalars(consulta).first()

    if not mensaje:
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    mensaje.estado = EstadoMensaje.PROCESANDO   # UPDATE
    mensaje.dispositivo_id = dispositivo_id
    db.commit()
    db.refresh(mensaje)
    return mensaje


@router.post(
    "/confirmar",
    response_model=MensajeResponse,
    summary="ACK del ESP32: marca el mensaje como EMITIDO",
)
def confirmar_emision(datos: ConfirmarRequest, db: Session = Depends(get_db)):
    mensaje = db.get(Mensaje, datos.id)

    if not mensaje:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    if mensaje.estado != EstadoMensaje.PROCESANDO:
        raise HTTPException(
            status_code=409,
            detail=f"El mensaje está en estado {mensaje.estado.value}, no PROCESANDO",
        )
    if mensaje.dispositivo_id != datos.dispositivo_id:
        raise HTTPException(status_code=409, detail="El mensaje fue asignado a otro dispositivo")

    mensaje.estado = EstadoMensaje.EMITIDO      # UPDATE
    mensaje.fecha_emision = datetime.now(timezone.utc)
    db.commit()
    db.refresh(mensaje)
    return mensaje