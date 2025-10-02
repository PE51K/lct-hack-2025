#!/usr/bin/env python3
"""Upload TESTDATA files to MinIO bucket."""

import sys
from pathlib import Path

import boto3
from tqdm import tqdm


def upload_testdata():
    """Upload all files from TESTDATA directory to MinIO."""
    endpoint_url = "http://localhost:9000"
    access_key = "test_minio"
    secret_key = "b27151ebd132e5c37325ee5bda0048aeda118d97493bd2b3f1da3aad09c17ca2"
    bucket_name = "test-bucket"

    s3_client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )

    testdata_dir = Path("TESTDATA")

    if not testdata_dir.exists():
        print(f"Error: {testdata_dir} directory not found")
        sys.exit(1)

    files = list(testdata_dir.rglob("*"))
    files = [f for f in files if f.is_file() and f.name != ".gitkeep"]

    print(f"Found {len(files)} files to upload")
    total_size = sum(f.stat().st_size for f in files)
    print(f"Total size: {total_size / (1024**3):.2f} GB")

    for file_path in tqdm(files, desc="Uploading", unit="file"):
        key = f"TESTDATA/{file_path.relative_to(testdata_dir)}"
        key = key.replace("\\", "/")

        file_size = file_path.stat().st_size
        file_size_mb = file_size / (1024**2)

        tqdm.write(f"Uploading {file_path.name} ({file_size_mb:.1f} MB)")

        try:
            s3_client.upload_file(
                str(file_path),
                bucket_name,
                key,
            )
        except Exception as e:
            tqdm.write(f"Error uploading {file_path.name}: {e}")
            continue

    print("\nUpload complete!")
    print(f"Files are available at: s3://{bucket_name}/TESTDATA/")


if __name__ == "__main__":
    upload_testdata()
