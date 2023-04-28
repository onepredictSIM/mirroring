"""상세페이지와 관련된 CRUD 모음.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
from datetime import datetime
from typing import Optional, TypeVar

from api.crud.setting_client import (
    read_motor_category,
    read_single_external_setting,
    read_single_tension_setting,
    read_single_variable_setting,
)
from api.crud.util import determine_period
from db.plc.crud.load import load_current_plc_model
from sqlalchemy import and_
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker

T = TypeVar("T")


class MotorInfo:
    """현재 plc에 대한 특정호기 특정모터번호에 대한 parameter 리턴받을 수 있는 클래스."""

    def __init__(self, equipment_id: int, motor_number: int) -> None:
        """미국 LGES까지는 line이 1개씩만 존재하므로 저렇게 하드코딩으로 써둠.

        Args:
            equipment_id (int): 호기 번호
            motor_number (int): 모터 번호
        """
        self.equipment_id = equipment_id
        self.motor_number = motor_number
        self.category = read_motor_category(self.equipment_id, self.motor_number)
        self.plc = load_current_plc_model(
            {
                "line_id": 1,
                "equipment_id": self.equipment_id,
                "name": "CellState_Model",
            },
        )
        self.category_parameter_function = {
            "u3e": read_single_external_setting,
            "u3t": read_single_tension_setting,
            "v3": read_single_variable_setting,
        }

    def read_motor_parameter(self) -> dict:
        """특정 모터의 카테고리에 맞는 feature들을 로딩.

        대쉬보드 상세페이지의 진단 메시지 및 진단 트렌드를 보여주기 위해 존재한다.

        Returns:
            dict
        """
        return self.category_parameter_function[self.category](
            self.equipment_id,
            self.motor_number,
            self.plc,
        ).dict()


class ReadDetailFeature:
    """템플릿 메소드 패턴을 위한 부모 클래스 정의.

    Args:
        columns (list[str]): 조회할 컬럼들 목록
        required_dict (dict): 조회할 때 매번 공통으로 사용되는 컬럼 정보
    Examples:
        required_dict = {'equipment_id':1, 'motor_number':3, 'plc':3}
    """

    def __init__(self) -> None:
        """컬럼과 required_dict(필수 인자)정의."""
        self.columns: Optional[list[str]] = None
        self.required_dict: Optional[dict] = None
        self.start: Optional[datetime] = None
        self.end: Optional[datetime] = None

    def read_detail(
        self, SessionLocal: sessionmaker, orm_cls: DeclarativeMeta,
    ) -> list[Row]:
        """부모 클래스에서 정의되는 템플릿 메소드.

        자식 클래스에서 정의되는 columns들을 조회(SELECT)하고,
        WHERE 조건으로는 self.start와 self.end 기간 사이와
        required_dict의 조건과 일치하는 row들을 필터를 걸고,
        ORDER BY로는 계측 시간(acq_time) 순서대로 리턴하도록 함.

        Args:
            SessionLocal (sessionmaker): sessionmaker 객체
            orm_cls (DeclarativeMeta): ORM 클래스
        Returns:
            list[Row]
        """
        with SessionLocal() as session:
            query_results = (
                session.query(*[getattr(orm_cls, column) for column in self.columns])
                .filter(
                    and_(
                        orm_cls.acq_time > self.start,
                        orm_cls.acq_time < self.end,
                    ),
                )
                .filter(
                    *[
                        getattr(orm_cls, key) == value
                        for key, value in self.required_dict.items()
                    ],
                )
                .order_by(orm_cls.acq_time.asc())
                .all()
            )
        return query_results


class UniformExternalDetailFeature(ReadDetailFeature):
    """정속 모터 외부베어링 1개(u3e) 상세페이지 인자 정의 클래스."""

    def __init__(
        self,
        required_dict: dict[str, int],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> None:
        """모터 카테고리(u3e)에서 조회해야하는 feature 목록 정의.

        Args:
            required_dict (Dict[str, int]): 조회할 때 매번 공통으로 사용되는 컬럼 정보
            start (datetime): 조회 시작 시간
            end (datetime): 조회 끝 시간
        """
        self.required_dict = required_dict
        self.columns = [
            "equipment_id",
            "motor_number",
            "plc",
            "acq_time",
            "rolling_load",
            "rolling_load_ratio",
            "signal_noise_ratio",
            "winding_supply_freq_amp_unbalance_ratio_median",
            "motor_bpfi_1x_median",
            "gearbox_rotation_freq_amp_median",
            "external_bpfo_1x_median",
            "coupling_supply_freq_amp_median",
            "belt_kurtosis_max_median",
            "stator_diagnosis",
            "motor_bearing_diagnosis",
            "gear_shaft_diagnosis",
            "external_bearing_diagnosis",
            "coupling_diagnosis",
            "belt_diagnosis",
            "final_diagnosis",
        ]
        self.start, self.end = determine_period(start, end)


class UniformTensionDetailFeature(UniformExternalDetailFeature):
    """정속 모터 텐션베어링 포함된(u3t) 모터의 상세페이지 인자 정의 클래스."""

    def __init__(
        self,
        required_dict: dict[str, int],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> None:
        """모터 카테고리(u3t)에서 조회해야하는 feature 목록 정의.

        u3t 카테고리는 u3e의 자식 클래스이므로,
        부모 클래스의 메소드를 호출한 뒤, 추가 컬럼만 더해줌.

        Args:
            required_dict (Dict[str, int]): 조회할 때 매번 공통으로 사용되는 컬럼 정보
            start (datetime): 조회 시작 시간
            end (datetime): 조회 끝 시간
        """
        super().__init__(required_dict, start, end)
        self.columns.remove("external_bearing_diagnosis")
        self.columns += [  # type: ignore[operator]
            "tension_bpfo_1x_median",
            "external_main_bearing_diagnosis",
            "external_tension_bearing_diagnosis",
        ]


class VariablePhase3DetailFeature(ReadDetailFeature):
    """변속 3상 모터 상세페이지 피처 정의 클래스."""

    def __init__(
        self,
        required_dict: dict[str, int],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> None:
        """모터 카테고리(v3)에서 조회해야하는 feature 목록 정의.

        Args:
            required_dict (Dict[str, int]): 조회할 때 매번 공통으로 사용되는 컬럼 정보
            start (datetime): 조회 시작 시간
            end (datetime): 조회 끝 시간
        """
        self.required_dict = required_dict
        self.columns = [
            "equipment_id",
            "motor_number",
            "plc",
            "acq_time",
            "avg_load",
            "avg_load_ratio",
            "peak_load",
            "peak_load_ratio",
            "cutting_interval",
            "current_corr_pvm_median",
            "current_noise_rms_pvm_median",
            "current_corr_pvm_diagnosis",
            "current_noise_rms_pvm_diagnosis",
            "final_diagnosis",
        ]
        self.start, self.end = determine_period(start, end)
