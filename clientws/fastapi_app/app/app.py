import socket
from fastapi import FastAPI

hostname = socket.gethostname()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": f"Kaixo Client! (by {hostname})"}


@app.get("/client")
def s1():
    return {"message": f"Executing Service Client WS (by {hostname})"}
