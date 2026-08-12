from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database.database import engine
from app.models.user import User
from app.routes.auth import router as auth_router
from app.core.dependencies import get_current_user
from fastapi import Depends

app = FastAPI(
    title="Employee Leave Management System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "message": "Employee Leave Management Backend is running"
    }


@app.get("/db-test")
def database_test():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "message": "MySQL database connected successfully"
        }

    except Exception as error:
        return {
            "message": "Database connection failed",
            "error": str(error)
        }


@app.get("/users")
def get_users():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text(
                    "SELECT id, name, email, role, created_date "
                    "FROM users"
                )
            )

            users = [
                dict(row._mapping)
                for row in result
            ]

        return {
            "users": users
        }

    except Exception as error:
        return {
            "message": "Failed to retrieve users",
            "error": str(error)
        }


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }

@app.get("/api/auth/me")
def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    return {
        "message": "Authentication successful",
        "user": current_user
    }