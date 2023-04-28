"""Define LGES_metadata Database Model.

Motor를 중심으로 하는 Star Schema 구조를 채택
추가 설명 요청 시 description 개선 가능
- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
- Reference: https://onepredict.atlassian.net/wiki/spaces/PROD/pages/1275167027/LAMI2.LG-ES+ERD
"""

from db.table import Base
from sqlalchemy import VARCHAR, Column, DateTime, Integer, String
from sqlalchemy.sql import func


class MetaData(Base):
    """원시 데이터의 메타 정보(모터, 취득 시간)와 경로를 저장하는 테이블.

    Attributes:
        line_id : 라인 번호
        equipment_id : 호기 번호
        motor_number: 모터 번호
        phase : 데이터 종류(e.g. 전류:uvw)
        acq_time: 데이터 취득 시간
        file_path: 데이터 파일 경로
        sampling_rate: 샘플링 레이트
        sample_size : 데이터 길이, 샘플 사이즈(샘플링 레이트*계측 시간)
    """

    __tablename__ = "metadata"

    line_id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer, primary_key=True)
    motor_number = Column(Integer, primary_key=True)
    phase = Column(VARCHAR(16), primary_key=True)
    acq_time = Column(DateTime(timezone=True), default=func.now(), primary_key=True)
    file_path = Column(String, nullable=False)
    sampling_rate = Column(Integer, nullable=False)
    sample_size = Column(Integer, nullable=False)
