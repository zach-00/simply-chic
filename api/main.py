from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
import os
from routers import appointments, accounts
from datetime import timedelta
import authenticator as authenticator
from authenticator import user_db, Token


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("CORS_HOST", "http://localhost:3000")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(appointments.router)
app.include_router(accounts.router)

ACCESS_TOKEN_EXPIRE_MINUTES = 30


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticator.authenticate_user(user_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
            )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # current_user = await authenticator.get_current_active_user(user)  # Tried finding a way to add current user to access token, hoping this would enabled /token path to actually authenticate user the way authorize button does

    access_token = authenticator.create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
        )

    # print("GET CURRENT ACTIVE USER ****", await authenticator.get_current_active_user(user))

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/")
def root():
    return {"message": "You hit the root path!"}
