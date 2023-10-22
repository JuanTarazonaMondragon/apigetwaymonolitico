# -*- coding: utf-8 -*-
"""FastAPI router definitions."""
import logging
from typing import List
from fastapi import APIRouter, Depends, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from dependencies import get_db
from routers import security
from sql import crud, schemas
from routers.router_utils import raise_and_log_error

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import jwt
import json

from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    summary="Health check endpoint",
    response_model=schemas.Message,
)
async def health_check():
    """Endpoint to check if everything started correctly."""
    logger.debug("GET '/' endpoint called.")
    return {
        "detail": "OK"
    }


@router.post(
    "/client",
    response_model=schemas.Client,
    summary="Create single client",
    status_code=status.HTTP_201_CREATED,
    tags=["Client"]
)
async def create_client(
        client_schema: schemas.ClientPost,
        db: AsyncSession = Depends(get_db),
        token: str = Header(..., description="JWT Token in the Header")
):
    """Create single client endpoint."""
    logger.debug("POST '/client' endpoint called.")
    try:
        #decodificar el token
        payload = security.decode_token(token)
        # validar fecha expiración del token
        is_expirated = security.validar_fecha_expiracion(payload)
        if(is_expirated):
            raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"The token is expired, please log in again")
        else:
            es_admin = security.validar_es_admin(payload)
            if(es_admin):
                db_client = await crud.create_client(db, client_schema)
                return db_client 
            else:
                raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"You don't have permissions")

    except Exception as exc:  # @ToDo: To broad exception
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error creating client: {exc}")


@router.get(
    "/client",
    response_model=List[schemas.Client],
    summary="Retrieve client list",
    tags=["Client", "List"]  # Optional so it appears grouped in documentation
)
async def get_client_list(
        db: AsyncSession = Depends(get_db)
):
    """Retrieve client list"""
    logger.debug("GET '/client' endpoint called.")
    client_list = await crud.get_client_list(db)
    return client_list


@router.get(
    "/client/{client_id}",
    summary="Retrieve single client by id",
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Client,
            "description": "Requested Client."
        },
        status.HTTP_404_NOT_FOUND: {
            "model": schemas.Message, "description": "Client not found"
        }
    },
    tags=['Client']
    
)
async def get_single_client(
        client_id: int,
        db: AsyncSession = Depends(get_db),
        token: str = Header(..., description="JWT Token in the Header")
):
    """Retrieve single client by id"""
    logger.debug("GET '/client/%i' endpoint called.", client_id)
      
    payload = security.decode_token(token)
    # validar fecha expiración del token
    is_expirated = security.validar_fecha_expiracion(payload)
    if(is_expirated):
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"The token is expired, please log in again")
    else:
        es_admin = security.validar_es_admin(payload)
        if(es_admin==False):
            raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"You don't have permissions")
        
    client = await crud.get_client(db, client_id)
    if not client:
        raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, f"Client {client_id} not found")
    return client



@router.post(
    "/client/auth",
    summary="Obtener token",
    status_code=status.HTTP_200_OK,
    tags=["Client"]
)
async def get_token(
        request_data: schemas.TokenRequest,  # Debes crear un esquema TokenRequest para manejar los datos
        db: AsyncSession = Depends(get_db)
):
    """Obtener token JWT."""
    logger.debug("POST '/auth/token' endpoint called.")
    try:
        username = request_data.username
        password = request_data.password

        # Realiza la autenticación aquí (sustituye esto con tu lógica real)
        client = await crud.get_client_by_username_and_pass(db, username, password)
        if not client:
            authenticated = False
            raise_and_log_error(logger, status.HTTP_404_NOT_FOUND, f"Client {username} not found")
        else: 
            authenticated = True

        if authenticated:
            # Aquí puedes generar un token JWT si la autenticación es exitosa
            with open('private_key.pem', 'rb') as private_key_file:
                private_key_pem = private_key_file.read()
            
            #print(private_key_pem)
            expiration_time = datetime.utcnow() + timedelta(hours=3)
            expiration_time_serializable = expiration_time.isoformat()
            print(expiration_time)
            payload = {'username': client.username, 'id_client':client.id_client, 'email':client.email, 'role': client.role, 'fecha_expiracion': expiration_time_serializable}
            token = jwt.encode(payload, private_key_pem, algorithm='RS256')
            return {"token": token}
        else:
            return {"message": "Credenciales incorrectas"}, 401    
    except Exception as exc:
        raise_and_log_error(logger, status.HTTP_409_CONFLICT, f"Error generando token: {exc}")



# Función para autenticar al usuario (solo como ejemplo)
def authenticate(username, password):
    # Aquí puedes agregar lógica de autenticación, como verificar en una base de datos
    # Si el usuario y la contraseña son válidos, devuelve True; de lo contrario, False.
    if username == 'usuario' and password == 'password':
        return True
    else:
        return False
