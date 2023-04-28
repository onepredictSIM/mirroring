"""Define LGES_Plc Database Model.

Motor를 중심으로 하는 Star Schema 구조를 채택
추가 설명 요청 시 description 개선 가능
- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
- Reference: https://onepredict.atlassian.net/wiki/spaces/PROD/pages/1275167027/LAMI2.LG-ES+ERD
"""

from db.table import Base
from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.sql import func


class PLCModel(Base):
    """라인/호기 번호에 따른 plc 모델을 담는 테이블.

    Attributes:
        id: id
        line_id: 라인 id
        equipment_id: 호기 id
        model: 모델 번호
        name : 셀 생산 모드
        description: 상세 설명
    """

    __tablename__ = "model"

    id = Column(Integer, primary_key=True, autoincrement=True)
    line_id = Column(Integer, nullable=False)
    equipment_id = Column(Integer, nullable=False)
    model = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)


class MemoryMapping(Base):
    """plc 메모리 정보를 담는 테이블.

    Attributes:
        id: id
        line_id: 라인 id
        equipment_id: 호기 id
        name : plc에 적혀있는 내용들
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    line_id = Column(Integer, nullable=False)
    equipment_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)


class PLCLog(Base):
    """plc 메모리 정보를 담는 테이블.

    Attributes:
        id: id
        timestamp: PLC Log 기록 시간
        mm_id: MemoryMapping 테이블에 대응되는 id
        value: 해당 memory mapping id가 가질 수 있는 값
    """

    __tablename__ = "log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    mm_id = Column(Integer, nullable=False)
    value = Column(String, nullable=False)

    __table_args__: tuple = (
        UniqueConstraint("timestamp", "mm_id", name="log_unique"),
        {},
    )
