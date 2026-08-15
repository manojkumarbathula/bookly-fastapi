from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello-World"}

@app.get("/greet/{name}")
async def greet(name: str) -> dict:
    return {"message": f"Hello, {name}!"}

@app.get("/great/{name}")
async def greet(name: str,age:int) -> dict:
    return {"message": f"Hii {name}!","age": age}


class BookCreateModel(BaseModel):
    title: str
    author: str
@app.post("/create_book")
async def create_book(book: BookCreateModel):
    return{
        'title': book.title,
        'author': book.author
    }
