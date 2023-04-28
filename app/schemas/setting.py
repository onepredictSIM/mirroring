"""setting client endpoint와 관련된 pydantic class 모음.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com.
"""

from datetime import datetime
from typing import Any, Optional, Union

from pydantic import BaseModel, PostgresDsn
from pydantic.typing import Literal


class MotorEquipment(BaseModel):
    """setting-client의 /metadata 엔드포인트의 Response에 해당하는 DTO.

    Attributes:
        line_id : 라인 번호
        equipment_name : 호기 이름
        equipment_id : 호기 번호
        number : 모터 번호
        name : 모터 이름
        category : 모터 카테고리.
    """

    line_id: int
    equipment_name: str
    equipment_id: int
    number: int
    name: str
    category: Literal["u3e", "u3t", "v3"]  # noqa: F821


class MetadataDTO(BaseModel):
    """setting-client의 /metadata 엔드포인트의 Response에 해당하는 DTO.

    Attributes:
        line_id : 라인 번호
        equipment_name : 호기 이름
        equipment_id : 호기 번호
        number : 모터 번호
        name : 모터 이름
        category : 모터 카테고리.
    """

    equipment_id: int
    phase: str
    file_path: str
    motor_number: int
    line_id: int
    acq_time: datetime
    sampling_rate: int
    sample_size: int


class MetadataRMSDTO(MetadataDTO):
    """setting-client의 /metadata-rms 엔드포인트의 Response에 해당하는 DTO.

    Attributes:
        rms_u : rms_u 값
        rms_v : rms_v 값
        rms_w : rms_w 값.
    """

    rms_u: float
    rms_v: float
    rms_w: float


class MinioObjectDTO(BaseModel):
    """setting-client의 /raw-data 엔드포인트의 Response에 해당하는 DTO.

    Attributes:
        current : 전류 데이터, sampling_rate * 계측 시간만큼의 길이를 가짐.
        equipment_name : 호기 이름
        equipment_id : 호기 번호
        number : 모터 번호
        name : 모터 이름
        channel : 전류 채널(u,v,w).
    """

    current: list[float]
    equipment_name: str
    equipment_id: int
    number: int
    name: str
    channel: Literal["u", "v", "w"]  # noqa: F821


class FDCConfigDTO(BaseModel):
    """setting-client의 /fdc-config 엔드포인트의 Response에 해당하는 DTO.

    LGES FDC(Solace)와 연결되기 위해 setting-client를 통해 채워줘야하는 값들의 모음이며,
    LGES로부터 해당 값들을 받아야 사용가능.
    """

    topic: str
    host: str
    user_name: str
    client_name: str
    reconnect_attempts: int
    connect_retries_per_host: int
    sheet_path: str
    vpn: str
    password: str
    connect_attempts: int
    reconnect_interval: int
    message_interval: int
    featuredb_uri: PostgresDsn


class PLCModelRow(BaseModel):
    """setting-client의 /plc-model 엔드포인트의 Response에 해당하는 DTO.

    Attributes:
        id : plc id
        line_id : 라인 번호
        equipment_id : 호기 번호
        model : 배터리 모델 생산 번호(모노셀 ,하프셀)
        name : 모터 이름
        description : 배터리 모델 생산 번호에 대한 상세 설명.
    """

    id: int
    line_id: int
    equipment_id: int
    model: int
    name: str
    description: str


class ParameterSettingPLC(BaseModel):
    """setting-client의 "/parameter" 엔드포인트의 Response 중 model 파트에 해당하는 DTO.

    Attributes:
        model : 배터리 모델 생산 번호(모노셀 ,하프셀)
        name : 모터 이름
        description : 배터리 모델 생산 번호에 대한 상세 설명.
    """

    model: int
    name: str
    description: str


class ParameterSettingMotor(BaseModel):
    """setting-client의 "/parameter" 엔드포인트의 Response 중 motor 파트에 해당하는 DTO.

    Attributes:
        equipment_id : 호기 번호
        number : 모터 번호
        rated_current : 정격 전류
        pole : 폴 개수
        name : 모터 이름
        category : 모터 카테고리
        gear_ratio : 기어 비율
        max_current : 최대 전류.
    """

    equipment_id: int
    number: int
    rated_current: float
    pole: Optional[int] = 0
    name: str
    category: Literal["u3e", "u3t", "v3"]  # noqa: F821
    gear_ratio: Optional[float] = 0
    max_current: Optional[float] = 0


class ParameterSettingVariable(BaseModel):
    """setting-client의 "/parameter" 엔드포인트의 Response 중 parameter 파트에 해당 DTO.

    Attributes:
        moving_median_sample_number : 최종 진단 시 중위값을 구하기 위한 샘플의 개수.
    """

    moving_median_sample_number: int


class ParameterSettingUniformExternal(BaseModel):
    """setting-client의 /parameter 엔드포인트의 Response 중 parameter 파트에 해당 DTO.

    Attributes:
        supply_freq: 모터의 공급 주파수
        motor_bearing_moving_median_sample_number: 최종 진단 시 중위값을 구하기 위한
                                                    샘플의 개수(모터 베어링)
        motor_bearing_ball_diameter: 서보모터 베어링 볼 지름
        motor_bearing_ball_number: 서보모터 베어링 볼 개수
        motor_bearing_pitch_diameter: 서보모터 베어링 피치 지름
        external_bearing_moving_median_sample_number: 최종 진단 시 중위값을 구하기 위한
                                                        샘플의 개수(외부 베어링)
        external_bearing_ball_diameter: 외부베어링 베어링 볼 지름
        external_bearing_ball_number: 외부베어링 베어링 볼 개수
        external_bearing_pitch_diameter: 외부베어링 베어링 피치 지름
        external_bearing_number: 외부베어링 번호.
    """

    supply_freq: float
    motor_bearing_moving_median_sample_number: int
    motor_bearing_ball_diameter: float
    motor_bearing_ball_number: int
    motor_bearing_pitch_diameter: float

    external_bearing_moving_median_sample_number: int
    external_bearing_ball_diameter: float
    external_bearing_ball_number: int
    external_bearing_pitch_diameter: float
    external_bearing_number: int


