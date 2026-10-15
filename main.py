from fastapi import FastAPI, Request, Form, RedirectResponse
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SQLALCHEMY_DATABASE_URL = "sqlite:///./pet.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Pet(Base):
    __tablename__ = "pets"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String)
    age = Column(Integer)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    db = next(get_db())
    pets = db.query(Pet).all()
    return templates.TemplateResponse("index.html", {"request": request, "pets": pets})

@app.post("/add")
async def add_pet(name: str = Form(...), type: str = Form(...), age: int = Form(...)):
    db = next(get_db())
    pet = Pet(name=name, type=type, age=age)
    db.add(pet)
    db.commit()
    return RedirectResponse("/", status_code=303)

@app.get("/edit/{pet_id}", response_class=HTMLResponse)
async def edit(request: Request, pet_id: int):
    db = next(get_db())
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    return templates.TemplateResponse("edit.html", {"request": request, "pet": pet})

@app.post("/update/{pet_id}")
async def update(pet_id: int, name: str = Form(...), type: str = Form(...), age: int = Form(...)):
    db = next(get_db())
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    pet.name = name
    pet.type = type
    pet.age = age
    db.commit()
    return RedirectResponse("/", status_code=303)

@app.get("/delete/{pet_id}")
async def delete(pet_id: int):
    db = next(get_db())
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    db.delete(pet)
    db.commit()
    return RedirectResponse("/", status_code=303)
