import socket
from fastapi import FastAPI

hostname = socket.gethostname()
app = FastAPI()


@app.get("/")
async def root():
    return {"message": f"Kaixo Machine! (by {hostname})"}


@app.get("/machine")
def s1():
    return {"message": f"Executing Service Machine WS (by {hostname})"}
