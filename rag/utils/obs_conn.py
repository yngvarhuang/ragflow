#
#  Copyright 2025 The InfiniFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
from common.decorator import singleton
from rag import settings
import boto3
from botocore.exceptions import ClientError
import time
from io import BytesIO


@singleton
class RAGFlowOBS:
    def __init__(self):
        self.conn = None
        # Guard against missing configuration
        self.obs_config = settings.OBS or {}
        self.access_key = self.obs_config.get('access_key', None)
        self.secret_key = self.obs_config.get('secret_key', None)
        self.region = self.obs_config.get('region', None)
        self.endpoint_url = self.obs_config.get('endpoint_url', None)
        self.bucket = self.obs_config.get('bucket', None)
        self.prefix_path = self.obs_config.get('prefix_path', None)
        self.__open__()

    @staticmethod
    def use_default_bucket(method):
        def wrapper(self, bucket, *args, **kwargs):
            actual_bucket = self.bucket if self.bucket else bucket
            return method(self, actual_bucket, *args, **kwargs)
        return wrapper

    @staticmethod
    def use_prefix_path(method):
        def wrapper(self, bucket, fnm, *args, **kwargs):
            if self.prefix_path:
                fnm = f"{self.prefix_path}/{fnm}"
            return method(self, bucket, fnm, *args, **kwargs)
        return wrapper

    def __open__(self):
        try:
            if self.conn:
                self.__close__()
        except Exception:
            pass

        try:
            params = {}
            # Credentials: if not provided, boto3 will use default provider chain
            if self.access_key and self.secret_key:
                params['aws_access_key_id'] = self.access_key
                params['aws_secret_access_key'] = self.secret_key
            if self.region:
                params['region_name'] = self.region
            if self.endpoint_url:
                params['endpoint_url'] = self.endpoint_url

            self.conn = boto3.client('s3', **params)
        except Exception:
            logging.exception(f"Fail to connect OBS at region {self.region} endpoint {self.endpoint_url}")

    def __close__(self):
        try:
            if self.conn is not None:
                del self.conn
        finally:
            self.conn = None

    def _ensure_conn(self):
        if self.conn is None:
            self.__open__()
        return self.conn is not None

    @use_default_bucket
    def bucket_exists(self, bucket):
        if not self._ensure_conn():
            return False
        conn = self.conn
        if conn is None:
            return False
        try:
            conn.head_bucket(Bucket=bucket)
            return True
        except ClientError:
            logging.exception(f"head_bucket error {bucket}")
            return False

    def health(self):
        if not self._ensure_conn():
            return None
        bucket = self.bucket
        fnm = "txtxtxtxt1"
        fnm, binary = (f"{self.prefix_path}/{fnm}" if self.prefix_path else fnm), b"_t@@@1"
        conn = self.conn
        if conn is None:
            return None
        if not self.bucket_exists(bucket):
            conn.create_bucket(Bucket=bucket)
            logging.debug(f"create bucket {bucket} ********")

        r = conn.upload_fileobj(BytesIO(binary), bucket, fnm)
        return r

    def get_properties(self, bucket, key):
        return {}

    def list(self, bucket, dir, recursive=True):
        return []

    @use_prefix_path
    @use_default_bucket
    def put(self, bucket, fnm, binary, *args, **kwargs):
        if not self._ensure_conn():
            return None
        conn = self.conn
        if conn is None:
            return None
        logging.debug(f"put bucket name {bucket}; filename :{fnm}:")
        for _ in range(1):
            try:
                if not self.bucket_exists(bucket):
                    conn.create_bucket(Bucket=bucket)
                r = conn.upload_fileobj(BytesIO(binary), bucket, fnm)
                return r
            except Exception:
                logging.exception(f"Fail put {bucket}/{fnm}")
                self.__open__()
                time.sleep(1)

    @use_prefix_path
    @use_default_bucket
    def rm(self, bucket, fnm, *args, **kwargs):
        if not self._ensure_conn():
            return None
        conn = self.conn
        if conn is None:
            return None
        try:
            conn.delete_object(Bucket=bucket, Key=fnm)
        except Exception:
            logging.exception(f"Fail rm {bucket}/{fnm}")

    @use_prefix_path
    @use_default_bucket
    def get(self, bucket, fnm, *args, **kwargs):
        if not self._ensure_conn():
            return None
        conn = self.conn
        if conn is None:
            return None
        for _ in range(1):
            try:
                r = conn.get_object(Bucket=bucket, Key=fnm)
                object_data = r['Body'].read()
                return object_data
            except Exception:
                logging.exception(f"fail get {bucket}/{fnm}")
                self.__open__()
                time.sleep(1)
        return

    @use_prefix_path
    @use_default_bucket
    def obj_exist(self, bucket, fnm, *args, **kwargs):
        if not self._ensure_conn():
            return False
        conn = self.conn
        if conn is None:
            return False
        try:
            if conn.head_object(Bucket=bucket, Key=fnm):
                return True
        except ClientError as e:
            if e.response.get('Error', {}).get('Code') == '404':
                return False
            else:
                raise

    @use_prefix_path
    @use_default_bucket
    def get_presigned_url(self, bucket, fnm, expires, *args, **kwargs):
        if not self._ensure_conn():
            return None
        conn = self.conn
        if conn is None:
            return None
        for _ in range(10):
            try:
                r = conn.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket, 'Key': fnm},
                    ExpiresIn=expires,
                )
                return r
            except Exception:
                logging.exception(f"fail get url {bucket}/{fnm}")
                self.__open__()
                time.sleep(1)
        return

    @use_default_bucket
    def move(self, src_bucket, src_path, dest_bucket, dest_path, *args, **kwargs):
        if not self._ensure_conn():
            return False
        conn = self.conn
        if conn is None:
            return False
        try:
            conn.copy_object(
                Bucket=dest_bucket,
                Key=dest_path,
                CopySource={'Bucket': src_bucket, 'Key': src_path},
            )
            conn.delete_object(Bucket=src_bucket, Key=src_path)
            return True
        except Exception as e:
            logging.exception(f"Fail to move {src_bucket}/{src_path} -> {dest_bucket}/{dest_path}: {e}")
            return False