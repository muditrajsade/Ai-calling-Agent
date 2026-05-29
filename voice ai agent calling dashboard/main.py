import boto3
from fastapi import FastAPI, File, UploadFile, HTTPException
import os
from dotenv import load_dotenv
import openpyxl
import pandas as pd
import json
load_dotenv()
AWS_ACCESS_ID = os.getenv("AWS_ACCESS_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
app = FastAPI()
#S3_BUCKET = "excelsheetbucketmuditrajsade"
queueurl = "https://sqs.ap-south-1.amazonaws.com/633665344245/numbersqueue"
S3_REGION = "ap-south-1"

sqs = boto3.client(
    "sqs",
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
        file = pd.read_excel(file.file)
        first_column = file['Phone'].tolist()
        for num in first_column:
            print(num)
            sqs.send_message(QueueUrl=queueurl, MessageBody=json.dumps({"numbers": str(num)}))
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
