"""dashboard api 포맷팅을 위한 함수들.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
import re
from collections import defaultdict
from typing import Optional, Union

from api.crud.dashboard import (
    TriggerDashboard,
    UniformExternalDashboard,
    UniformTensionDashboard,
    VariableDashboard,
    get_supply_freq,
)
from api.crud.util import get_matching_part
from api.format.detail import generate_motor_code, response_key_change
from db.feature.database import FeatureSessionLocal
from db.feature.model import (
    Trigger,
    UniformSpeedExternalFeature,
    UniformSpeedTensionFeature,
    VariableSpeedPhase3Feature,
)
from fastapi import HTTPException
from util.func import dt_to_unix
from util.utils import extract_need_key


def format_dashboard(
    motors_in_equipment: list[dict[str, Union[int, str]]],
    part_motor_number_dict: dict[str, tuple[int]],
    plc: Optional[int] = None,
) -> dict[str, dict[str, Union[int, float, str]]]:
    """대쉬보드 API 포매팅하는 함수.

    Args:
        motors_in_equipment(List[Dict[str, Union[int, str]]]): 현재 호기에 들어있는
                                                                전체 모터 정보 리스트
        part_motor_number_dict (Dict[str, Tuple[int]]): 호기별 특정 파트에
                                                        어떤 모터가 들어있는지에
                                                        대한 정보를 주는 딕셔너리
        plc (int): plc 모델 번호. PLC가 None인 경우, PLC Log 테이블에 들어있는
                    현재 호기의 가장 최신 모델
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
        equipment_id, motor_number = motor_dict["equipment_id"], motor_dict["number"]
        str_mtr_id = "".join(("motor", str(motor_number)))

        def load_dashboard(str_mtr_id: str, category: str, plc: Optional[int]) -> dict:
            category_matching_dict = {
                "u3e": {
                    "dashboard": UniformExternalDashboard,
                    "orm_cls": UniformSpeedExternalFeature,
                },
                "u3t": {
                    "dashboard": UniformTensionDashboard,
                    "orm_cls": UniformSpeedTensionFeature,
                },
                "v3": {
                    "dashboard": VariableDashboard,
                    "orm_cls": VariableSpeedPhase3Feature,
                },
            }
            ud = category_matching_dict[category]["dashboard"](
                equipment_id,
                motor_number,
                plc,
            )
            try:
                [dashboard] = ud.read_dashboard(
                    FeatureSessionLocal,
                    category_matching_dict[category]["orm_cls"],
                )
            except ValueError as err:
                raise HTTPException(
                    status_code=501,
                    detail=f"DB에 {str_mtr_id}에 해당하는 데이터가 존재하지 않습니다.",
                ) from err
            else:
                dashboard["acq_time"] = dt_to_unix(dashboard["acq_time"])
                response[str_mtr_id] = dashboard | {
                    "part": get_matching_part(part_motor_number_dict, motor_number),
                    "name": generate_motor_code(motor_dict["name"]),
                    "label": motor_dict["category"],
                }
                if category != "v3":
                    if plc is None:
                        plc = 3
                    response[str_mtr_id] = response[str_mtr_id] | get_supply_freq(
                        str_mtr_id,
                        equipment_id,
                        plc,
                    )
                    return response[str_mtr_id]
                else:
                    return response[str_mtr_id]

        response[str_mtr_id] = load_dashboard(
            str_mtr_id,
            motor_dict["category"],  # type: ignore[arg-type]
            plc,
        )

        trigger = TriggerDashboard(equipment_id, motor_number)
        [trigger_dashboard] = trigger.read_dashboard(FeatureSessionLocal, Trigger)
        trigger_dashboard["trigger_acq_time"] = dt_to_unix(
            trigger_dashboard["acq_time"],
        )
        trigger_status = extract_need_key(
            trigger_dashboard,
            [
                "status",
                "plc_status",
                "supply_freq_by_data",
                "rms_u",
                "trigger_acq_time",
            ],
        )
        trigger_status = format_trigger_status(trigger_status)

        response[str_mtr_id] = response_key_change(
            response[str_mtr_id] | trigger_status,
        )
    return dict(
        sorted(response.items(), key=lambda x: int(re.sub(r"[^0-9]", "", x[0]))),
    )


def format_trigger_status(trigger_status: dict) -> dict:
    """대쉬보드 API에서 trigger status 포매팅하는 함수.

    Args:
        trigger_status (dict):trigger 상태.


    Example:
        >>> print(trigger_status.keys())
        [
                "status",
                "plc_status",
                "supply_freq_by_data",
                "rms_u",
                "trigger_acq_time",
        ],

    """
    trigger_status["status"] = "".join(
        ("lges.dashboard.", "status", str(trigger_status["status"])),
    )
    trigger_status["plc_status"] = "".join(
        ("lges.dashboard.", "status", str(trigger_status["plc_status"])),
    )
    return trigger_status
