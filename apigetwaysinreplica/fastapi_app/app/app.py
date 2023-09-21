import socket
from fastapi import FastAPI

hostname = socket.gethostname()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": f"Kaixo Mundua! (by {hostname})"}


@app.get("/client")
def s1():
    return {"message": f"Executing Cliente WS - API GETWAY 1 (by {hostname})"}


@app.get("/delivery")
def s2():
    return {"message": f"Executing Delivery WS - API GETWAY (by {hostname})"}


@app.get("/machine")
def s2():
    return {"message": f"Executing MACHINE WS - API GETWAY (by {hostname})"}


@app.get("/order")
def s2():
    return {"message": f"Executing ORDER WS - API GETWAY (by {hostname})"}


@app.get("/payment")
def s2():
    return {"message": f"Executing PAYMENT WS - API GETWAY (by {hostname})"}