import logging

from app.core.security import hash_password
from app.database.database import SessionLocal
from app.models.user import User
from app.models.leave_balance import create_default_balances
from app.models.employee_profile import EmployeeProfile
from app.services.user_service import generate_employee_id

logger = logging.getLogger("app.seed")


def seed_database():
    """Insert demo users if they do not exist yet."""
    db = SessionLocal()

    try:
        # Demo admin
        admin = (
            db.query(User)
            .filter(User.email == "admin@gmail.com")
            .first()
        )

        if admin is None:
            db.add(
                User(
                    name="System Admin",
                    email="admin@gmail.com",
                    password=hash_password("Admin@123"),
                    role="admin",
                    employee_id=generate_employee_id(db),
                )
            )
            db.commit()

            admin = (
                db.query(User)
                .filter(User.email == "admin@gmail.com")
                .first()
            )

            db.add(
                EmployeeProfile(
                    user_id=admin.id,
                    name=admin.name,
                    email=admin.email,
                    role=admin.role,
                )
            )
            db.commit()

        # Demo employee (with leave balances)
        employee = (
            db.query(User)
            .filter(User.email == "employee@gmail.com")
            .first()
        )

        if employee is None:
            db.add(
                User(
                    name="Employee One",
                    email="employee@gmail.com",
                    password=hash_password("Employee@123"),
                    role="employee",
                    employee_id=generate_employee_id(db),
                )
            )
            db.commit()

            employee = (
                db.query(User)
                .filter(User.email == "employee@gmail.com")
                .first()
            )

            create_default_balances(db, employee.id)

            db.add(
                EmployeeProfile(
                    user_id=employee.id,
                    name=employee.name,
                    email=employee.email,
                    role=employee.role,
                )
            )
            db.commit()

    except Exception:
        logger.error("Database seeding failed", exc_info=True)
        db.rollback()
    finally:
        db.close()
