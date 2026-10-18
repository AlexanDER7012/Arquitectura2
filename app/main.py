from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers import router_mensaje, router_dispositivo

app = FastAPI(
    title="API Matriz LED 8x8",
    description="Proyecto Arquitectura de Computadoras II - ESP32 + MAX7219 por SPI",
    version="1.0.0",
)

app.include_router(router_mensaje.router, tags=["Mensajes"])
app.include_router(router_dispositivo.router, tags=["Dispositivo (ESP32)"])


@app.get("/api/status", tags=["Estado"])
def read_status(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "Online", "base_de_datos": "ok", "docs": "/docs"}