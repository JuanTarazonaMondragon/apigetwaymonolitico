import socket
from fastapi import FastAPI

hostname = socket.gethostname()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": f"Kaixo Order! (by {hostname})"}


@app.get("/order")
def s1():
    return {"message": f"Executing Service Order WS (by {hostname})"}
