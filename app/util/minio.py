"""minio와 관련된 함수들 모음.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
from array import array
from datetime import datetime

import boto3
import zstd
from core.config import setting


def connect_minio_resource() -> boto3.resource:
    """boto3 resource 객체를 리턴받는 함수.

    Returns:
        boto3.resource
    """
    clientargs_keys = (
        "endpoint_url",
        "aws_access_key_id",
        "aws_secret_access_key",
        "verify",
        # "region_name",
    )

    clientargs = {}
    for args in clientargs_keys:
        clientargs[args] = getattr(setting, args)

    s3 = boto3.resource("s3", **clientargs)
    return s3


def connect_minio_client() -> boto3.client:
    """Minio client 객체를 리턴받는 함수.

    Returns:
        boto3.client
    """
    clientargs_keys = (
        "endpoint_url",
        "aws_access_key_id",
        "aws_secret_access_key",
        "verify",
        # "region_name",
    )

    clientargs = {}
    for args in clientargs_keys:
        clientargs[args] = getattr(setting, args)

    s3 = boto3.client("s3", **clientargs)
    return s3


def get_zstd_object(key: str) -> list[float]:
    """Minio key를 이용하여 float list 형태로 변환.

    Args:
        key (str): zstd 압축방식으로 압축한 객체의 키
    Returns:
        List[float]
    """
    s3 = connect_minio_client()
    obj = s3.get_object(Bucket=setting.bucket_name, Key=key)
    zstd_data = obj["Body"].read()
    bytes_data = zstd.decompress(zstd_data)
    return list(array("f", bytes_data))


def zstd_compress(data_list: list, level: int = 22) -> bytes:
    """List 형태의 데이터를 zstd 압축된 데이터로 리턴하는 함수.

    Args:
        data_list (list): list 형태의 데이터이며, 주로 float list를 다룸.
        level (int): 압축 레벨, 3~22의 범위를 가지며 22가 압축률이 가장 높음.


    Returns:
        bytes
    """
    if not isinstance(data_list, bytes):
        bytes_data = array("f", data_list).tobytes()  # Convert array to bytes
    compressed_data = zstd.compress(bytes_data, level)
    return compressed_data


def generate_minio_key(
    line_id: int,
    equipment_id: int,
    motor_number: int,
    acq_time: datetime,
    phase: str,
) -> str:
    """Minio key를 생성하는 함수.

    Args:
        line_id (int): Line 테이블의 id를 의미
        equipment_id (int): equipment 테이블의 id를 의미
        motor_number (int): 모터 번호
        acq_time (datetime): 계측된 시간
        phase (str): 전류일 경우 uvw, 진동의 경우 uvw 이외의 값들이 채워짐.


    Returns:
        str
    """
    year = acq_time.year
    month = acq_time.month
    day = acq_time.day
    hour = acq_time.hour
    minute = acq_time.minute
    second = acq_time.second
    key = f"/{line_id}/{equipment_id}/{motor_number}/{year}/{month}/{day}/{hour}:{minute}:{second}_{phase}.zst"  # noqa: E501
    return key
