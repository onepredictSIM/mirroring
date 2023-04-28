"""Config for config server app.

- Author: Kibum Park
- Contact: kibum.park@onepredict.com
- Reference : https://www.coninggu.com/m/12.
"""


from pydantic import BaseSettings


class Setting(BaseSettings):
    """Setting Configuration.

    Attributes:
        servicedb_uri : 서비스DB uri
        featuredb_uri : 피처DB uri
        metadatadb_uri : 메타데이터DB uri
        plcdb_uri : plcDB uri
        fdcdb_uri : fdcDB uri
        endpoint_url : endpoint url
        aws_access_key_id : minio 접속 정보 아이디
        aws_secret_access_key : minio 접속 정보 비밀번호
        verify : 기본적으로 False 사용.
        bucket_name : 버킷 이름
        timezone : 타임존
        line_num : 라인 번호
    """

    servicedb_uri: str
    featuredb_uri: str
    metadatadb_uri: str
    plcdb_uri: str
    fdcdb_uri: str
    endpoint_url: str
    aws_access_key_id: str
    aws_secret_access_key: str
    verify: bool
    bucket_name: str
    timezone: str
    line_num: str


setting = Setting()

# 추후에는 이 방식으로 동작하도록 변경 예정
# class GlobalSettings(BaseSettings):

#     class Config:


# class DevSettings(GlobalSettings):

#     class Config:


# class ProdSettings(GlobalSettings):

#     class Config:


# class FactorySettings:
#     @staticmethod
#     def load():
#         if env_state == "dev":
