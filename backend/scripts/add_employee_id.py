"""Add employee_id column to leaves table if missing (development helper).
Run with: python scripts/add_employee_id.py
"""
from sqlalchemy import text
from app.database.database import engine

with engine.connect() as conn:
    res = conn.execute(text("SHOW COLUMNS FROM leaves LIKE 'employee_id'"))
    row = res.fetchone()

    if row:
        print("Column 'employee_id' already exists on 'leaves'.")
    else:
        print("Adding 'employee_id' column to 'leaves' table...")
        conn.execute(text("ALTER TABLE leaves ADD COLUMN employee_id INT NULL AFTER user_id"))
        print("Done.")
