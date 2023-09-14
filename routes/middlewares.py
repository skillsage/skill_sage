from functools import wraps

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from models.user import Role

from routes.helpers import sendError
from typing import List

import jwt
import os


def with_authentication(roles: List[Role]):
    def user_auth(request: Request):
        if "authorization" not in request.headers:
            raise HTTPException(status_code=401, detail="Unauthorized")

        bearer = request.headers["authorization"]
        token = bearer.split(" ")[1]

        try:
            data = jwt.decode(
                token, os.environ["SECRET_KEY"], algorithms=["HS256"])
        except Exception as err:
            print(err)
            raise HTTPException(status_code=401, detail="Invalid token")

        for role in roles:
            if role == data["role"]:
                request.state.user = data
                return data

        raise HTTPException(status_code=401)

    return user_auth
