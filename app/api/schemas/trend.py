"""TrendInitAPI와 관련된 모듈 모음.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
from typing import Optional

from pydantic import BaseModel


class TrendInit(BaseModel):
    """Trend페이지를 누르면 처음 필요한 정보(운영/건전성 인자목록)를 전달하는 클래스."""

    @classmethod
    def apply_operating_prefix(cls) -> list[str]:
        """운영 인자에 lges.feature.opearting prefix를 붙여주는 함수."""
        lges_prefix_attrs = []
        for key in cls.__fields__:
            lges_prefix_attrs.append(".".join(["lges.feature.operating", key]))
        return lges_prefix_attrs

    @classmethod
    def apply_health_prefix(cls) -> list[str]:
        """건전성 인자에 lges.feature.health prefix를 붙여주는 함수."""
        lges_prefix_attrs = []
        for key in cls.__fields__:
            lges_prefix_attrs.append(".".join(["lges.feature.health", key]))
        return lges_prefix_attrs


class OperatingTrendInit(TrendInit):
    """운영 인자 트렌드 init 때 필요한 attribute 관리. attribute들의 속성은 의미 없음.

    Attributes:
        avgLoad: 평균 부하
        avgLoadRatio: 평균 부하율
        peakLoad: 피크 부하
        peakLoadRatio: 피크 부하율
        cuttingInterval: 커팅 시간 간격
        rollingLoad: 전류 실효값
        SNR: 신호 노이즈 비율
        rollingLoadRatio: 회전 부하율
    """

    avgLoad: Optional[str] = None  # noqa: N815
    avgLoadRatio: Optional[str] = None  # noqa: N815
    peakLoad: Optional[str] = None  # noqa: N815
    peakLoadRatio: Optional[str] = None  # noqa: N815
    cuttingInterval: Optional[str] = None  # noqa: N815
    rollingLoad: Optional[str] = None  # noqa: N815
    SNR: Optional[str] = None
    rollingLoadRatio: Optional[str] = None  # noqa: N815


class HealthTrendInit(TrendInit):
    """건전성 인자 트렌드 init 때 필요한 attribute 관리. attribute들의 속성은 의미 없음.

    Attributes:
        motor_bearing_diagnosis: 모터 베어링 고장 진단 결과
        external_bearing_diagnosis: 구동부 베어링 고장 진단 결과
        stator_diagnosis: 모터 전기적 고장 진단 결과
        gear_shaft_diagnosis: 기어 고장 진단 결과
        coupling_diagnosis: 커플링 고장 진단 결과
        belt_diagnosis: 벨트 고장 진단 결과
        correlation_diagnosis: 전류 유사도 진단 결과
        noise_diagnosis: 전류 노이즈 진단 결과
        external_main_bearing_diagnosis: 구동부 메인베어링 고장 진단 결과
        external_tension_bearing_diagnosis: 구동부 텐션베어링 고장 진단 결과
    """

    motor_bearing_diagnosis: Optional[str] = None
    external_bearing_diagnosis: Optional[str] = None
    stator_diagnosis: Optional[str] = None
    gear_shaft_diagnosis: Optional[str] = None
    coupling_diagnosis: Optional[str] = None
    belt_diagnosis: Optional[str] = None
    correlation_diagnosis: Optional[str] = None
    noise_diagnosis: Optional[str] = None
    external_main_bearing_diagnosis: Optional[str] = None
    external_tension_bearing_diagnosis: Optional[str] = None
