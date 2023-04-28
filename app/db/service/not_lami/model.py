"""Define Database Model.

Motor를 중심으로 하는 Star Schema 구조를 채택
추가 설명 요청 시 description 개선 가능
- Author: Kibum Park
- Contact: kibum.park@onepredict.com
- Reference: https://onepredict.atlassian.net/wiki/spaces/PROD/pages/1247576300/LAMI2.LG-ES+ERD
             https://onepredict.atlassian.net/wiki/spaces/PROD/pages/1250754670/LAMI2.LG-ES.
"""

from db.table import Base
from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func


class Line(Base):
    """라인 상태를 저장하는 테이블.

    Attributes:
        id: 라인 id
        category : 라미, 스태킹, 패키지 등의 분류
        name : 라인 이름.
    """

    __tablename__ = "line"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False)
    name = Column(String, nullable=False)
    __table_args__ = ({"extend_existing": True},)


class Equipment(Base):
    """라인에 있는 호기 정보를 저장하는 테이블.

    Attributes:
        id: 호기 id
        line_id: 라인 id
        name : 호기 이름.
    """

    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    line_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)

    __table_args__ = ({"extend_existing": True},)


class Motor(Base):
    """모터 스펙의 현재 상태를 저장하는 테이블.

    Attributes:
        id: id
        equipment_id: 호기 id
        number : 특정 호기의 모터 번호
        updated_time : 모터 정보가 업데이트된 날짜
        name: 모터명
        category: 정속/변속(u/v), 단상/3상(1:3) 여부. ex) 정속 3상 = u3
        rated_current: 정격 전류
        supply_freq: 모터의 공급 주파수
        pole: 폴 수
        gear_ratio: 기어비
        max_current: 최대 전류.
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, nullable=False)
    number = Column(Integer, nullable=False)
    updated_time = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    rated_current = Column(Float, nullable=True)
    pole = Column(Integer, nullable=True)
    gear_ratio = Column(Float, nullable=True)
    max_current = Column(Float, nullable=True)

    __table_args__ = ({"extend_existing": True},)
