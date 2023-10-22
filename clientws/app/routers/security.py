import cryptography
from fastapi import APIRouter, Depends, status, Header
import logging
import jwt
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from routers.router_utils import raise_and_log_error
import json

logger = logging.getLogger(__name__)


def generar_claves():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Serializar la clave privada en formato PKCS #8
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )

    # Almacenar la clave privada en un archivo
    with open('private_key.pem', 'wb') as private_key_file:
        private_key_file.write(private_key_pem)

    # Generar la clave pública correspondiente
    public_key = private_key.public_key()

    # Serializar la clave pública en formato PKCS #8
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.PKCS1
    )

    # Almacenar la clave pública en un archivo
    with open('public_key.pem', 'wb') as public_key_file:
        public_key_file.write(public_key_pem)

def decode_token(token:str):
    try:
        with open('public_key.pem', 'rb') as public_key_file:
                public_key_client_pem = public_key_file.read()

        payload = json.loads(json.dumps(jwt.decode(token, public_key_client_pem, ['RS256'])))
        return payload
    except Exception as exc:  # @ToDo: To broad exception
        raise_and_log_error(logger, status.HTTP_403_CONFLICT, f"Error decoding the token: {exc}")

def validar_fecha_expiracion(payload:dict):
    # Obtiene la fecha de expiración del token
    exp_timestamp_str = payload.get("fecha_expiracion")
    exp_timestamp_datetime = datetime.fromisoformat(exp_timestamp_str)
    exp_timestamp = exp_timestamp_datetime.timestamp()
    # Convierte el tiempo Unix en una fecha y hora
    exp_datetime = datetime.utcfromtimestamp(exp_timestamp)
    # Comprueba si el token ha expirado
    if exp_datetime <= datetime.utcnow():
        return True
    else:
        return False

def validar_es_admin(payload:dict):
    # Obtiene la fecha de expiración del token
    role = payload.get("role")
    print("comprobacionnnnnnn")
    print(type(role))
    print(role)
    # Convierte el tiempo Unix en una fecha y hora
    # Comprueba si el token ha expirado
    if role==1:
        return True
    else:
        return False