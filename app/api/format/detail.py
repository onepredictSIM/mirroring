"""상세페이지 api 포맷팅을 위한 함수들.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
from collections import defaultdict
from datetime import datetime
from typing import Optional

from api.crud.detail import (
    MotorInfo,
    UniformExternalDetailFeature,
    UniformTensionDetailFeature,
    VariablePhase3DetailFeature,
)
from api.crud.util import dt_to_unix
from db.feature.database import FeatureSessionLocal
from db.feature.model import (
    UniformSpeedExternalFeature,
    UniformSpeedTensionFeature,
    VariableSpeedPhase3Feature,
)
from fastapi import HTTPException
from util.utils import delete_key, extract_threshold


def format_detail_feature_trend(features: list[dict]) -> dict:
    """모든 상세페이지(e.g. XX커팅부)에서 threshold를 제외한 값들을 불러오는 함수.

    (트렌드 그릴 때 필요한 feature, 기본 진단 정보(diagnosis 등).

    Note: 특정 구간에 조회된 데이터가 전혀 없을 경우 에러 발생
        -> #TODO 만약 특정 구간에 조회된 데이터가 전혀없을 경우
            값을 0으로만 보내주는 방향으로 생각중.

    1. features가 빈 리스트인 경우, 501 status code 설정.
    2. 스칼라값을 갖는 키들(equipment_id, motor_number, plc, diagnosis 등)
        을 제외하고는 리스트에 담음.
    3. 그 외의 값들은 주어진 features에서 가장 마지막 feature만 담음(최신 정보).
    """
    if not features:
        raise HTTPException(
            status_code=404,
            detail=("해당 날짜 구간에 feature가 존재하지 않습니다."),
        )

    zero_dimension_keys = ("equipment_id", "motor_number", "plc")
    response: dict = defaultdict(list)

    for feature in features:
        for key, value in feature.items():
            if key not in zero_dimension_keys and not (key.endswith("diagnosis")):
                if key == "acq_time":
                    response[key].append(dt_to_unix(value))
                else:
                    response[key].append(value)

    zero_dimension_dict = {
        key: value
        for key, value in features[-1].items()
        if key in zero_dimension_keys or key.endswith("diagnosis")
    }

    return response | zero_dimension_dict


def generate_motor_code(motor_name: str) -> str:
    """프론트엔드와 협의한 모터 이름 코드로 변경하기 위해 사용되는 함수.

    Args:
        motor_name (str):LGES측에서 제공 및 DB에 들어있는 모터 이름
    Example:
        >>> print(motor_name)
        "ESWA_Auto_A_LAM_13_1_LAM_ESC_CenterElectrodeCuttingLinear_SVM_Axis_X",.
    """
    parsed_motor_name = motor_name.split("_")[-4]
    first_lower_case_motor_name = parsed_motor_name[0].lower() + parsed_motor_name[1:]
    return ".".join(("lges", "motors", first_lower_case_motor_name))


def parse_for_detail_init(motor_param: dict) -> dict:
    """detail_init을 위해 motor_param을 파싱하는 함수.

    Args:
        motor_param (dict): MotorInfo 객체의 read_motor_parameter 리턴 값.
    """
    required_key_list = ["equipment_id", "number", "name", "plc", "category"]
    parsed_motor_param = {key: motor_param[key] for key in required_key_list}
    parsed_motor_param["motor_number"] = parsed_motor_param.pop("number")
    parsed_motor_param["name"] = generate_motor_code(parsed_motor_param["name"])
    return parsed_motor_param


def response_key_change(response: dict) -> dict:
    """Response key를 변경해주는 함수."""
    match_table = {
        "avg_load": "lges.feature.operating.avgLoad",
        "avg_load_ratio": "lges.feature.operating.avgLoadRatio",
        "peak_load": "lges.feature.operating.peakLoad",
        "peak_load_ratio": "lges.feature.operating.peakLoadRatio",
        "cutting_interval": "lges.feature.operating.cuttingInterval",
        "current_corr_pvm_median": "lges.feature.health.correlation",
        "current_noise_rms_pvm_median": "lges.feature.health.noise",
        "final_diagnosis": "lges.feature.health.final_diagnosis",
        "current_corr_pvm_diagnosis": "lges.feature.health.correlation_diagnosis",
        "current_noise_rms_pvm_diagnosis": "lges.feature.health.noise_diagnosis",
        "current_corr_pvm_lower_warning": "lges.feature.health.corr_lower_warning",
        "current_corr_pvm_lower_caution": "lges.feature.health.corr_lower_caution",
        "current_noise_rms_upper_warning": "lges.feature.health.noise_upper_warning",
        "current_noise_rms_upper_caution": "lges.feature.health.noise_upper_caution",
        "current_noise_rms_lower_warning": "lges.feature.health.noise_lower_warning",
        "current_noise_rms_lower_caution": "lges.feature.health.noise_lower_caution",
        "rolling_load": "lges.feature.operating.rollingLoad",
        "rolling_load_ratio": "lges.feature.operating.rollingLoadRatio",
        "signal_noise_ratio": "lges.feature.operating.SNR",
        "winding_supply_freq_amp_unbalance_ratio_median": "lges.feature.health.motorStator",  # noqa: E501
        "motor_bpfi_1x_median": "lges.feature.health.motorBearing",
        "gearbox_rotation_freq_amp_median": "lges.feature.health.gearbox",
        "external_bpfo_1x_median": "lges.feature.health.externalBearing",
        "belt_kurtosis_max_median": "lges.feature.health.belt",
        "stator_diagnosis": "lges.feature.health.stator_diagnosis",
        "motor_bearing_diagnosis": "lges.feature.health.motor_bearing_diagnosis",
        "gear_shaft_diagnosis": "lges.feature.health.gear_shaft_diagnosis",
        "external_bearing_diagnosis": "lges.feature.health.external_bearing_diagnosis",
        "coupling_diagnosis": "lges.feature.health.coupling_diagnosis",
        "belt_diagnosis": "lges.feature.health.belt_diagnosis",
        "stator_feature_warning": "lges.feature.health.stator_warning",
        "stator_feature_caution": "lges.feature.health.stator_caution",
        "motor_bearing_feature_warning": "lges.feature.health.motor_bearing_warning",
        "motor_bearing_feature_caution": "lges.feature.health.motor_bearing_caution",
        "gear_shaft_feature_warning": "lges.feature.health.gear_shaft_warning",
        "gear_shaft_feature_caution": "lges.feature.health.gear_shaft_caution",
        "external_bearing_feature_warning": "lges.feature.health.external_bearing_warning",  # noqa: E501
        "external_bearing_feature_caution": "lges.feature.health.external_bearing_caution",  # noqa: E501
        "coupling_feature_warning": "lges.feature.health.coupling_warning",
        "coupling_feature_caution": "lges.feature.health.coupling_caution",
        "belt_feature_warning": "lges.feature.health.belt_warning",
        "belt_feature_caution": "lges.feature.health.belt_caution",
        "tension_bpfo_1x_median": "lges.feature.health.externalTensionBearing",
        "external_main_bearing_diagnosis": "lges.feature.health.external_main_bearing_diagnosis",  # noqa: E501
        "external_tension_bearing_diagnosis": "lges.feature.health.external_tension_bearing_diagnosis",  # noqa: E501
        "tension_bearing_feature_warning": "lges.feature.health.tension_bearing_warning",
        "tension_bearing_feature_caution": "lges.feature.health.tension_bearing_caution",
        "coupling_supply_freq_amp_median": "lges.feature.health.coupling",
    }

    new_response: dict = defaultdict()

    for key, value in response.items():
        if key in match_table:
            new_response[match_table[key]] = response[key]
        else:
            new_response[key] = value

    return new_response


def format_detail(
    equipment_id: int,
    motor_number: int,
    plc: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    """모든 상세페이지(e.g. XX커팅부)에서 response를 위해 사용되는 함수.

    1. 호기 번호와 모터 정보를 이용하여 현재 모터 상태 및 스펙을 불러온다(MotorInfo)
    2. plc 값 설정 여부에 따라 다른 plc를 불러온다.
    3. 모터 카테고리 별로 매칭된 table 이름과 crud class를 불러와서
        해당 구간에 대한 feature를 불러온다.
    """
    category_feature_class = {
        "u3e": {
            "table_name": UniformSpeedExternalFeature,
            "class": UniformExternalDetailFeature,
        },
        "u3t": {
            "table_name": UniformSpeedTensionFeature,
            "class": UniformTensionDetailFeature,
        },
        "v3": {
            "table_name": VariableSpeedPhase3Feature,
            "class": VariablePhase3DetailFeature,
        },
    }

    motor_info = MotorInfo(equipment_id, motor_number)
    motor_param = motor_info.read_motor_parameter()
    category = motor_param["category"]
    motor_param["motor_number"] = motor_param["number"]

    if plc is None:
        columns = ["equipment_id", "motor_number", "plc"]
        required_dict = {col: motor_param[col] for col in columns}
    else:
        columns = ["equipment_id", "motor_number"]
        required_dict = {col: motor_param[col] for col in columns} | {"plc": plc}

    unnecessary_key_list = ("template_u", "template_v", "template_w")
    motor_param = delete_key(motor_param, unnecessary_key_list)

    detail_feature_instance = category_feature_class[category]["class"](
        required_dict,
        start,
        end,
    )
    features = detail_feature_instance.read_detail(
        FeatureSessionLocal,
        category_feature_class[category]["table_name"],
    )
    # 원래 row_to_dict로 돌아야하나, 현재 row_to_dict함수를 넣었을 때
    # 안도는 경우가 발생하여 임시로 사용하는 코드 라인
    features = [x._asdict() for x in features]
    return (
        format_detail_feature_trend(features)
        | extract_threshold(motor_param, category)
        | {"category": category}
        | {"name": generate_motor_code(motor_param["name"])}
    )
