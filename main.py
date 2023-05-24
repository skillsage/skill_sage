from fastapi import FastAPI
from db.connection import initDB
from routes.user_routes import router
from routes.auth import auth_router
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()
initDB()

app.include_router(auth_router)
app.include_router(router)

@app.get("/")
def hello_world():
    return "Hello"

