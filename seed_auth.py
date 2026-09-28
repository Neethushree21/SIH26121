import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "backend"))

from app.core.database import init_db, SessionLocal
from app.models.user import User
from app.core.security import hash_password

init_db()
db = SessionLocal()

demo_accounts = [
    {
        "email": "engineer@oilindia.in",
        "password": "OilIndia@2026",
        "full_name": "Er. Jyoti Saikia",
        "role": "Lead Drilling Engineer",
        "asset_field": "Nahorkatiya Field"
    },
    {
        "email": "superintendent@oilindia.in",
        "password": "OilIndia@2026",
        "full_name": "B. K. Goswami",
        "role": "Drilling Superintendent",
        "asset_field": "Assam Shelf Asset"
    },
    {
        "email": "geologist@oilindia.in",
        "password": "OilIndia@2026",
        "full_name": "Dr. Manash Borah",
        "role": "Chief Geologist",
        "asset_field": "Baghjan Asset"
    }
]

created = []
for acc in demo_accounts:
    existing = db.query(User).filter(User.email == acc["email"]).first()
    if not existing:
        user = User(
            email=acc["email"],
            hashed_password=hash_password(acc["password"]),
            full_name=acc["full_name"],
            role=acc["role"],
            asset_field=acc["asset_field"],
            is_active=True
        )
        db.add(user)
        created.append(acc["email"])

db.commit()

count = db.query(User).count()
print(f"[PASS] Users initialized. Total users in database: {count}")
for u in db.query(User).all():
    print(f" - {u.email} | {u.full_name} ({u.role})")

db.close()
