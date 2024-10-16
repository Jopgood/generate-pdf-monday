# main.py
from fastapi import HTTPException


from fastapi import Request

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from jose import JWTError
import uvicorn
import jwt
from dotenv import load_dotenv
import os

from monday_routes import monday_router


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
    authorization = request.headers.get(
        "Authorization") or request.query_params.get("token")
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        # Split the Authorization header in case it's "Bearer <token>"
        if authorization.startswith("Bearer "):
            authorization = authorization.split(" ")[1]

        payload = jwt.decode(
            authorization,
            os.getenv("MONDAY_SIGNING_SECRET"),
            algorithms=["HS256"],
            options={"verify_aud": False}  # Disable audience verification
        )
        request.state.session = payload
        return payload
    except JWTError as e:
        print(f"JWT Error: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"Unexpected error during authentication: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

app.include_router(monday_router, prefix="/monday",
                   dependencies=[Depends(authenticate)])


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/health")
async def health():
    return {"ok": True, "message": "Healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
