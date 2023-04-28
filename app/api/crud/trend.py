"""트렌드와 관련된 CRUD 모음.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
from datetime import datetime
from typing import Optional, TypeVar

from api.crud.util import determine_period
from sqlalchemy import and_
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker

T = TypeVar("T")


class Trend:
    """템플릿 메소드 패턴을 위한 부모 클래스 정의.

    Args:
        columns (list[str]): 조회할 컬럼들 목록
        required_dict (dict): 조회할 때 매번 공통으로 사용되는 컬럼 정보
        e.g. required_dict = {'equipment_id':1, 'motor_number':3, 'plc':3}
    """

    def __init__(self) -> None:
        """컬럼과 required_dict(필수 인자)정의."""
        self.columns: Optional[list[str]] = None
        self.required_dict: Optional[dict] = None
        self.start: Optional[datetime] = None
        self.end: Optional[datetime] = None

    def read_trend(
        self,
        SessionLocal: sessionmaker,
        orm_cls: DeclarativeMeta,
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


class VariableLoad(Trend):
    """변속 모터 부하 인자 정의 클래스."""

    def __init__(
        self,
        required_dict: dict[str, int],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> None:
        """변속 모터 부하 인자 목록 정의.

        Args:
            required_dict (Dict[str, int]): 조회할 때 매번 공통으로 사용되는 컬럼 정보
            start (datetime): 조회 시작 시간
            end (datetime): 조회 끝 시간
        """
        self.required_dict = required_dict
        self.columns = [
            "acq_time",
            "avg_load",
            "avg_load_ratio",
            "peak_load",
            "peak_load_ratio",
        ]
        self.start, self.end = determine_period(start, end)


class UniformLoad(Trend):
    """정속 모터 부하 인자 정의 클래스."""

    def __init__(
        self,
        required_dict: dict[str, int],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> None:
        """정속 모터 부하 인자 목록 정의.

        Args:
            required_dict (Dict[str, int]): 조회할 때 매번 공통으로 사용되는 컬럼 정보
            start (datetime): 조회 시작 시간
            end (datetime): 조회 끝 시간
        """
        self.required_dict = required_dict
        self.columns = [
            "acq_time",
            "rolling_load",
            "rolling_load_ratio",
        ]
        self.start, self.end = determine_period(start, end)


class VariableOperating(Trend):
    """변속 모터 운영 인자 정의 클래스."""

    def __init__(
        self,
        required_dict: dict[str, int],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> None:
        """변속 모터 운영 인자 목록 정의.

        Args:
            required_dict (Dict[str, int]): 조회할 때 매번 공통으로 사용되는 컬럼 정보
            start (datetime): 조회 시작 시간
            end (datetime): 조회 끝 시간
        """
        self.required_dict = required_dict
        self.columns = ["acq_time", "cutting_interval"]
        self.start, self.end = determine_period(start, end)


class UniformOperating(Trend):
    """정속 모터 운영 인자 정의 클래스."""

    def __init__(
        self,
        required_dict: dict[str, int],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> None:
        """정속 모터 운영 인자 목록 정의.

        Args:
            required_dict (Dict[str, int]): 조회할 때 매번 공통으로 사용되는 컬럼 정보
            start (datetime): 조회 시작 시간
            end (datetime): 조회 끝 시간
        """
        self.required_dict = required_dict
        self.columns = ["acq_time", "signal_noise_ratio"]
        self.start, self.end = determine_period(start, end)


class VariableDiagnosis(Trend):
    """변속 모터 인자 정의 클래스."""

    def __init__(
        self,
        required_dict: dict[str, int],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> None:
        """변속 모터 진단 인자 목록 정의.

        Args:
            required_dict (Dict[str, int]): 조회할 때 매번 공통으로 사용되는 컬럼 정보
            start (datetime): 조회 시작 시간
            end (datetime): 조회 끝 시간
        """
        self.required_dict = required_dict
        self.columns = [
            "acq_time",
            "current_corr_pvm_median",
            "current_noise_rms_pvm_median",
        ]
        self.start, self.end = determine_period(start, end)


class UniformExternalDiagnosis(Trend):
    """정속 모터 외부베어링 1개(u3e) 인자 정의 클래스."""

    def __init__(
        self,
        required_dict: dict[str, int],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> None:
        """u3e 모터 진단 인자 목록 정의.

        Args:
            required_dict (Dict[str, int]): 조회할 때 매번 공통으로 사용되는 컬럼 정보
            start (datetime): 조회 시작 시간
            end (datetime): 조회 끝 시간
        """
        self.required_dict = required_dict
        self.columns = [
            "acq_time",
            "stator_diagnosis",
            "motor_bearing_diagnosis",
            "gear_shaft_diagnosis",
            "external_bearing_diagnosis",
            "coupling_diagnosis",
            "belt_diagnosis",
            "final_diagnosis",
        ]
        self.start, self.end = determine_period(start, end)


class UniformTensionDiagnosis(UniformExternalDiagnosis):
    """정속 모터 텐션베어링 포함된(u3t) 모터의 인자 정의 클래스."""

    def __init__(
        self,
        required_dict: dict[str, int],
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
    ) -> None:
        """u3t 모터 진단 인자 목록 정의.

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
            "external_main_bearing_diagnosis",
            "external_tension_bearing_diagnosis",
        ]
