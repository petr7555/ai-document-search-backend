from typing import Annotated

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

LOCKOUT_TIME_SECONDS = 60 * 15
LOCKOUT_INTERVAL_SECONDS = 60 * 5
MAX_LOGIN_ATTEMPTS = 5


class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool
    disabled_time: datetime
    failed_logins: list


class UserInDB(User):
    password: str


fake_users_db = {
    "marius": {
        "username": "marius",
        "full_name": "Marius Berdal Gaalaas",
        "email": "marius@gmail.com",
        "password": "123",
        "disabled": False,
        "disabled_time": 0,
        "failed_logins": [],
    }
}

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Called on failed login
# Checks how many recent login failures the user has, if over the limit, disable them
def check_lockout(username: str):
    user_dict = fake_users_db.get(username)
    lockout_interval = timedelta(seconds=LOCKOUT_INTERVAL_SECONDS)
    now = datetime.utcnow()
    for login_fail in user_dict["failed_logins"].copy():
        if login_fail + lockout_interval < now:
            user_dict["failed_logins"].remove(login_fail)

    user_dict["failed_logins"].append(datetime.utcnow())
    if len(user_dict["failed_logins"]) >= MAX_LOGIN_ATTEMPTS:
        user_dict["disabled"] = True
        user_dict["disabled_time"] = datetime.utcnow()
        print("LOCKOUT")
        return True
    return False


# Called to check if disabled user should be opened again
def check_lockin(username: str):
    user_dict = fake_users_db.get(username)
    timedelta_expire = timedelta(seconds=LOCKOUT_TIME_SECONDS)
    if user_dict["disabled"] and user_dict["disabled_time"] + timedelta_expire < datetime.utcnow():
        print("LOCKIN")
        user_dict["disabled"] = False
        user_dict["disabled"] = 0
        return True
    return False


# For authenticating
@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)  # TODO: Make proper users
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    password = form_data.password
    if user.disabled and not check_lockin(user.username):
        raise HTTPException(
            status_code=400, detail="Failed login attempts exceed limit. Account locked."
        )
    if not password == user.password:
        if check_lockout(user.username):
            raise HTTPException(
                status_code=400, detail="Failed login attempts exceed limit. Account locked."
            )
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user_dict["failed_logins"].clear()
    return {"access_token": user.username, "token_type": "bearer"}
