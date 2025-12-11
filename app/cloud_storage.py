from google.cloud import storage
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import os
import uuid

load_dotenv()

def get_fernet():
    key = os.environ.get("ENCRYPTION_KEY")
    if not key: 
        raise ValueError("ENCRYPTION_KEY is not set in environment variables.")
    return Fernet(key)

def encrypt_file(content: bytes) -> bytes:
    f = get_fernet()
    return f.encrypt(content)

def decrypt_file(content: bytes) -> bytes:
    f = get_fernet()
    return f.decrypt(content)

def upload_to_cloud(encrypted_content: bytes, unique_filename: str, bucket_name: str):
    """Upload encrypted file to Google Cloud Storage"""

    # Open Bucket
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Create blob
    blob = bucket.blob(unique_filename)

    # Upload the file
    blob.upload_from_string(encrypted_content)

    return blob.name

def download_and_decrypt(blob_name: str, bucket_name: str) -> bytes:
    """Download encrypted file and decrypt it"""
    f = get_fernet()

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    encrypted_data = blob.download_as_bytes()

    return f.decrypt(encrypted_data)