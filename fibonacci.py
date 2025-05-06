from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
import aiosmtplib
from email.message import EmailMessage
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import List
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi import Depends
import secrets

DATABASE_URL = "sqlite:///./fibonacci.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class Serie(Base):
    __tablename__ = "series"
    id = Column(Integer, primary_key=True, index=True)
    hora_ejecucion = Column(String, index=True)
    serie = Column(String)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Serie Fibonacci",
    description="Genera series de Fibonacci a partir de la hora y guarda los resultados. Incluye envío de correo y autenticación.",
    version="1.0.0"
    )

security = HTTPBasic()

class TimeRequest(BaseModel):
    time: str = Field(..., example="12:23:04")
    
class TimeRequestEmail(BaseModel):
    time: str = Field(..., example="12:23:04")
    email: EmailStr   
    subject: str = Field(..., example="Prueba Técnica - Paulo Urbina Zuñiga")

class AutoSendRequest(BaseModel):
    email: EmailStr
    subject: str = Field(..., example="Prueba Técnica - Paulo Urbina Zuñiga")
    
class SerieOut(BaseModel):
    id: int
    hora_ejecucion: str
    serie: str
    
def verificar_credenciales(credentials: HTTPBasicCredentials = Depends(security)):
    usuario_valido = "admin"
    contrasena_valida = "1234"
    
    correcto_usuario = secrets.compare_digest(credentials.username, usuario_valido)
    correcto_password = secrets.compare_digest(credentials.password, contrasena_valida)
    
    if not (correcto_usuario and correcto_password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas", headers={"WWW-Authenticate": "Basic"})
    
    return credentials.username

def fibonacci_desc(a: int, b: int, n: int):
    seq = [a, b]
    for _ in range(n):
        seq.append(seq[-1] + seq[-2])
    return seq[::-1]

async def send_email(recipient: str, subject: str, content: str):
    message = EmailMessage()
    message["From"] = "Paulo Urbina Zuñiga" 
    message["To"] = recipient
    message["Subject"] = "Prueba Técnica - Paulo Urbina Zuñiga"
    message.set_content(content)

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username="paurbi1101@gmail.com",
        password="tghv qqwn klbb ephr"    
    )

def procesar_hora(hora: datetime):
    min1 = int(str(hora.minute).zfill(2)[0])
    min2 = int(str(hora.minute).zfill(2)[1])
    segundos = hora.second
    return min1, min2, segundos, fibonacci_desc(min1, min2, segundos)

@app.post("/fibonacci/manual/pruebas")
async def generar_fibonacci_manual_pruebas(data: TimeRequestEmail, usuario: str = Depends(verificar_credenciales)):
    try:
        hora_manual = datetime.strptime(data.time, "%H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de hora inválido. Usa HH:MM:SS")

    min1, min2, segundos, serie = procesar_hora(hora_manual)
    
    db = SessionLocal()
    nueva_serie = Serie(
        hora_ejecucion=hora_manual.strftime("%H:%M:%S"),
        serie=",".join(map(str, serie))
    )
    db.add(nueva_serie)
    db.commit()
    db.close()
    
    mensaje = (
    f"🔢 *Generación de Serie Fibonacci*\n\n"
    f"🕒 Hora de ejecución: {data.time}\n"
    f"🌱 Semillas iniciales: {min1}, {min2}\n"
    f"📏 Longitud de la serie: {segundos}\n\n"
    f"📋 Serie generada:\n"
    f"{', '.join(map(str, serie))}\n\n"
    f"Atentamente,\n"
    f"Paulo Urbina Zuñiga"
    )
    await send_email(data.email, data.subject, mensaje)

    return {
        "modo": "manual+correo",
        "hora": data.time,
        "semillas": [min1, min2],
        "longitud": segundos,
        "serie": serie
    }
    
@app.post("/fibonacci/manual")
async def generar_fibonacci_manual(data: TimeRequest, usuario: str = Depends(verificar_credenciales)):
    try:
        hora_manual = datetime.strptime(data.time, "%H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de hora inválido. Usa HH:MM:SS")
    
    min1, min2, segundos, serie = procesar_hora(hora_manual)
    
    db = SessionLocal()
    nueva_serie = Serie(
        hora_ejecucion=hora_manual.strftime("%H:%M:%S"),
        serie=",".join(map(str, serie))
    )
    db.add(nueva_serie)
    db.commit()
    db.close()
    
    return {
        "modo": "manual",
        "hora": hora_manual.strftime("%H:%M:%S"),
        "semillas": [min1, min2],
        "longitud": segundos,
        "serie": serie
    }
    
    

@app.post("/fibonacci/auto")
def generar_fibonacci_auto(usuario: str = Depends(verificar_credenciales)):
    hora_actual = datetime.now()
    min1, min2, segundos, serie = procesar_hora(hora_actual)
        
    db = SessionLocal()
    nueva_serie = Serie(
        hora_ejecucion=hora_actual.strftime("%H:%M:%S"),
        serie=",".join(map(str, serie))
    )
    db.add(nueva_serie)
    db.commit()
    db.close()
    
    return {
        "modo": "automático",
        "hora": hora_actual.strftime("%H:%M:%S"),
        "semillas": [min1, min2],
        "longitud": segundos,
        "serie": serie
    }

@app.post("/fibonacci/auto/send")
async def generar_fibonacci_auto_y_enviar(data: AutoSendRequest, usuario: str = Depends(verificar_credenciales)):
    hora_actual = datetime.now()
    min1, min2, segundos, serie = procesar_hora(hora_actual)
        
    db = SessionLocal()
    nueva_serie = Serie(
        hora_ejecucion=hora_actual.strftime("%H:%M:%S"),
        serie=",".join(map(str, serie))
    )
    db.add(nueva_serie)
    db.commit()
    db.close()

    mensaje = (
    f"🔢 *Generación de Serie Fibonacci*\n\n"
    f"🕒 Hora de ejecución: {data.time}\n"
    f"🌱 Semillas iniciales: {min1}, {min2}\n"
    f"📏 Longitud de la serie: {segundos}\n\n"
    f"📋 Serie generada:\n"
    f"{', '.join(map(str, serie))}\n\n"
    f"Atentamente,\n"
    f"Paulo Urbina Zuñiga"
    )
    await send_email(data.email, data.subject, mensaje)

    return {
        "modo": "automático+correo",
        "hora": hora_actual.strftime("%H:%M:%S"),
        "semillas": [min1, min2],
        "longitud": segundos,
        "serie": serie
    }
    
@app.get("/series", response_model=List[SerieOut])
def obtener_series(usuario: str = Depends(verificar_credenciales)):
    db = SessionLocal()
    series = db.query(Serie).all()
    db.close()
    return series

@app.get("/")
def root():
    return {
        "Bienvenido a la API de Serie Fibonacci. Usa /docs para ver la documentación interactiva."
    }