from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import psycopg

ROOT_PATH=os.getenv("ROOT_PATH", "")

DB_NAME = os.getenv("POSTGRES_DB", "dev_db")
DB_USER = os.getenv("POSTGRES_USER", "dev_user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "dev_password")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")

status = {"db": "❌ db not initialized"}


origins = [
    "http://localhost:3000",
    "https://air.anselbrandt.net",
    "https://cdn.anselbrandt.ca",
    "https://fastapiservices.vercel.app"
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with psycopg.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        ) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username TEXT NOT NULL UNIQUE,
                        email TEXT NOT NULL UNIQUE,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
        status["db"] = "✅ 'users' table created or already exists."
    except Exception as e:
        status["db"] = f"❌ DB init failed: {e}"

    yield


app = FastAPI(root_path=ROOT_PATH, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Item(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float = 10.5
    tags: list[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {"name": "Bar", "description": "The bartenders", "price": 62, "tax": 20.2},
    "baz": {"name": "Baz", "description": None, "price": 50.2, "tax": 10.5, "tags": []},
}


@app.get("/")
async def root():
    return {"message": "Hello World", "status": status}


@app.get("/health")
async def health():
    return {"status": status}


@app.get("/items", response_model=dict[str, Item])
async def all_items():
    return items


@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: str):
    return items[item_id]


@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    update_item_encoded = jsonable_encoder(item)
    items[item_id] = update_item_encoded
    return update_item_encoded
