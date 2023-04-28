"""setting-client api 포맷팅을 위한 함수들.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
from datetime import datetime
from typing import Any

from schemas.setting import MetadataDTO


def matching_metadata_and_trigger(
    metadata_query_results: list[MetadataDTO],
    trigger_query_results: list[dict[str, float]],
) -> list[dict[str, Any]]:
    """metadata와 trigger가 같은 개수만큼 들어있기 때문에 매칭.(legacy).

    추후 metadata-rms 기능을 개발하고 싶은 경우, 본 함수를 사용하는 것보다는
    trigger 테이블에서 rms_v, rms_w를 만드는 것이 바람직함.
    """
    n = 3
    metadata_query_results = [
        metadata_query_results[i * n : (i + 1) * n]
        for i in range((len(metadata_query_results) + n - 1) // n)
    ]

    for metadata_three_row, trigger_row in zip(
        metadata_query_results,
        trigger_query_results,
    ):
        metadata_acq_time = metadata_three_row[0]["acq_time"]
        trigger_acq_time = trigger_row["acq_time"]

        for metadata_row in metadata_three_row:

            if metadata_acq_time == trigger_acq_time and metadata_row["phase"] == "u":
                metadata_row.update(
                    {"rms_u": round(trigger_row["rms_u"], 6), "rms_v": 0, "rms_w": 0},
                )
            else:
                metadata_row.update({"rms_u": 0, "rms_v": 0, "rms_w": 0})

    def flatten(nested_list: list) -> list:
        """Nested list를 flatten 하는 함수.

        출처 : https://stackoverflow.com/questions/952914/how-do-i-make-a-flat-list-out-of-a-list-of-lists.
        """
        return [item for sublist in nested_list for item in sublist]

    return flatten(metadata_query_results)


def format_motor_bearing(body: dict, aware_now: datetime) -> dict:
    """세팅 파라미터에서 파라미터를 세팅할 때 모터 베어링 관련 인자 관련 포맷을 설정한 것.

    Args:
        body (dict): 세팅 클라이언트에서 파라미터 세팅할 때, 필요한 전체 body를 의미함.
                    schemas.setting.ParameterSettingModel참고
        aware_now (datetime): UTC 보정 시간.


    Returns:
        dict
    """
    required_dict = generate_required_dict(body, aware_now)
    motor_bearing = {
        key: body["parameter"][key]
        for key in body["parameter"]
        if key.startswith("motor_bearing")
    } | {"supply_freq": body["parameter"]["supply_freq"]}

    motor_bearing["moving_median_sample_number"] = motor_bearing.pop(
        "motor_bearing_moving_median_sample_number",
    )

    return motor_bearing | required_dict


def format_external_bearing(body: dict, aware_now: datetime) -> dict:
    """세팅클라이언트 파라미터 세팅을 위한 구동부 베어링 인자 관련 포맷을 설정한 것.

    Args:
        body (dict): 세팅 클라이언트에서 파라미터 세팅할 때, 필요한 전체 body를 의미함.
                    schemas.setting.ParameterSettingModel참고
        aware_now (datetime): UTC 보정 시간.


    Returns:
        dict
    """
    required_dict = generate_required_dict(body, aware_now)
    external_bearing = {
        key: body["parameter"][key]
        for key in body["parameter"]
        if key.startswith("external_bearing")
    } | {
        key: body["threshold"][key]
        for key in body["threshold"]
        if key.startswith("external_bearing")
    }
    external_bearing["moving_median_sample_number"] = external_bearing.pop(
        "external_bearing_moving_median_sample_number",
    )
    external_bearing["bearing_number"] = external_bearing.pop("external_bearing_number")
    return external_bearing | required_dict


def format_uniform_threshold(body: dict, aware_now: datetime) -> dict:
    """세팅클라이언트 파라미터 세팅을 위한 uniform threshold 인자 관련 포맷을 설정한 것.

    Args:
        body (dict): 세팅 클라이언트에서 파라미터 세팅할 때, 필요한 전체 body를 의미함.
                    schemas.setting.ParameterSettingModel참고
        aware_now (datetime): UTC 보정 시간.


    Returns:
        dict
    """
    required_dict = generate_required_dict(body, aware_now)
    uniform_threshold = {
        key: body["threshold"][key]
        for key in body["threshold"]
        if not key.startswith("external_bearing")
        and not key.startswith("tension_bearing")
    }
    return uniform_threshold | required_dict


def format_tension_bearing(body: dict, aware_now: datetime) -> dict:
    """세팅클라이언트 파라미터 세팅을 위한 구동부텐션 베어링 인자 관련 포맷을 설정한 것.

    Args:
        body (dict): 세팅 클라이언트에서 파라미터 세팅할 때, 필요한 전체 body를 의미함.
                    schemas.setting.ParameterSettingModel참고
        aware_now (datetime): UTC 보정 시간.


    Returns:
        dict
    """
    required_dict = generate_required_dict(body, aware_now)
    tension_bearing = {
        key: body["parameter"][key]
        for key in body["parameter"]
        if key.startswith("tension_bearing")
    } | {
        key: body["threshold"][key]
        for key in body["threshold"]
        if key.startswith("tension_bearing")
    }
    tension_bearing["moving_median_sample_number"] = tension_bearing.pop(
        "tension_bearing_moving_median_sample_number",
    )
    tension_bearing["bearing_number"] = tension_bearing.pop("tension_bearing_number")
    return tension_bearing | required_dict


def generate_required_dict(body: dict, aware_now: datetime) -> dict:
    """세팅클라이언트 파라미터 세팅을 위한 CRUD 필수 인자 관련 포맷을 설정한 것.

    Args:
        body (dict): 세팅 클라이언트에서 파라미터 세팅할 때, 필요한 전체 body를 의미함.
                    schemas.setting.ParameterSettingModel참고
        aware_now (datetime): UTC 보정 시간.


    Returns:
        dict
    """
    required_dict = {
        "equipment_id": body["motor"]["equipment_id"],
        "motor_number": body["motor"]["number"],
        "plc": body["model"]["model"],
        "updated_time": aware_now,
    }
    return required_dict
