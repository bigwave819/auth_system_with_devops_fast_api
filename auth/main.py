from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .auth_database import get_db
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

SECRET_KEY = "bLXolj5Vlv-FFNFABHeEnQ15cu4L-qV80_kzSG3RzfI"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRATION_MINUTE = 30

# Create Token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRATION_MINUTE)
    to_encode.update({"exp": expire})   # FIXED
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

app = FastAPI()

# Signup
@app.post("/signup")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = utils.hash_password(user.password)

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # FIXED

    return {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "role": new_user.role
    }

# Login
@app.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Username")

    if not utils.verify_password(form_data.password, user.hashed_password):  # FIXED
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password")

    token_data = {"sub": user.username, "role": user.role}
    token = create_access_token(token_data)

    return {"access_token": token, "token_type": "bearer"}

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Get current user
def get_the_current_user(token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate the Credential",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # FIXED
        username: str = payload.get("sub")
        role: str = payload.get("role")

        if username is None or role is None:
            raise credential_exception

    except JWTError:
        raise credential_exception

    return {"username": username, "role": role}

# Protected route
@app.get("/protected")
def protected_route(current_user: dict = Depends(get_the_current_user)):
    return {"message": f"Hello, {current_user['username']}"}

# Role checker
def require_role(allowed_roles: list[str]):
    def role_checker(current_user: dict = Depends(get_the_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(status_code=403, detail="Not enough permission")
        return current_user
    return role_checker

# Routes
@app.get("/profile")
def profile(current_user: dict = Depends(require_role(["user", "admin"]))):
    return {"message": f"profile of {current_user['username']} ({current_user['role']})"}

@app.get("/user/dashboard")
def user_dashboard(current_user: dict = Depends(require_role(["user"]))):
    return {"message": "Welcome User"}

@app.get("/admin/dashboard")
def admin_dashboard(current_user: dict = Depends(require_role(["admin"]))):
    return {"message": "Welcome Admin"}