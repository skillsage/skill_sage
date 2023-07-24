
from fastapi import APIRouter, Request, Depends, status, UploadFile, Response


router = APIRouter(prefix="/", tags=["common"])

