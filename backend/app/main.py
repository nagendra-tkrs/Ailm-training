import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
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

logger = logging.getLogger("app")

app = FastAPI(
    title="Employee Leave Management System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        loc = " -> ".join(str(l) for l in error["loc"])
        errors.append({"field": loc, "message": error["msg"]})

    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        errors,
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": errors,
        },
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    logger.error(
        "Database error on %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred"},
    )


@app.exception_handler(Exception)
async def generic_error_handler(request: Request, exc: Exception):
    logger.error(
        "Unhandled error on %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"},
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

    except Exception:
        logger.error("Database connection test failed", exc_info=True)
        return JSONResponse(
            status_code=503,
            content={"message": "Database connection failed"},
        )


@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }
