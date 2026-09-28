import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    role = Column(String(60), default="Drilling Engineer", nullable=False)
    asset_field = Column(String(80), default="Assam Shelf", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "asset_field": self.asset_field,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
