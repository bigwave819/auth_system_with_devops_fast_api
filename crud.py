from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

books = [
    {
        'id': 1,
        'title': 'The Hitchhiker\'s Guide to the Galaxy',
        'author': 'Douglas Adams',
        'publish_date': '1979-10-12'
    },
    {
        'id': 2,
        'title': 'Dune',
        'author': 'Frank Herbert',
        'publish_date': '1965-08-01'
    },
    {
        'id': 3,
        'title': '1984',
        'author': 'George Orwell',
        'publish_date': '1949-06-08'
    }
]


app = FastAPI()

@app.get("/books")
def get_all_books():
    return books

@app.get("/book/{id}")
def get_single_specific_book(id: int):
    for book in books:
        if book['id'] == id:
            return book
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book Not found")


class Book(BaseModel):
    id: int
    title: str
    author: str
    publish_date: str


@app.post("/books")
def create_book(book: Book):
    new_book = book.model_dump()
    books.append(new_book)


class BookUpdate(BaseModel):
    title: str
    author: str
    publish_date: str

@app.put('/book/{id}')
def update_book(id: int, book_update: BookUpdate):
    for book in books:
        if book["id"] == id :
            book['title'] = book_update.title
            book["author"] = book_update.author
            book["publish_date"] = book_update.publish_date

            return book


    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book Not found")


@app.delete('/book/{id}')
def delete_book(id: int):
    for i, book in enumerate(books):
        if book["id"] == id:
            deleted_book = books.pop(i)
            return {"message": "Book deleted successfully", "deleted_book": deleted_book}
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book Not found")