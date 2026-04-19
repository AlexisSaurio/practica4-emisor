import os
from dataclasses import dataclass
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
import json
import boto3

expediente = "Alexis Geovanni Flores Vazquez" 
nombre_completo = "Alexis Geovanni Flores Vazquez"

app = FastAPI(title="Practica 4 - Emisor")


S3_BUCKET = os.getenv("S3_BUCKET", "practica-4-752798")
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME", "cola-boletines")
REGION = os.getenv("AWS_REGION", "us-east-1")

def s3_client():
    return boto3.client('s3', region_name=REGION)

def sqs_client():
    return boto3.client('sqs', region_name=REGION)

def s3_upload_file(file: UploadFile, filename: str) -> str:
    cliente = s3_client()
    cliente.upload_fileobj(file.file, S3_BUCKET, filename)
    return f"https://{S3_BUCKET}.s3.{REGION}.amazonaws.com/{filename}"

def sqs_get_queue_url() -> str:
    cliente = sqs_client()
    response = cliente.get_queue_url(QueueName=SQS_QUEUE_NAME)
    return response['QueueUrl']

def sqs_send_message(queue_url: str, correo: str, mensaje: str, s3_url: str) -> None:
    cliente = sqs_client()
    cuerpo_mensaje = {
        'correo': correo,
        'mensaje': mensaje,
        'imagen_url': s3_url
    }
    
    cliente.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(cuerpo_mensaje)
    )

def handle_crear_boletin(archivo: UploadFile, mensaje: str, correo: str) -> Dict[str, Any]:
    if not archivo or not mensaje or not correo:
        raise HTTPException(status_code=400, detail="Faltan parámetros (archivo, mensaje o correo)")
    
    try:
        filename = archivo.filename.replace(" ", "_")
        s3_url = s3_upload_file(archivo, filename)
        
        queue_url = sqs_get_queue_url()
        sqs_send_message(queue_url, correo, mensaje, s3_url)
        
        return {
            "status": "success",
            "message": "Boletín procesado y enviado a la cola correctamente",
            "s3_url": s3_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/boletines", status_code=201)
def crear_boletin(
    archivo: UploadFile = File(...),
    mensaje: str = Form(...),
    correo: str = Form(...)
):
    return handle_crear_boletin(archivo, mensaje, correo)





preguntas = """
1. ¿Qué función cumple SQS dentro de esta arquitectura?
por lo que vi , funciona como tun tipo de fila , donde sqs guaarda los mensajes que envias hasta que lleguen con el emisor y sean leidos
2. ¿Por qué es útil desacoplar el emisor del receptor?
en mi clase de diseno de software vimos que una de los principios es la responsabilidad unica y creo que cabe aqui , ya que pues son 2 cosas que en si no tienen nada que ver
y se pueden separar de manera facil , ademas de que nos evitamos errores si alguno de los 2 llegara a fallar 
3. ¿Qué ventajas ofrece SNS en este flujo?
pues lo chido es quee te deja mandar el mismo mensaje a muchos lugares al mismo tiempo
"""

conclusiones = """
hijo de su sambomba madre, ODIE esta practica , con la parte de el codigo no huboo tanto problema , todo funciono relativamente bien a la primera el mayor problema que tuve
esta practica fue docker , al momento de intentar subir mis cosas a docker me daba este error error saving credentials: error storing credentials - err: exit status 1, out: Not enough memory resources are available to process this command.,
estuve HORAS intentando arreglar esto , use todas las IA's , hilos de reddit y publicaciones pocibles , por lo que vi este error da por 2 motivos , tus credenciales de docker se corrompieron
o por algun motivo falta memoria ram para ccumplir la accion , y pues la segundda no era , entonces me puse a borrar un friego de credenciales en el gestor de credenciales
de windows y tampoco funciono , le movi a la configuracion de docker en su config.json y tampoco funciono , logre hacer que funcionara gracias a un amigo , que me mostro
una forma con un archivo llamado docker-credential-ecr-login-windows-amd64.exe , se lo puse al system 32 y no se como y por que peero funciono y ya luego de eso no hubo tanto
problema , aprendi a usar cosas con las que no tenia mucha familiaridad como la consola de ec2 o por ejemplo las ip elasticas que las utilice para que mi proyecto solo tuviera una 
IP y que aunque reinicie el leb no se pieerda esa ip.
De ahi en mas todo bien , el proyecto sirve y eso me hace feliz 
"""