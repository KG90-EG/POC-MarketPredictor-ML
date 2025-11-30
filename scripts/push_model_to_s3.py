#!/usr/bin/env python3
import argparse
import boto3
import os

def upload_file(file_path, bucket, key):
    s3 = boto3.client('s3')
    s3.upload_file(file_path, bucket, key)
    print(f'Uploaded {file_path} to s3://{bucket}/{key}')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True)
    parser.add_argument('--bucket', required=True)
    parser.add_argument('--key', default=None)
    args = parser.parse_args()
    key = args.key or os.path.basename(args.file)
    upload_file(args.file, args.bucket, key)

if __name__ == '__main__':
    main()
