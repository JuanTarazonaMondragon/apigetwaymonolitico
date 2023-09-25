import socket
from fastapi import FastAPI

hostname = socket.gethostname()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": f"Kaixo Delivery! (by {hostname})"}


@app.get("/delivery")
def s1():
    return {"message": f"Executing Service Delivery WS (by {hostname})"}
