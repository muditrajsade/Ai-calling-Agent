import boto3
from fastapi import FastAPI, File, UploadFile, HTTPException
import os
from dotenv import load_dotenv

load_dotenv()
AWS_ACCESS_ID = os.getenv("AWS_ACCESS_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
app = FastAPI()
S3_BUCKET = "excelsheetbucketmuditrajsade"
S3_REGION = "ap-south-1"  # e.g. us-east-1

s3 = boto3.client(
    "s3",
    region_name=S3_REGION,
    aws_access_key_id=AWS_ACCESS_ID,
    aws_secret_access_key=AWS_SECRET_KEY,
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/upload_leads")
def upload(file: UploadFile = File(...)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only Excel files are allowed")
    try:
        s3.upload_fileobj(file.file, S3_BUCKET, file.filename)
        return {"message": f"{file.filename} uploaded to S3 bucket {S3_BUCKET}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
