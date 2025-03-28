import os
from fastapi import FastAPI, Depends, Request
import psycopg2
from contextlib import contextmanager
from datetime import datetime as dt
from openai import OpenAI
import dotenv
import auth
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from database import db_setup

dotenv.load_dotenv()

db_setup()

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(dependencies=[Depends(auth.validate_api_key)])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

dbname, user, password, host = os.getenv("DATABASE_NAME"), os.getenv("DATABASE_USERNAME"), os.getenv(
    "DATABASE_PASSWORD"), os.getenv("DATABASE_HOST")


@contextmanager
def get_db():
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
    cur = conn.cursor()
    try:
        yield cur, conn
    finally:
        cur.close()
        conn.close()


@app.post("/users", status_code=201)
async def create_new_user(name: str, email: str):
    with get_db() as (cur, conn):
        try:
            cur.execute("INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id", (name, email))
            user_id = cur.fetchone()[0]
            conn.commit()
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            return {"message": "User already exists"}

    return {"message": "User created successfully", "user_id": user_id}


@app.get("/users/{user_id}", status_code=200)
async def fetch_user_details(user_id: int):
    with get_db() as (cur, conn):
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cur.fetchone()

    return {"user": user} if user else {"message": "User not found"}


@app.post("/courses", status_code=201)
async def submit_course(user_id: int, course_title: str, course_description: str):
    created_at = dt.now()
    status = "pending"
    with get_db() as (cur, conn):
        try:
            cur.execute(
                "INSERT INTO courses (user_id, course_title, course_description, status, created_at) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (user_id, course_title, course_description, status, created_at))
            course_id = cur.fetchone()[0]
            conn.commit()
        except psycopg2.errors.ForeignKeyViolation:
            conn.rollback()
            return {"message": "User not found"}

    return {"message": "Course created successfully", "course_id": course_id}


@app.post("/generate_summary", status_code=200)
@limiter.limit("3/hour")
async def generate_summary(request: Request, course_id: int):
    with get_db() as (cur, conn):
        cur.execute("SELECT course_description FROM courses WHERE id = %s", (course_id,))
        course_description = cur.fetchone()

        if course_description is None:
            return {"message": "Course not found"}

        course_description = course_description[0]

        prompt = f"Please generate a concise summary of the following course description: {course_description}"

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            store=False,
            messages=[{"role": "user", "content": prompt}]
        )

        generated_summary = completion.choices[0].message.content

        return {"generated_summary": generated_summary, "course_id": course_id}


@app.post("/edit_summary", status_code=200)
async def edit_summary(course_id: int, edited_summary: str):
    with get_db() as (cur, conn):
        cur.execute(
            "UPDATE courses SET ai_summary = %s, status = %s WHERE id = %s",
            (edited_summary, "completed", course_id)
        )
        conn.commit()

        if cur.rowcount == 0:
            return {"message": "Course not found"}

    return {"message": "Summary successfully updated"}
