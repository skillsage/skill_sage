from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder


def sendSuccess(data):
  return {"success": True, "result": jsonable_encoder(data)}

def sendError(data, code=500):
  response = {"success": False, "result": data}
  raise HTTPException(code, response)
