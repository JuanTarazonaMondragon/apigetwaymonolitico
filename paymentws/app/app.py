import socket
from fastapi import FastAPI

hostname = socket.gethostname()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": f"Kaixo Payment! (by {hostname})"}


@app.get("/payment")
def s1():
    return {"message": f"Executing Service Payment WS (by {hostname})"}
