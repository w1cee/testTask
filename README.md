## Setup Instructions

### 1. Clone the repository

First, clone the repository to your local machine:

```bash
git clone https://github.com/w1cee/testTask.git
cd testTask
```

### 2. Install dependencies

Create a virtual environment and install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

### 3. Run the FastAPI server

To start the FastAPI server in development mode, run the following command:

```bash
fastapi dev api.py
```

This will start the server on `http://127.0.0.1:8000`.

### 4. Access the API documentation

Once the server is running, you can access the auto-generated API documentation at:

```
http://127.0.0.1:8000/docs
```

This documentation provides an interactive interface to test and explore the available endpoints.

### 5. Environment Variables

Ensure you have the following environment variables set in your `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key for generating summaries.
- `DATABASE_NAME`: The name of your PostgreSQL database.
- `DATABASE_USERNAME`: The username for your PostgreSQL database.
- `DATABASE_PASSWORD`: The password for your PostgreSQL database.
- `DATABASE_HOST`: The host of your PostgreSQL database.
- `API_KEY`: The API key for authentication.

## Endpoints

- `POST /users`: Create a new user.
- `GET /users/{user_id}`: Fetch user details by user ID.
- `POST /courses`: Submit a new course.
- `POST /generate_summary`: Generate a summary of a course description using OpenAI's GPT.
- `POST /edit_summary`: Edit the summary of a course.
