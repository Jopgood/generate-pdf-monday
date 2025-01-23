# main.py
from fastapi import Depends, FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError
import uvicorn
import jwt
from dotenv import load_dotenv
import os
import logging
from logging_config import setup_logging, LoggerAdapter
from monday_routes import monday_router


logger = LoggerAdapter(setup_logging(), "main")

load_dotenv()
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication middleware


async def authenticate(request: Request):
    logger_auth = LoggerAdapter(logger.logger, "auth")
    authorization = request.headers.get(
        "Authorization") or request.query_params.get("token")

    if not authorization:
        logger_auth.log_operation(
            logging.WARNING,
            "authenticate",
            "Authentication failed - no token provided"
        )
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        if authorization.startswith("Bearer "):
            authorization = authorization.split(" ")[1]

        payload = jwt.decode(
            authorization,
            os.getenv("MONDAY_SIGNING_SECRET"),
            algorithms=["HS256"],
            options={"verify_aud": False}
        )
        request.state.session = payload
        logger_auth.log_operation(
            logging.INFO,
            "authenticate",
            "Authentication successful",
            {"user_id": payload.get("user_id")}
        )
        return payload

    except JWTError as e:
        logger_auth.log_operation(
            logging.ERROR,
            "authenticate",
            "JWT validation failed",
            {"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        logger_auth.log_operation(
            logging.ERROR,
            "authenticate",
            "Unexpected authentication error",
            {"error": str(e)},
            exc_info=True
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    return {"ok": True, "message": "Healthy"}

app.include_router(monday_router, prefix="/monday",
                   dependencies=[Depends(authenticate)])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
