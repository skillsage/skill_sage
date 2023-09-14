from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.connection import initDB
from routes.user_routes import router, app_router
from routes.auth import auth_router
from routes.courses import router as c_router, app_router as c2_router
from routes.job import router as j_router, app_router as j2_router
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()
initDB()

app.include_router(auth_router)
app.include_router(router)
app.include_router(app_router)
app.include_router(c_router)
app.include_router(c2_router)
app.include_router(j_router)
app.include_router(j2_router)

origins = [
    "http://localhost:3000",
    "https://skill-sage.netlify.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],      
    allow_headers=["*"],  
)


@app.get("/")
def hello_world():
    return "Hello"
