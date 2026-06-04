from app.core.database import SessionLocal, engine
from app.core.security import get_password_hash
from app.models.user import User

User.__table__.create(bind=engine, checkfirst=True)

db = SessionLocal()
try:
    email = "admin@example.com"
    user = db.query(User).filter(User.email == email).first()
    if user:
        print(f"exists {user.id} {user.email} admin={user.is_admin}")
    else:
        user = User(
            email=email,
            hashed_password=get_password_hash("AdminPass123!"),
            full_name="Admin User",
            is_admin=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"created {user.id} {user.email} admin={user.is_admin}")
finally:
    db.close()
