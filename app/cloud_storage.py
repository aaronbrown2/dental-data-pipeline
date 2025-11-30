from google.cloud import storage
import uuid

def upload_to_cloud(file_content, filename, bucket_name):
    """Upload file to Google Cloud Storage"""
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    # Create unique filename
    blob_name = f"{uuid.uuid4()}_{filename}"
    blob = bucket.blob(blob_name)

    # Upload the file
    blob.upload_from_string(file_content)

    # Make it publicly readable
    blob.make_public()

    return blob.public_url