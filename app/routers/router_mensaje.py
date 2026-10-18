from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Mensaje, EstadoMensaje
from app.schemas import MensajeCreate, MensajeResponse

router = APIRouter()


@router.post(
    "/mensaje",
    response_model=MensajeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un mensaje (queda PENDIENTE)",
)
def crear_mensaje(datos: MensajeCreate, request: Request, db: Session = Depends(get_db)):
    nuevo = Mensaje(
        mensaje=datos.mensaje,
        longitud=len(datos.mensaje),
        velocidad=datos.velocidad,
        estado=EstadoMensaje.PENDIENTE,
        ip_origen=request.client.host if request.client else None,
    )
    db.add(nuevo)        
    db.commit()
    db.refresh(nuevo)
    return nuevo


@router.get(
    "/mensajes",
    response_model=list[MensajeResponse],
    summary="Historial de mensajes (filtro opcional por estado)",
)
def listar_mensajes(
    estado: EstadoMensaje | None = Query(None, description="Filtrar por estado"),
    limite: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    consulta = select(Mensaje).order_by(Mensaje.id.desc()).limit(limite)
    if estado:
        consulta = consulta.where(Mensaje.estado == estado)   # consulta filtrada
    return db.scalars(consulta).all()


@router.get(
    "/mensajes/{mensaje_id}",
    response_model=MensajeResponse,
    summary="Consultar un mensaje por ID",
)
def obtener_mensaje(mensaje_id: int, db: Session = Depends(get_db)):
    mensaje = db.get(Mensaje, mensaje_id)
    if not mensaje:
        raise HTTPException(status_code=404, detail="Mensaje no encontrado")
    return mensaje