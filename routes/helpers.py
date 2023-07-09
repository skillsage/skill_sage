from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
import hashlib

def sendSuccess(data):
  return {"success": True, "result": jsonable_encoder(data)}

def sendError(data, code=500):
  response = {"success": False, "result": data}
  raise HTTPException(code, response)


def getSha(file):
  m = hashlib.sha1()
  m.update(file)
  return m.hexdigest()