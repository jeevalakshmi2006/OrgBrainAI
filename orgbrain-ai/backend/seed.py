"""
Run once after first setup: creates tables, an admin user, and two sample
employees across departments.

Usage: python seed.py
"""
from database import engine, Base, SessionLocal
import models
from auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

DEPARTMENTS = ["Software Development", "Software Testing", "IT Marketing"]

dept_objs = {}
for name in DEPARTMENTS:
    existing = db.query(models.Department).filter(models.Department.name == name).first()
    if not existing:
        existing = models.Department(name=name, description=f"{name} department")
        db.add(existing)
        db.commit()
        db.refresh(existing)
    dept_objs[name] = existing

USERS = [
    {"name": "Admin User", "email": "admin@orgbrain.ai", "password": "Admin@123", "role": "admin", "dept": None},
    {"name": "Arun Kumar", "email": "arun@orgbrain.ai", "password": "Arun@123", "role": "employee", "dept": "Software Development"},
    {"name": "Priya Sharma", "email": "priya@orgbrain.ai", "password": "Priya@123", "role": "employee", "dept": "Software Testing"},
]

for u in USERS:
    existing = db.query(models.User).filter(models.User.email == u["email"]).first()
    if not existing:
        dept_id = dept_objs[u["dept"]].id if u["dept"] else None
        user = models.User(
            name=u["name"], email=u["email"],
            hashed_password=hash_password(u["password"]),
            role=u["role"], department_id=dept_id,
        )
        db.add(user)

db.commit()
db.close()

print("Seed complete. Login with:")
for u in USERS:
    print(f"  {u['role']:<10} {u['email']:<25} password: {u['password']}")
