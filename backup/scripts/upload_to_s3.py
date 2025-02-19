#!/usr/bin/env python3
import os
import sys
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

def upload_to_s3(file_path, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_path: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    if object_name is None:
        object_name = os.path.basename(file_path)

    # Create a timestamp-based folder structure
    date_prefix = datetime.now().strftime('%Y/%m/%d/')
    object_name = f"{date_prefix}{object_name}"

    s3_client = boto3.client('s3')
    try:
        print(f"Uploading {file_path} to {bucket}/{object_name}")
        s3_client.upload_file(file_path, bucket, object_name)
        print(f"Successfully uploaded {object_name}")
        return True
    except ClientError as e:
        print(f"Error uploading {file_path}: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: upload_to_s3.py file1 [file2 ...]")
        sys.exit(1)

    bucket = os.environ.get('BACKUP_BUCKET_NAME')
    if not bucket:
        print("Error: BACKUP_BUCKET_NAME environment variable not set")
        sys.exit(1)

    success = True
    for file_path in sys.argv[1:]:
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist")
            success = False
            continue

        if not upload_to_s3(file_path, bucket):
            success = False

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main() 