class ParameterSettingUniformTension(ParameterSettingUniformExternal):
    """setting-client의 /parameter 엔드포인트의 Response 중 parameter 파트에 해당 DTO.

    텐션베어링에 해당하는 모터(u3t)는 기본적으로 u3e 모터의 자식클래스이기 때문에,
    상속받은 후 추가되는 항목만 더 적음.

    Attributes:
        tension_bearing_moving_median_sample_number: 최종 진단 시 중위값을 구하기 위한
                                                        샘플의 개수(텐션 베어링)
        tension_bearing_ball_diameter: 서보모터 베어링 볼 지름
        tension_bearing_ball_number: 서보모터 베어링 볼 개수
        tension_bearing_pitch_diameter: 서보모터 베어링 피치 지름
        tension_bearing_number: 텐션베어링 번호
        tension_bearing_feature_upper_warning: 텐션 베어링 고장 인자의 1차 상한
        tension_bearing_feature_upper_caution: 텐션 베어링 고장 인자의 2차 상한.
    """

    tension_bearing_moving_median_sample_number: int
    tension_bearing_ball_diameter: float
    tension_bearing_ball_number: int
    tension_bearing_pitch_diameter: float
    tension_bearing_number: int
    tension_bearing_feature_warning: float
    tension_bearing_feature_caution: float


class ParameterSettingUniformThreshold(BaseModel):
    """setting-client의 /parameter 엔드포인트의 Response 중 threshold 파트에 해당하는 DTO.

    Attributes:
        stator_feature_warning: 고정자 고장 인자의 2차 상한
        stator_feature_caution: 고정자 고장 인자의 1차 상한
        motor_bearing_feature_warning: 내부 베어링 고장 인자의 2차 하한
        motor_bearing_feature_caution: 내부 베어링 고장 인자의 1차 하한
        gear_feature_warning: 기어 샤프트 고장 인자의 2차 상한
        gear_feature_caution: 기어 샤프트 고장 인자의 1차 상한
        external_bearing_feature_warning: 외부 베어링 고장 인자의 2차 상한
        external_bearing_feature_caution: 외부 베어링 고장 인자의 1차 상한
        coupling_feature_warning: 커플링 고장 인자의 2차 상한
        coupling_feature_caution: 커플링 고장 인자의 1차 상한
        belt_feature_warning: 벨트 고장 인자의 2차 상한
        belt_feature_caution: 벨트 고장 인자의 1차 상한.
    """

    stator_feature_warning: float
    stator_feature_caution: float
    motor_bearing_feature_warning: float
    motor_bearing_feature_caution: float
    gear_shaft_feature_warning: float
    gear_shaft_feature_caution: float
    external_bearing_feature_warning: float
    external_bearing_feature_caution: float
    coupling_feature_warning: float
    coupling_feature_caution: float
    belt_feature_warning: float
    belt_feature_caution: float


class ParameterSettingVariableThreshold(BaseModel):
    """setting-client의 /parameter 엔드포인트의 Response 중 threshold 파트에 해당하는 DTO.

    Attributes:
        current_corr_lower_warning: 전류 유사도의 2차 하한
        current_corr_lower_caution: 전류 유사도의 1차 하한
        current_noise_rms_upper_warning: 전류 노이즈 rms의 2차 상한
        current_noise_rms_upper_caution: 전류 노이즈 rms의 1차 싱한
        current_noise_rms_lower_warning: 전류 노이즈 rms의 2차 하한
        current_noise_rms_lower_caution: 전류 노이즈 rms의 1차 하한.
    """

    current_corr_pvm_lower_warning: float
    current_corr_pvm_lower_caution: float
    current_noise_rms_upper_warning: float
    current_noise_rms_upper_caution: float
    current_noise_rms_lower_warning: float
    current_noise_rms_lower_caution: float


class ParameterSettingModel(BaseModel):
    """setting-client의 /parameter 엔드포인트의 Response에 해당하는 DTO.

    Attributes:
        model: 세팅 클라이언트에서 PLC 관련 부분 DTO
        motor: 세팅 클라이언트에서 모터 관련 부분 DTO
        parameter: 세팅 클라이언트에서 파라미터 관련 부분 DTO
        threshold: 세팅 클라이언트에서 threshold 관련 부분 DTO.
    """

    model: ParameterSettingPLC
    motor: ParameterSettingMotor
    parameter: Union[
        ParameterSettingUniformTension,
        ParameterSettingUniformExternal,
        ParameterSettingVariable,
    ]
    threshold: Union[
        ParameterSettingUniformThreshold,
        ParameterSettingVariableThreshold,
    ]

    def __getitem__(self, key: str) -> Any:
        """모델에서 속성 값을 검색합니다.

        Args:
            key (str): 속성의 이름입니다.
        반환합니다:
            Any: 속성의 값입니다.
        """
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        """모델에서 속성의 값을 설정합니다.

        Args:
            key (str): 속성의 이름입니다.
            value (Any): 속성에 설정할 값입니다.


        Returns:
            None.
        """
        return setattr(self, key, value)
