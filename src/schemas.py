from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    firstname: str
    lastname: str
    email: EmailStr
    company: str | None = None
    phone: str | None = None
    password1: str
