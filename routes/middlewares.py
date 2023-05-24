from functools import wraps

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from routes.helpers import sendError

import jwt
import os


async def user_authentication(request: Request):
    if "authorization" not in request.headers:
        raise HTTPException(status_code=401, detail="Unauthorized")

    bearer = request.headers["authorization"]
    token = bearer.split(" ")[1]

    try:
        data = jwt.decode(token, os.environ["SECRET_KEY"], algorithms=["HS256"])
    except Exception as err:
        print(err)
        raise HTTPException(status_code=401, detail="Invalid token")

    request.state.user = data

    return data
