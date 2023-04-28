"""minio locust 부하 테스트 엔드포인트.

legacy이며, ESWA 구축 과정 당시에,
Window Server minio가 자주 다운되어 부하 테스트를 하기 위해 생성한 임시 API.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""


import random
from array import array
from datetime import datetime
from typing import List, Union

import boto3
import zstd
from botocore.client import Config
from fastapi import APIRouter, status

router = APIRouter()


@router.post("/insert-minio", status_code=status.HTTP_201_CREATED)
async def insert_minio(body: dict):
    """
    fdc feature를 읽어오는 api, deprecated
    """

    endpoint_url = "http://10.10.30.23:9000"
    aws_access_key_id = "guardione"
    aws_secret_access_key = "onepredict1!"
    bucket_name = "test"

    # arr = random.sample(range(160000), 160000)
    # data = bytes(array("f", arr))
    # compressed_data = zstd.compress(data, 22)

    s3 = boto3.resource(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        config=Config(signature_version="s3v4"),
        verify=False,
        region_name="ap-northeast-2",
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    data = bytes(array("f", body["data"]))
    compressed_data = zstd.compress(data, 22)

    s3.Object(bucket_name, "".join((now, ".zst"))).put(Body=compressed_data)
