
from auth import *
from database import SessionLocal, engine, Base
from models import User
from sqlalchemy.orm import Session
from passlib.context import CryptContext
# main.py
from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)


oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...),
                db: Session = Depends(get_db)):
    #user = authenticate_user(db,username, password)
    user = db.query(User).filter(User.email == username).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Benutzer oder Passwort falsch"})
    # 2. Token erzeugen und ins Cookie schreiben
    token = create_access_token({"sub": user.firstname, "role": user.role})
    resp = RedirectResponse(url="/home", status_code=status.HTTP_303_SEE_OTHER)
    resp.set_cookie("access_token", f"Bearer {token}", httponly=True)

    return resp

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register(request: Request,
             firstname: str = Form(...),
             lastname: str = Form(...),
             email: str = Form(...),
             company: str | None = Form(None),
             phone: str | None = Form(None),
             password1: str = Form(...),
             password2: str = Form(...),
             db: Session = Depends(get_db)):
    if password1 != password2:
        return templates.TemplateResponse("register.html",
             {"request": request, "error": "Passwörter stimmen nicht überein"})
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse("register.html",
            {"request": request, "error": "E-Mail existiert bereits"})
    user = User(firstname=firstname, lastname=lastname, email=email,
                company=company, phone=phone,
                hashed_password=pwd_context.hash(password1))
    db.add(user)
    db.commit()
    
    # Willkommensnachricht vorbereiten
    msg = f"Herzlich willkommen, {firstname} {lastname}! Ihre Registrierung war erfolgreich."
    
    return RedirectResponse(
        url=f"/erfolg?firstname={firstname}&lastname={lastname}",
        status_code=status.HTTP_303_SEE_OTHER
    )
    #return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/home", response_class=HTMLResponse)
def home(request: Request, user=Depends(get_current_user)):
    return templates.TemplateResponse("home.html", {"request": request, "user": user})

@app.get("/logout")
def logout():
    resp = RedirectResponse("/", status_code=302)
    resp.delete_cookie("access_token")
    return resp

@app.get("/erfolg", response_class=HTMLResponse)
async def erfolg(request: Request, firstname: str, lastname: str):
    return templates.TemplateResponse("erfolg.html", {
        "request": request,
        "firstname": firstname,
        "lastname": lastname
    })
