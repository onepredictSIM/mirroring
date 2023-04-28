"""dashboard와 관련된 CRUD 모음.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
import re
from typing import Optional, TypeVar, Union

from api.crud.interface import AnalysisSQL
from core.config import setting
from db.plc.crud.load import load_current_plc_model
from db.plc.database import PLCSessionLocal
from db.plc.model import PLCModel
from db.service.database import SessionLocal
from db.service.model import Equipment, Line, MotorBearing
from fastapi import HTTPException
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker
from util.utils import row_to_dict

T = TypeVar("T")


class Dashboard:
    """Dashboard API 조회 메소드를 구현한 부모 클래스."""

    def __init__(
        self, equipment_id: int, motor_number: int, plc: Optional[int] = None,
    ) -> None:
        """대쉬보드 클래스 생성자.

        Args:
            equipment_id (int): 호기 번호
            motor_number (int): 모터 번호
            plc (int):plc 값이 None(default)로 주어진 경우,
                        PLC log테이블에 들어있는 가장 최신 plc값 사용,
        """
        self.columns: list[str] = None  # type: ignore[assignment]
        line_equipment = {
            "line_id": 1,
            "equipment_id": equipment_id,
            "name": "CellState_Model",
        }
        self.plc = load_current_plc_model(line_equipment) if plc is None else plc
        self.required_dict = {
            "equal_condition": {
                "equipment_id": equipment_id,
                "motor_number": motor_number,
                "plc": self.plc,
            },
            "order_by_condition": {"column": "acq_time", "option": "desc"},
            "limit_condition": 1,
        }

    def read_dashboard(
        self,
        SessionLocal: sessionmaker,
        orm_cls: DeclarativeMeta,
    ) -> list[Row]:
        """특정 컬럼과 orm class를 조건으로 주어 AnalysisSQL 세션을 생성.

        주어진 조건(required_dict)에 맞는 결과를 리턴.

        Args:
            SessionLocal: sessionmaker 객체
            orm_cls : ORM 클래스
        Returns:
            list[Row]
        """
        analysis_session = AnalysisSQL(self.columns, SessionLocal, orm_cls)
        query_results = analysis_session.load_query_result(**self.required_dict)
        return query_results


class VariableDashboard(Dashboard):
    """변속 Dashboard 클래스."""

    def __init__(
        self, equipment_id: int, motor_number: int, plc: Optional[int] = None,
    ) -> None:
        """대쉬보드에서 변속 모터 관련 인자를 나타내기 위해 사용되는 클래스 생성자.

        Args:
            equipment_id (int): 호기 번호
            motor_number (int): 모터 번호
            plc (int): 배터리 생산 모드.
        """
        super().__init__(equipment_id, motor_number, plc)
        self.columns = [
            "equipment_id",
            "acq_time",
            "motor_number",
            "plc",
            "final_diagnosis",
        ]


class UniformExternalDashboard(Dashboard):
    """정속 외부 베어링 1개 Dashboard 클래스."""

    def __init__(
        self, equipment_id: int, motor_number: int, plc: Optional[int] = None,
    ) -> None:
        """대쉬보드에서 외부 베어링 관련 인자를 나타내기 위해 사용되는 클래스 생성자.

        Args:
            equipment_id (int): 호기 번호
            motor_number (int): 모터 번호
            plc (int): 배터리 생산 모드.
        """
        super().__init__(equipment_id, motor_number, plc)
        self.columns = [
            "equipment_id",
            "acq_time",
            "motor_number",
            "plc",
            "stator_diagnosis",
            "motor_bearing_diagnosis",
            "gear_shaft_diagnosis",
            "external_bearing_diagnosis",
            "coupling_diagnosis",
            "belt_diagnosis",
            "final_diagnosis",
        ]


class UniformTensionDashboard(UniformExternalDashboard):
    """정속 외부 베어링 2개 Dashboard 클래스."""

    def __init__(
        self, equipment_id: int, motor_number: int, plc: Optional[int] = None,
    ) -> None:
        """대쉬보드에서 텐션 베어링 관련 인자를 나타내기 위해 사용되는 클래스 생성자.

        Args:
            equipment_id (int): 호기 번호
            motor_number (int): 모터 번호
            plc (int): 배터리 생산 모드.
        """
        super().__init__(equipment_id, motor_number, plc)
        self.columns.remove("external_bearing_diagnosis")
        self.columns += [
            "external_main_bearing_diagnosis",
            "external_tension_bearing_diagnosis",
        ]


class TriggerDashboard(Dashboard):
    """Trigger 대쉬보드 클래스."""

    def __init__(
        self, equipment_id: int, motor_number: int, plc: Optional[int] = None,
    ) -> None:
        """대쉬보드에서 트리거를 나타내기 위해 사용되는 클래스 생성자.

        Args:
            equipment_id (int): 호기 번호
            motor_number (int): 모터 번호
            plc (int): 배터리 생산 모드.
        """
        super().__init__(equipment_id, motor_number, plc)
        self.columns = [
            "equipment_id",
            "acq_time",
            "motor_number",
            "plc",
            "status",
            "plc_status",
            "supply_freq_by_data",
            "rms_u",
        ]


def load_equipments() -> list[dict[str, Union[int, str]]]:
    """현재 라인에 들어있는 호기 조회.

    Returns:
        list[dict[str, Union[int, str]]]
    """
    with SessionLocal() as session:
        query_results = session.query(Equipment).all()

    return row_to_dict(query_results)


def load_plcmodel_by_equipment(equipment_id: int) -> list[dict[str, Union[int, str]]]:
    """현재 호기에 들어있는 plc 모델 정보 리턴.

    Args:
        equipment_id (int): 호기 번호
    Returns:
        list[dict[str, Union[int, str]]]
    """
    columns = ["equipment_id", "model", "name", "description"]
    orm_class = PLCModel
    analysis_session = AnalysisSQL(columns, PLCSessionLocal, orm_class)
    required_dict = {"equal_condition": {"line_id": 1, "equipment_id": equipment_id}}
    query_results = analysis_session.load_query_result(**required_dict)
    if not query_results:
        raise HTTPException(
            status_code=404,
            detail="해당 호기에 대한 plc 정보가 없습니다.",
        )
    return query_results


def get_supply_freq(str_motor_id: str, equipment_id: int, plc: int) -> dict:
    """대쉬보드 정속모터 supply freq 정보 리턴.

    Args:
        str_motor_id (str): 모터 번호(e.g. motor1, motor2)
        equipment_id (int): 호기 번호
        plc (int): 배터리 생산 모드
    Returns:
        dict
    """
    motor_number = int(re.sub(r"[^0-9]", "", str_motor_id))
    columns = ["supply_freq"]
    orm_class = MotorBearing
    analysis_session = AnalysisSQL(columns, SessionLocal, orm_class)
    required_dict = {
        "equal_condition": {
            "equipment_id": equipment_id,
            "motor_number": motor_number,
            "plc": plc,
        },
    }
    query_results = analysis_session.load_query_result(**required_dict)
    if not query_results:
        raise HTTPException(
            status_code=404,
            detail="해당 호기에 대한 plc 정보가 없습니다.",
        )
    return query_results[0]


def load_line_equipment_category() -> list[dict]:
    """line의 카테고리, line 이름, 호기 아이디, 호기 이름을 리턴해주는 함수."""
    with SessionLocal() as session:
        query_result = (
            session.query(Line.category, Line.name, Equipment.id, Equipment.name)
            .filter(Line.name == setting.line_num)
            .join(Equipment, Line.id == Equipment.line_id)
            .all()
        )
    key_list = ["category", "line_name", "equipment_id", "equipment_name"]
    response = []
    for row in query_result:
        result_dict = dict(zip(key_list, row))
        response.append(result_dict)
    return response
