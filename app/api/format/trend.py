"""trend api 포맷팅을 위한 함수들.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
from collections import defaultdict
from datetime import datetime
from typing import Optional, Union

from api.crud.detail import MotorInfo
from api.crud.trend import (
    UniformExternalDiagnosis,
    UniformLoad,
    UniformOperating,
    UniformTensionDiagnosis,
    VariableDiagnosis,
    VariableLoad,
    VariableOperating,
)
from api.crud.util import get_matching_part, merge_list_of_dictionary
from api.format.detail import generate_motor_code, response_key_change
from db.feature.database import FeatureSessionLocal
from db.feature.model import (
    UniformSpeedExternalFeature,
    UniformSpeedTensionFeature,
    VariableSpeedPhase3Feature,
)


def format_load(
    motors_in_equipment: list[dict[str, Union[int, str]]],
    part_motor_number_dict: dict[str, tuple[int]],
    plc: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    """Load API 포매팅하는 함수.

    Args:
        motors_in_equipment(List[Dict[str, Union[int, str]]]): 현재 호기에 들어있는
                                                                전체 모터 정보 리스트
        part_motor_number_dict (Dict[str, Tuple[int]]): 호기별 특정 파트에
                                                        어떤 모터가 들어있는지에
                                                        대한 정보를 주는 딕셔너리
        plc (int): plc 모델 번호. PLC가 None인 경우, PLC Log 테이블에 들어있는
                    현재 호기의 가장 최신 모델
        start (datetime):기본값(None)인 경우 최근 2주 데이터 조회, 그외 경우 해당구간 조회
        end (datetime):기본값(None)인 경우 최근 2주 데이터 조회,그외 경우 해당구간 조회
    Example:
        >>> print(motors_in_equipment)
        [{
        "line_id": 1,
        "equipment_name": "13-1",
        "equipment_id": 1,
        "number": 1,
        "name": "ESWA_Auto_A_LAM_13_1_LAM_ESC_CenterElectrodeCuttingLinear_SVM_Axis_X",
        "category": "v3"
        }, ...}
        >>> print(part_motor_number_dict)
        {
            "pc": (4, 5, 6),
            "nc": (1, 2, 3),
            "lami": (7, 8, 12, 13),
            "fc": (9, 10, 11, 14),
        }.
    """
    response: dict = defaultdict(dict)
    for motor_dict in motors_in_equipment:
        motor_number = motor_dict["number"]
        str_mtr_id = "".join(("motor", str(motor_number)))
        motor_info = MotorInfo(motor_dict["equipment_id"], motor_number)
        motor_param = motor_info.read_motor_parameter()
        motor_param["motor_number"] = motor_param["number"]
        if plc is None:
            columns = ["equipment_id", "motor_number", "plc"]
            required_dict = {col: motor_param[col] for col in columns}
        else:
            columns = ["equipment_id", "motor_number"]
            required_dict = {col: motor_param[col] for col in columns} | {"plc": plc}

        if motor_dict["category"] == "u3e":
            ul = UniformLoad(required_dict, start, end)
            trend = [
                x._asdict()
                for x in ul.read_trend(FeatureSessionLocal, UniformSpeedExternalFeature)
            ]
        elif motor_dict["category"] == "u3t":
            ut = UniformLoad(required_dict, start, end)
            trend = [
                x._asdict()
                for x in ut.read_trend(FeatureSessionLocal, UniformSpeedTensionFeature)
            ]
        elif motor_dict["category"] == "v3":
            vl = VariableLoad(required_dict, start, end)
            trend = [
                x._asdict()
                for x in vl.read_trend(FeatureSessionLocal, VariableSpeedPhase3Feature)
            ]
        merged_trend = merge_list_of_dictionary(trend)
        response[str_mtr_id] = merged_trend | {
            "part": get_matching_part(part_motor_number_dict, motor_number),
            "name": generate_motor_code(motor_dict["name"]),
            "label": motor_dict["category"],
        }

        response[str_mtr_id] = response_key_change(response[str_mtr_id])
    return response


def format_operating(
    motors_in_equipment: list[dict[str, Union[int, str]]],
    part_motor_number_dict: dict[str, tuple[int]],
    plc: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    """Operating API 포매팅하는 함수.

    Args:
        motors_in_equipment(List[Dict[str, Union[int, str]]]): 현재 호기에 들어있는
                                                                전체 모터 정보 리스트
        part_motor_number_dict (Dict[str, Tuple[int]]): 호기별 특정 파트에
                                                        어떤 모터가 들어있는지에
                                                        대한 정보를 주는 딕셔너리
        plc (int): plc 모델 번호. PLC가 None인 경우, PLC Log 테이블에 들어있는
                    현재 호기의 가장 최신 모델
        start (datetime):기본값(None)인 경우 최근 2주 데이터 조회, 그외 경우 해당구간 조회
        end (datetime):기본값(None)인 경우 최근 2주 데이터 조회,그외 경우 해당구간 조회
    Example:
        >>> print(motors_in_equipment)
        [{
        "line_id": 1,
        "equipment_name": "13-1",
        "equipment_id": 1,
        "number": 1,
        "name": "ESWA_Auto_A_LAM_13_1_LAM_ESC_CenterElectrodeCuttingLinear_SVM_Axis_X",
        "category": "v3"
        }, ...}
        >>> print(part_motor_number_dict)
        {
            "pc": (4, 5, 6),
            "nc": (1, 2, 3),
            "lami": (7, 8, 12, 13),
            "fc": (9, 10, 11, 14),
        }.
    """
    response: dict = defaultdict(dict)
    for motor_dict in motors_in_equipment:
        motor_number = motor_dict["number"]
        str_mtr_id = "".join(("motor", str(motor_number)))
        motor_info = MotorInfo(motor_dict["equipment_id"], motor_number)
        motor_param = motor_info.read_motor_parameter()
        motor_param["motor_number"] = motor_param["number"]
        if plc is None:
            columns = ["equipment_id", "motor_number", "plc"]
            required_dict = {col: motor_param[col] for col in columns}
        else:
            columns = ["equipment_id", "motor_number"]
            required_dict = {col: motor_param[col] for col in columns} | {"plc": plc}

        if motor_dict["category"] == "u3e":
            ul = UniformOperating(required_dict, start, end)
            trend = [
                x._asdict()
                for x in ul.read_trend(FeatureSessionLocal, UniformSpeedExternalFeature)
            ]
        elif motor_dict["category"] == "u3t":
            ut = UniformOperating(required_dict, start, end)
            trend = [
                x._asdict()
                for x in ut.read_trend(FeatureSessionLocal, UniformSpeedTensionFeature)
            ]
        elif motor_dict["category"] == "v3":
            vl = VariableOperating(required_dict, start, end)
            trend = [
                x._asdict()
                for x in vl.read_trend(FeatureSessionLocal, VariableSpeedPhase3Feature)
            ]
        merged_trend = merge_list_of_dictionary(trend)
        response[str_mtr_id] = merged_trend | {
            "part": get_matching_part(part_motor_number_dict, motor_number),
            "name": generate_motor_code(motor_dict["name"]),
            "label": motor_dict["category"],
        }

        response[str_mtr_id] = response_key_change(response[str_mtr_id])
    return response


def format_variable_diagnosis(
    motors_in_equipment: list[dict[str, Union[int, str]]],
    part_motor_number_dict: dict[str, tuple[int]],
    plc: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    """Variable diagnosis API 포매팅하는 함수.

    Args:
        motors_in_equipment(List[Dict[str, Union[int, str]]]): 현재 호기에 들어있는
                                                                전체 모터 정보 리스트
        part_motor_number_dict (Dict[str, Tuple[int]]): 호기별 특정 파트에
                                                        어떤 모터가 들어있는지에
                                                        대한 정보를 주는 딕셔너리
        plc (int): plc 모델 번호. PLC가 None인 경우, PLC Log 테이블에 들어있는
                    현재 호기의 가장 최신 모델
        start (datetime):기본값(None)인 경우 최근 2주 데이터 조회, 그외 경우 해당구간 조회
        end (datetime):기본값(None)인 경우 최근 2주 데이터 조회,그외 경우 해당구간 조회
    Example:
        >>> print(motors_in_equipment)
        [{
        "line_id": 1,
        "equipment_name": "13-1",
        "equipment_id": 1,
        "number": 1,
        "name": "ESWA_Auto_A_LAM_13_1_LAM_ESC_CenterElectrodeCuttingLinear_SVM_Axis_X",
        "category": "v3"
        }, ...}
        >>> print(part_motor_number_dict)
        {
            "pc": (4, 5, 6),
            "nc": (1, 2, 3),
            "lami": (7, 8, 12, 13),
            "fc": (9, 10, 11, 14),
        }.
    """
    response: dict = defaultdict(dict)
    for motor_dict in motors_in_equipment:
        if motor_dict["category"] == "v3":
            motor_number = motor_dict["number"]
            str_mtr_id = "".join(("motor", str(motor_number)))
            motor_info = MotorInfo(motor_dict["equipment_id"], motor_number)
            motor_param = motor_info.read_motor_parameter()
            motor_param["motor_number"] = motor_param["number"]
            if plc is None:
                columns = ["equipment_id", "motor_number", "plc"]
                required_dict = {col: motor_param[col] for col in columns}
            else:
                columns = ["equipment_id", "motor_number"]
                required_dict = {col: motor_param[col] for col in columns} | {
                    "plc": plc,
                }
            vd = VariableDiagnosis(required_dict, start, end)
            trend = [
                x._asdict()
                for x in vd.read_trend(FeatureSessionLocal, VariableSpeedPhase3Feature)
            ]
            merged_trend = merge_list_of_dictionary(trend)
            response[str_mtr_id] = merged_trend | {
                "part": get_matching_part(part_motor_number_dict, motor_number),
                "name": generate_motor_code(motor_dict["name"]),
                "label": "v3",
            }
            response[str_mtr_id] = response_key_change(response[str_mtr_id])

    return response


def format_uniform_diagnosis(
    motors_in_equipment: list[dict[str, Union[int, str]]],
    part_motor_number_dict: dict[str, tuple[int]],
    plc: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    """Uniform diagnosis API 포매팅하는 함수.

    Args:
        motors_in_equipment(List[Dict[str, Union[int, str]]]): 현재 호기에 들어있는
                                                                전체 모터 정보 리스트
        part_motor_number_dict (Dict[str, Tuple[int]]): 호기별 특정 파트에
                                                        어떤 모터가 들어있는지에
                                                        대한 정보를 주는 딕셔너리
        plc (int): plc 모델 번호. PLC가 None인 경우, PLC Log 테이블에 들어있는
                    현재 호기의 가장 최신 모델
        start (datetime):기본값(None)인 경우 최근 2주 데이터 조회, 그외 경우 해당구간 조회
        end (datetime):기본값(None)인 경우 최근 2주 데이터 조회,그외 경우 해당구간 조회
    Example:
        >>> print(motors_in_equipment)
        [{
        "line_id": 1,
        "equipment_name": "13-1",
        "equipment_id": 1,
        "number": 1,
        "name": "ESWA_Auto_A_LAM_13_1_LAM_ESC_CenterElectrodeCuttingLinear_SVM_Axis_X",
        "category": "v3"
        }, ...}
        >>> print(part_motor_number_dict)
        {
            "pc": (4, 5, 6),
            "nc": (1, 2, 3),
            "lami": (7, 8, 12, 13),
            "fc": (9, 10, 11, 14),
        }.
    """
    response: dict = defaultdict(dict)
    for motor_dict in motors_in_equipment:
        motor_number = motor_dict["number"]
        str_mtr_id = "".join(("motor", str(motor_number)))
        motor_info = MotorInfo(motor_dict["equipment_id"], motor_number)
        motor_param = motor_info.read_motor_parameter()
        motor_param["motor_number"] = motor_param["number"]
        if plc is None:
            columns = ["equipment_id", "motor_number", "plc"]
            required_dict = {col: motor_param[col] for col in columns}
        else:
            columns = ["equipment_id", "motor_number"]
            required_dict = {col: motor_param[col] for col in columns} | {"plc": plc}

        if motor_dict["category"] == "u3e":
            ud = UniformExternalDiagnosis(required_dict, start, end)
            trend = [
                x._asdict()
                for x in ud.read_trend(FeatureSessionLocal, UniformSpeedExternalFeature)
            ]
            merged_trend = merge_list_of_dictionary(trend)
            response[str_mtr_id] = merged_trend | {
                "part": get_matching_part(part_motor_number_dict, motor_number),
                "name": generate_motor_code(motor_dict["name"]),
                "label": motor_dict["category"],
            }
        elif motor_dict["category"] == "u3t":
            ut = UniformTensionDiagnosis(required_dict, start, end)
            trend = [
                x._asdict()
                for x in ut.read_trend(FeatureSessionLocal, UniformSpeedTensionFeature)
            ]
            merged_trend = merge_list_of_dictionary(trend)
            response[str_mtr_id] = merged_trend | {
                "part": get_matching_part(part_motor_number_dict, motor_number),
                "name": generate_motor_code(motor_dict["name"]),
                "label": motor_dict["category"],
            }
        else:
            continue

        response[str_mtr_id] = response_key_change(response[str_mtr_id])

    return response
