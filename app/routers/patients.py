import os
import uuid
import mimetypes
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from typing import List
from dotenv import load_dotenv
from .. import models, schemas, auth
from ..database import get_db
from ..cloud_storage import encrypt_file, decrypt_file, upload_to_cloud, download_and_decrypt

load_dotenv()
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")
LOCAL_UPLOAD_DIR = os.getenv("LOCAL_UPLOAD_DIR", "uploads")
BUCKET_NAME = os.getenv("BUCKET_NAME", "dummy_bucket")

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
    
    #Generate file name and read file 
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    file_content=await file.read()
    print("File size:", len(file_content))

    encrypted_content = encrypt_file(file_content)

    # Local / Cloud switch
    if ENVIRONMENT == "local":
        os.makedirs(LOCAL_UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(LOCAL_UPLOAD_DIR, unique_filename)
        
        with open (file_path, "wb") as f:
            f.write(encrypted_content)

        file_url = file_path
    
    else:
        file_path = None
        file_url = cloud_storage.upload_to_cloud(
            encrypted_content,
            unique_filename,
            BUCKET_NAME
        )
    
    # Save to database
    db_radiograph = models.Radiograph(
        user_id=current_user.id,
        filename=unique_filename,
        original_filename=file.filename,
        file_path=file_path,
        file_size=len(encrypted_content),
        description=description
    )
    db.add(db_radiograph)
    db.commit()
    db.refresh(db_radiograph)
    
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
    
    mime_type, _ = mimetypes.guess_type(radiograph.original_filename)
    if not mime_type:
        mime_type = "application/octet-stream"

    if ENVIRONMENT == "local" and radiograph.file_path:
        with open(radiograph.file_path, "rb") as f:
            encrypted_data = f.read()

        decrypted_bytes = decrypt_file(encrypted_data)

        return Response(decrypted_bytes, media_type=mime_type)

    decrypted_bytes = download_and_decrypt(
        radiograph.filename,
        BUCKET_NAME
    )

    return Response(decrypted_bytes, media_type=mime_type)