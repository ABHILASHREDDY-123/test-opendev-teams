from fastapi import FastAPI
from auth import app as auth_app

app = FastAPI()

app.include_router(auth_app, prefix='/auth')