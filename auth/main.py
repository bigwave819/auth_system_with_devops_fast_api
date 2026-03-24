from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
import models, schemas, utils
from auth_database import get_db
from jose import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError

SECRET_KEY = "bLXolj5Vlv-FFNFABHeEnQ15cu4L-qV80_kzSG3RzfI"
ALGORITHM = "SH256"
ACCESS_TOKEN_EXPIRATION_MINUTE = 30

#helper function that takes our user data

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTE)
    to_encode.update({ "expire": expire })
    to_encode = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return to_encode

app = FastAPI()

@app.post("/signup")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # check if user exists
    existing_user = db.query(models.user).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # hash password
    hashed_password = utils.hash_password(user.password)

    # Create new User
    new_user = models.User(
        username = user.username,
        email = user.email,
        hashed_password = hashed_password,
        role  = user.role
    )

    # save user to database

    db.add(new_user)
    db.commit()
    db.refresh()


    # Return the value (exclude password)

    return { 'id': new_user.id, "username": new_user.username, "email": new_user.email, "role": new_user.role }


@app.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Username")
    
    if not utils.verify_password(form_data.password, user.hashedPassword):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password")
    
    token_data = { "sub": user.username, "role": user.role }
    token = create_access_token(token_data)
    return { "access_token": token, "token_type": "bearer" }


oauth2_schema = OAuth2PasswordRequestForm(token_url="login")
def get_the_current_user(token: str = Depends(oauth2_schema)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate the Credential")
    headers=({"WW-authenicate": "Bearer"})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credential_exception
        
    except JWTError:
        raise credential_exception
    
    return { "username": username, "role": role }

@app.get("/protected")
def protected_route(current_user: dict = Depends(get_the_current_user)):
    return { "message": f"Hello, {current_user['username']} | you access the protected Route" }


def require_role(allowed_roles: list[str]):
    def role_checker(current_user: dict = Depends(get_the_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permission")
        
        return current_user
    return role_checker

@app.get("/profile")
def profile(current_user: dict = Depends(require_role(["user", "admin"]))):
    return { "message": f"profile of {current_user['username']} ({current_user['role']})" }

@app.get('/user/dashboard')
def user_dashboard(current_user: dict = Depends(require_role(['user']))):
    return { "Message": "Welcome User" }

@app.get('/admin/dashboard')
def admin_dashboard(current_user: dict = Depends(require_role(['admin']))):
    return { "Messages": 'Welcome Admin' }