import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db
from ..cloud_storage import upload_to_cloud

router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("/profile", response_model=schemas.PatientProfileResponse)
def create_or_update_profile(
    profile: schemas.PatientProfileCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Check if profile exists
    db_profile = db.query(models.PatientProfile).filter(
        models.PatientProfile.user_id == current_user.id
    ).first()
    
    if db_profile:
        # Update existing profile
        for key, value in profile.dict(exclude_unset=True).items():
            setattr(db_profile, key, value)
    else:
        # Create new profile
        db_profile = models.PatientProfile(
            user_id=current_user.id,
            **profile.dict()
        )
        db.add(db_profile)
    
    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.get("/profile", response_model=schemas.PatientProfileResponse)
def get_profile(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(models.PatientProfile).filter(
        models.PatientProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    return profile

@router.post("/radiographs/upload")
async def upload_radiograph(
    file: UploadFile = File(...),
    description: str = None,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/tiff"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG, PNG, and TIFF files are allowed"
        )
    
    # Create upload directory if it doesn't exist
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    file_url = upload_to_cloud(
        file_content=await file.read(),
        filename=file.filename,
        bucket_name="dental-files-aaronbrown"
    )
    
    # Save to database
    db_radiograph = models.Radiograph(
        user_id=current_user.id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=len(file_content),
        description=description
    )
    db.add(db_radiograph)
    db.commit()
    
    return {"message": "File uploaded successfully", "filename": unique_filename}

@router.get("/radiographs", response_model=List[schemas.RadiographResponse])
def get_radiographs(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    radiographs = db.query(models.Radiograph).filter(
        models.Radiograph.user_id == current_user.id
    ).all()
    
    return radiographs

@router.get("/radiographs/{radiograph_id}")
def get_radiograph_file(
    radiograph_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    radiograph = db.query(models.Radiograph).filter(
        models.Radiograph.id == radiograph_id,
        models.Radiograph.user_id == current_user.id
    ).first()
    
    if not radiograph:
        raise HTTPException(status_code=404, detail="Radiograph not found")
    
    return FileResponse(
        path=radiograph.file_path,
        filename=radiograph.original_filename
    )