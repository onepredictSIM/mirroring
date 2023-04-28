"""상세페이지를 실행할 때, 프론트엔드측에서 처음 요청해서 얻어야하는 API.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
from enum import Enum
from typing import Union

from pydantic import BaseModel


class UniformExternalDetailInit(BaseModel):
    """모터 카테고리가 u3e일 때, 상세페이지 클릭시 처음 요청되어야하는 정보.

    Attributes:
        category : 모터 카테고리
        operating : 운영 인자 목록 리스트
        health : 건전성 인자 목록 리스트
    """

    category = "u3e"
    operating = [
        "lges.feature.operating.rollingLoad",
        "lges.feature.operating.rollingLoadRatio",
        "lges.feature.operating.SNR",
    ]
    health = [
        "lges.feature.health.motorStator",
        "lges.feature.health.motorBearing",
        "lges.feature.health.gearbox",
        "lges.feature.health.externalBearing",
        "lges.feature.health.coupling",
        "lges.feature.health.belt",
    ]


class UniformTensionDetailInit(BaseModel):
    """모터 카테고리가 u3t일 때, 상세페이지 클릭시 처음 요청되어야하는 정보.

    Attributes:
        category : 모터 카테고리
        operating : 운영 인자 목록 리스트
        health : 건전성 인자 목록 리스트
    """

    category = "u3t"
    operating = [
        "lges.feature.operating.rollingLoad",
        "lges.feature.operating.rollingLoadRatio",
        "lges.feature.operating.SNR",
    ]
    health = [
        "lges.feature.health.motorStator",
        "lges.feature.health.motorBearing",
        "lges.feature.health.gearbox",
        "lges.feature.health.externalBearing",
        "lges.feature.health.TensionBearing",
        "lges.feature.health.coupling",
        "lges.feature.health.belt",
    ]


class VariablePhase3DetailInit(BaseModel):
    """모터 카테고리가 v3일 때, 상세페이지 클릭시 처음 요청되어야하는 정보.

    Attributes:
        category : 모터 카테고리
        operating : 운영 인자 목록 리스트
        health : 건전성 인자 목록 리스트
    """

    category = "v3"
    operating = [
        "lges.feature.operating.avgLoad",
        "lges.feature.operating.avgLoadRatio",
        "lges.feature.operating.peakLoad",
        "lges.feature.operating.peakLoadRatio",
        "lges.feature.operating.cuttingInterval",
    ]
    health = ["lges.feature.health.correlation", "lges.feature.health.noise"]


class MotorCategory(Enum):
    """motor category를 Enum으로 관리하는 클래스.

    Attributes:
        U3E: 정속 모터 외부 베어링 1개
        U3T: 정속 모터 외부 베어링 1개, 텐션 베어링 1개
        V3: 변속 3상 모터
    """

    U3E = "u3e"
    U3T = "u3t"
    V3 = "v3"

    @property
    def detail_init_class(
        self,
    ) -> Union[
        UniformExternalDetailInit,
        UniformTensionDetailInit,
        VariablePhase3DetailInit,
    ]:
        """모터 카테고리별로 해당 DetailInit 클래스를 리턴하는 함수."""
        if self == MotorCategory.U3E:
            return UniformExternalDetailInit
        elif self == MotorCategory.U3T:
            return UniformTensionDetailInit
        elif self == MotorCategory.V3:
            return VariablePhase3DetailInit
        else:
            raise ValueError(f"Invalid category: {self.value}")


class DetailInitFactory:
    """모터 카테고리별로 DetailInit 클래스 객체를 리턴하는 팩토리 클래스."""

    @staticmethod
    def create_detail(
        category: str,
    ) -> Union[
        UniformExternalDetailInit,
        UniformTensionDetailInit,
        VariablePhase3DetailInit,
    ]:
        """모터 카테고리별로 DetailInit 클래스 객체를 리턴하는 함수.

        Args:
            category (str): 모터 카테고리
        Returns:
            Union[UniformExternalDetailInit, UniformTensionDetailInit,
                    VariablePhase3DetailInit]
        """
        motor_category = MotorCategory(category)
        detail_init_class = motor_category.detail_init_class
        return detail_init_class()
