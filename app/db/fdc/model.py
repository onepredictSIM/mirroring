"""Define FDC Database Model.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""

from db.table import Base
from sqlalchemy import Column, DateTime, Integer, String


class FDCConfig(Base):
    """라인 상태를 저장하는 테이블.

    Attributes:
        id: id
        updated_time: 업데이트된 시간
        connect_retries:
        reconnect_retries:
        reconnect_retries_waits_in_msecs:
        connect_retries_per_host:
        vpn:
        user_name:
        client_name:
        send_interval: 전송 주기.
    """

    __tablename__ = "config"

    id = Column(Integer, primary_key=True)
    updated_time = Column(DateTime, nullable=False)
    host = Column(String, nullable=False)
    vpn = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    client_name = Column(String, nullable=False)
    connect_attempts = Column(Integer, nullable=False)
    reconnect_attempts = Column(Integer, nullable=False)
    reconnect_interval = Column(Integer, nullable=False)
    connect_retries_per_host = Column(Integer, nullable=False)
    message_interval = Column(Integer, nullable=False)
    sheet_path = Column(String, nullable=False)
    featuredb_uri = Column(String, nullable=False)
