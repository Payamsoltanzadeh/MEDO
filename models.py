import os
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, ForeignKey, Boolean,
    DateTime, Text, create_engine
)
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Optional: If you want to load .env files locally
# (On Railway, environment variables come from the project's settings.)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

Base = declarative_base()

# 1) Get DATABASE_URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")


if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

# 3) Create the engine and session factory
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

# ------------------
# Model definitions
# ------------------

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(50), nullable=False)

    appointments = relationship("Appointment", back_populates="user")
    certificates = relationship("HealthCertificate", back_populates="user")

class Specialization(Base):
    __tablename__ = 'specializations'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)

    # No cascade:
    doctors = relationship("Doctor", back_populates="specialization")


class Doctor(Base):
    __tablename__ = 'doctors'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    specialization_id = Column(Integer, ForeignKey('specializations.id'), nullable=False)
    in_person_available = Column(Boolean, default=True)
    online_available = Column(Boolean, default=True)

    specialization = relationship("Specialization", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")


class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id'), nullable=False)
    appointment_type = Column(String(100), nullable=False)
    contact_method = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default='pending')  # pending, confirmed, rejected, canceled
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")


class HealthCertificate(Base):
    __tablename__ = 'health_certificates'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reason = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default='pending')  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="certificates")


def init_db():
    """
    Creates all tables in the database (if they do not already exist).
    """
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
