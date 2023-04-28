"""util 함수들 모음.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
from typing import Any, Optional, TypeVar, Union

from sqlalchemy.engine.row import Row
from util.exception import EmptyKeyListError

T = TypeVar("T")


def extract_threshold(motor_param: dict, category: str) -> Optional[dict]:
    """motor_param이 주어지면 threshold를 특정 포맷에 맞게 리턴해주는 함수.

    Args:
        motor_param (dict): 모터 파라미터를 의미.
        category (str): 모터 카테고리를 의미
    Returns:
        dict
    """
    threshold_dict = {
        key: value
        for key, value in motor_param.items()
        if value is not None and (key.endswith("_warning") or key.endswith("_caution"))
    }

    if category == "v3":
        return {
            "threshold": {
                "lges.feature.health.correlation": [
                    {
                        "title": "lges.common.lower.caution",
                        "value": threshold_dict["current_corr_pvm_lower_caution"],
                    },
                    {
                        "title": "lges.common.lower.warning",
                        "value": threshold_dict["current_corr_pvm_lower_warning"],
                    },
                ],
                "lges.feature.health.noise": [
                    {
                        "title": "lges.common.lower.caution",
                        "value": threshold_dict["current_noise_rms_lower_caution"],
                    },
                    {
                        "title": "lges.common.lower.warning",
                        "value": threshold_dict["current_noise_rms_lower_warning"],
                    },
                    {
                        "title": "lges.common.upper.caution",
                        "value": threshold_dict["current_noise_rms_upper_caution"],
                    },
                    {
                        "title": "lges.common.upper.warning",
                        "value": threshold_dict["current_noise_rms_upper_warning"],
                    },
                ],
            },
        }
    elif category == "u3e":
        return {
            "threshold": {
                "lges.feature.health.motorStator": [
                    {
                        "title": "lges.common.upper.caution",
                        "value": threshold_dict["stator_feature_caution"],
                    },
                    {
                        "title": "lges.common.upper.warning",
                        "value": threshold_dict["stator_feature_warning"],
                    },
                ],
                "lges.feature.health.motorBearing": [
                    {
                        "title": "lges.common.upper.caution",
                        "value": threshold_dict["motor_bearing_feature_caution"],
                    },
                    {
                        "title": "lges.common.upper.warning",
                        "value": threshold_dict["motor_bearing_feature_warning"],
                    },
                ],
                "lges.feature.health.gearbox": [
                    {
                        "title": "lges.common.upper.caution",
                        "value": threshold_dict["gear_shaft_feature_caution"],
                    },
                    {
                        "title": "lges.common.upper.warning",
                        "value": threshold_dict["gear_shaft_feature_warning"],
                    },
                ],
                "lges.feature.health.externalBearing": [
                    {
                        "title": "lges.common.upper.caution",
                        "value": threshold_dict["external_bearing_feature_caution"],
                    },
                    {
                        "title": "lges.common.upper.warning",
                        "value": threshold_dict["external_bearing_feature_warning"],
                    },
                ],
                "lges.feature.health.coupling": [
                    {
                        "title": "lges.common.upper.caution",
                        "value": threshold_dict["coupling_feature_caution"],
                    },
                    {
                        "title": "lges.common.upper.warning",
                        "value": threshold_dict["coupling_feature_warning"],
                    },
                ],
                "lges.feature.health.belt": [
                    {
                        "title": "lges.common.upper.caution",
                        "value": threshold_dict["belt_feature_caution"],
                    },
                    {
                        "title": "lges.common.upper.warning",
                        "value": threshold_dict["belt_feature_warning"],
                    },
                ],
            },
        }
    elif category == "u3t":
        return {
            "threshold": {
                "lges.feature.health.motorStator": [
                    {
                        "title": "lges.common.upper.caution",
                        "value": threshold_dict["stator_feature_caution"],
                    },
                    {
                        "title": "lges.common.upper.warning",
                        "value": threshold_dict["stator_feature_warning"],
                    },
                ],
                "lges.feature.health.motorBearing": [
                    {
                        "title": "lges.common.upper.caution",
                        "value": threshold_dict["motor_bearing_feature_caution"],
                    },
                    {
                        "title": "lges.common.upper.warning",
                        "value": threshold_dict["motor_bearing_feature_warning"],
                    },
                ],
                "lges.feature.health.gearbox": [
                    {
                        "title": "lges.common.upper.caution",
                        "value": threshold_dict["gear_shaft_feature_caution"],
                    },
                    {
                        "title": "lges.common.upper.warning",
                        "value": threshold_dict["gear_shaft_feature_warning"],
                    },
                ],
                "lges.feature.health.externalBearing": [
                    {
                        "title": "lges.common.upper.caution",
                        "value": threshold_dict["external_bearing_feature_caution"],
                    },
                    {
                        "title": "lges.common.upper.warning",
                        "value": threshold_dict["external_bearing_feature_warning"],
                    },
                ],
                "lges.feature.health.coupling": [
                    {
                        "title": "lges.common.upper.caution",
                        "value": threshold_dict["coupling_feature_caution"],
                    },
                    {
                        "title": "lges.common.upper.warning",
                        "value": threshold_dict["coupling_feature_warning"],
                    },
                ],
                "lges.feature.health.belt": [
                    {
                        "title": "lges.common.upper.caution",
                        "value": threshold_dict["belt_feature_caution"],
                    },
                    {
                        "title": "lges.common.upper.warning",
                        "value": threshold_dict["belt_feature_warning"],
                    },
                ],
                "lges.feature.health.externalTensionBearing": [
                    {
                        "title": "lges.common.upper.caution",
                        "value": threshold_dict["tension_bearing_feature_caution"],
                    },
                    {
                        "title": "lges.common.upper.warning",
                        "value": threshold_dict["tension_bearing_feature_warning"],
                    },
                ],
            },
        }
    return None


def row_to_dict(
    query_results: Union[list[Row], list[T]],
) -> list[dict[str, dict[str, Any]]]:
    """Convert Rows in list or sqlalchemy class object defined by user to dict.

    Args:
        query_results (Union[list[Row], list[Generic[T]]]):
            session.query(T).all()의 결과
    Returns:
        list[dict[str, dict[str, Any]]].
    """
    # query_results 타입이 list[Row]인 경우
    if isinstance(query_results[0], Row):
        object_dict_list: list[dict] = [x._asdict() for x in query_results]

        return [
            {
                key: delete_sa_state(value.__dict__)
                if hasattr(value, "__dict__")
                else value
                for key, value in object_dict.items()
            }
            for object_dict in object_dict_list
        ]

    # Row 타입이 아닌 경우(list[Generic[T]])
    else:

        return [
            delete_sa_state(query_result.__dict__) for query_result in query_results
        ]


def delete_sa_state(query_result: dict) -> dict:
    """쿼리 결과 중에 _sa_instance_state 부분을 제거해주는 함수.

    Args:
        query_result (dict): 쿼리 결과(row 1개를 의미)

    Returns:
        dict
    """
    return {
        key: value for key, value in query_result.items() if key != "_sa_instance_state"
    }


def extract_need_key(x: dict, needed_keys: list[str]) -> dict:
    """딕셔너리 중 필요한 키만 반환.

    Args:
        x (dict): 딕셔너리 객체
        needed_keys (list[str]): 필요한 키의 리스트
    Returns:
        dict
    """
    if not needed_keys:
        raise EmptyKeyListError

    return {key: value for key, value in x.items() if key in needed_keys}


def change_key_name(x: dict, org_key: str, new_key: str) -> dict:
    """딕셔너리 특정 키-밸류 값을 새로운 키-밸류로 생성하고 싶을 경우 사용되는 함수.

    Args:
        x (dict): 딕셔너리 객체
        org_key (str): 원래 키
        new_key (str): 새로운 키이며, 원래 키의 밸류값을 가짐.


    Returns:
        dict
    """
    if org_key not in x:
        raise KeyError("org_key가 존재하지 않습니다.")
    x[new_key] = x.pop(org_key)
    return x


def load_columns(obj: type[T]) -> list[str]:
    """ORM 객체의 column를 모두 불러오는 함수.

    Args:
        obj (Generic[T]): ORM 객체
    Returns:
        list[str]
    """
    return [
        attr
        for attr in dir(obj)
        if not attr.startswith("_") and attr not in ["metadata", "registry"]
    ]


def delete_key(_dict: dict, popped_columns: list[str]) -> dict:
    """쿼리 결과 중에 _sa_instance_state 부분을 제거해주는 함수.

    Args:
        _dict (dict): 딕셔너리 객체
        popped_columns (list[str]): 제거하고 싶은 키의 리스트
    Returns:
        dict
    """
    for col in popped_columns:
        _dict.pop(col, None)
    return _dict
