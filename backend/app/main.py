from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database.database import engine, Base
from app.database import seed
from app.models import User, Leave, LeaveBalance, EmployeeProfile
from app.routes.auth import router as auth_router
from app.routes.leaves import router as leaves_router
from app.routes.leaves_crud import router as leaves_crud_router
from app.routes.dashboard import router as dashboard_router
from app.routes.users import router as users_router
from app.routes.admin import router as admin_router
from app.routes.profile import router as profile_router
from app.core.dependencies import get_current_user


app = FastAPI(
    title="Employee Leave Management System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed.seed_database()


app.include_router(auth_router)
app.include_router(leaves_router)
app.include_router(leaves_crud_router)
app.include_router(dashboard_router)
app.include_router(users_router)
app.include_router(admin_router)
app.include_router(profile_router)


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
