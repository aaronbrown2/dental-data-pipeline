import os
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from . import auth, models


def _enabled(value: str | None) -> bool:
    return value and value.lower() in {"1", "true", "yes", "on"}


def seed_demo_data(db: Session) -> None:
    if not _enabled(os.getenv("SEED_DEMO_DATA")):
        return

    email = os.getenv("DEMO_EMAIL", "demo@dental-records.dev")
    password = os.getenv("DEMO_PASSWORD", "DemoPassword123!")

    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        user = models.User(
            email=email,
            hashed_password=auth.get_password_hash(password),
            first_name="Demo",
            last_name="Patient",
            phone="(555) 010-0198",
        )
        db.add(user)
        db.flush()
    else:
        user.hashed_password = auth.get_password_hash(password)
        user.first_name = "Demo"
        user.last_name = "Patient"
        user.phone = "(555) 010-0198"
        user.is_active = True

    profile = db.query(models.PatientProfile).filter(
        models.PatientProfile.user_id == user.id
    ).first()
    profile_data = {
        "last_dental_visit": "2026-03-15",
        "dental_concerns": "Sensitivity near upper molars and interest in whitening options.",
        "current_medications": "None",
        "allergies": "Penicillin",
        "dental_history": "Routine cleanings, one composite filling in 2024.",
        "pain_level": 2,
        "insurance_provider": "Demo Dental PPO",
        "emergency_contact_name": "Jordan Patient",
        "emergency_contact_phone": "(555) 010-0204",
    }
    if profile:
        for key, value in profile_data.items():
            setattr(profile, key, value)
    else:
        db.add(models.PatientProfile(user_id=user.id, **profile_data))

    db.query(models.Appointment).filter(models.Appointment.user_id == user.id).delete()
    now = datetime.now()
    db.add_all(
        [
            models.Appointment(
                user_id=user.id,
                appointment_date=now + timedelta(days=14),
                appointment_type="cleaning",
                notes="Six-month preventive cleaning and exam.",
            ),
            models.Appointment(
                user_id=user.id,
                appointment_date=now + timedelta(days=45),
                appointment_type="consultation",
                notes="Review sensitivity and radiograph findings.",
            ),
        ]
    )

    db.commit()


def is_demo_login(email: str) -> bool:
    return (
        _enabled(os.getenv("SEED_DEMO_DATA"))
        and email.lower() == os.getenv("DEMO_EMAIL", "demo@dental-records.dev").lower()
    )
