import os
import psycopg2
import dotenv

dotenv.load_dotenv()
dbname, user, password, host = os.getenv("DATABASE_NAME"), os.getenv("DATABASE_USERNAME"), os.getenv(
    "DATABASE_PASSWORD"), os.getenv("DATABASE_HOST")


def create_database():
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
    conn.autocommit = True
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE my_database;")

    cursor.close()
    conn.close()
    

def create_tables():
    conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES users(id),
            course_title VARCHAR(255) NOT NULL,
            course_description TEXT NOT NULL,
            ai_summary TEXT,
            status VARCHAR(50) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT NOW()
        );
    ''')

    conn.commit()
    cursor.close()
    conn.close()


def db_setup():
    try:
        create_database()
    except psycopg2.errors.DuplicateDatabase:
        pass
    create_tables()

