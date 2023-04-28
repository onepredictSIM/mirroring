"""Define Motor DTO.

각 모터 별로 모터 스펙, 파라미터 정보를 모두 담을 수 있도록 하는 DTO 클래스를 정의한다.
- Author: Kibum Park, Sewon Kim
- Contact: kibum.park@onepredict.com, sewon.kim@onepredict.com.
"""

from typing import Optional

from pydantic import BaseModel


class UniformSpeedMotor(BaseModel):
    """정속 모터의 스펙과 파라미터를 저장하는 DTO 클래스.

    Attributes:
        rated_current: 정격 전류
        pole: 폴 수
        supply_freq: 모터의 공급 주파수
        name: 모터명
        category: 정속/변속(u/v), 단상/3상(1:3) 여부. ex) 정속 3상 = u3
        gear_ratio: 기어비
        max_current: 최대 전류
        stator_feature_upper_warning: 고정자 고장 인자의 2차 상한
        stator_feature_upper_caution: 고정자 고장 인자의 1차 상한
        motor_bearing_feature_lower_warning: 내부 베어링 고장 인자의 2차 하한
        motor_bearing_feature_lower_caution: 내부 베어링 고장 인자의 1차 하한
        gear_feature_upper_warning: 기어 샤프트 고장 인자의 2차 상한
        gear_feature_upper_caution: 기어 샤프트 고장 인자의 1차 상한
        external_bearing_feature_upper_warning: 외부 베어링 고장 인자의 2차 상한
        external_bearing_feature_upper_caution: 외부 베어링 고장 인자의 1차 상한
        moving_median_sample_number: 최종 진단 시 중위값을 구하기 위한 샘플의 개수
        plc : plc 모드
        motor_rpm: 서보 모터의 회전 속도
        motor_bearing_ball_diameter: 서보모터 베어링 볼 지름
        motor_bearing_pitch_diameter: 서보모터 베어링 피치 지름
        motor_bearing_ball_number: 서보모터 베어링 볼 개수
        external_bearing_ball_diameter: 외부베어링 베어링 볼 지름
        external_bearing_pitch_diameter: 외부베어링 베어링 피치 지름
        external_bearing_ball_number: 외부베어링 베어링 볼 개수.
    """

    line_id: int
    equipment_id: int
    equipment_name: str
    number: int
    rated_current: float
    pole: int
    supply_freq: float
    name: str
    category: str
    gear_ratio: float
    max_current: Optional[float]
    threshold_minimum_current: float = 0.1
    test_signal_num: int = 10

    stator_feature_warning: float
    stator_feature_caution: float
    motor_bearing_feature_warning: float
    motor_bearing_feature_caution: float
    gear_shaft_feature_warning: float
    gear_shaft_feature_caution: float
    external_bearing_feature_warning: float
    external_bearing_feature_caution: float
    tension_bearing_feature_warning: Optional[float] = None
    tension_bearing_feature_caution: Optional[float] = None
    coupling_feature_warning: float
    coupling_feature_caution: float
    belt_feature_warning: float
    belt_feature_caution: float

    motor_bearing_moving_median_sample_number: int
    external_bearing_moving_median_sample_number: int
    plc: int
    motor_bearing_ball_diameter: float
    motor_bearing_pitch_diameter: float
    motor_bearing_ball_number: int
    external_bearing_ball_diameter: float
    external_bearing_pitch_diameter: float
    external_bearing_ball_number: int
    tension_bearing_ball_diameter: Optional[float] = None
    tension_bearing_pitch_diameter: Optional[float] = None
    tension_bearing_ball_number: Optional[int] = None
    tension_bearing_moving_median_sample_number: Optional[int] = None
    external_bearing_number: Optional[int] = None
    tension_bearing_number: Optional[int] = None


class VariableSpeedMotor(BaseModel):
    """변속 모터의 스펙과 파라미터를 저장하는 DTO 클래스.

    Attributes:
        rated_current: 정격 전류
        pole: 폴 수
        name: 모터명
        category: 정속/변속(u/v), 단상/3상(1:3) 여부. ex) 정속 3상 = u3
        gear_ratio: 기어비
        max_current: 최대 전류
        current_corr_lower_warning: 전류 유사도의 1차 하한
        current_corr_lower_caution: 전류 유사도의 2차 하한
        current_noise_rms_upper_warning: 전류 노이즈 rms의 2차 상한
        current_noise_rms_upper_caution: 전류 노이즈 rms의 1차 싱한
        current_noise_rms_lower_warning: 전류 노이즈 rms의 2차 하한
        current_noise_rms_lower_caution: 전류 노이즈 rms의 1차 하한
        moving_median_sample_number: 최종 진단 시 중위값을 구하기 위한 샘플의 개수
        plc : plc 모드
        template_u : u상 전류 템플릿
        template_v : v상 전류 템플릿
        template_w : w상 전류 템플릿.
    """

    line_id: int
    equipment_id: int
    equipment_name: str
    number: int
    rated_current: float
    pole: Optional[int] = 0
    name: str
    category: str
    gear_ratio: Optional[float] = 0
    max_current: float
    current_corr_pvm_lower_warning: float
    current_corr_pvm_lower_caution: float
    current_noise_rms_upper_warning: float
    current_noise_rms_upper_caution: float
    current_noise_rms_lower_warning: float
    current_noise_rms_lower_caution: float
    moving_median_sample_number: int
    threshold_minimum_current: float = 0.1
    plc: int
    template_u: list[float]
    template_v: list[float]
    template_w: list[float]
