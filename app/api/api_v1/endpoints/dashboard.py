"""dashboard와 관련된 API 모음.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
from typing import Optional, Union

from api.crud.dashboard import (
    load_equipments,
    load_line_equipment_category,
    load_plcmodel_by_equipment,
)
from api.crud.setting_client import get_motors_in_equipment
from api.crud.util import get_detail_motor_number_list
from api.format.dashboard import format_dashboard
from fastapi import APIRouter

router = APIRouter()


@router.get("/line-equipment")
async def line_equipment_api() -> list[dict]:
    """현재 라인 넘버(환경변수)에 해당하는 라인, 호기 정보를 불러오는 api."""
    return load_line_equipment_category()


@router.get("/equipments")
async def equipments_api() -> list[dict[str, Union[int, str]]]:
    """현재 라인에 들어있는 전체 호기를 불러오는 API."""
    return load_equipments()


@router.get("/plc_models")
async def plc_model_api(equipment_id: int) -> list[dict[str, Union[int, str]]]:
    """현재 호기에 들어있는 plc model을 불러오는 API.

    - **equipment_id**: 호기 번호.
    """
    return load_plcmodel_by_equipment(equipment_id)


@router.get("/")
async def dashboard_api(
    equipment_id: int,
    plc: Optional[int] = None,
) -> dict[str, dict[str, Union[int, float, str]]]:
    """화면의 대쉬보드 정보를 담당하는 API.

    - **equipment_id**: 호기 번호
    - **plc**: plc 모델 번호, 기본 값으로는 PLC log 테이블에서
                현재 호기에 해당하는 가장 최신 plc값을 사용.
    """
    motors_in_equipment = get_motors_in_equipment(equipment_id)
    equipment_name = motors_in_equipment[0]["equipment_name"]
    part_motor_number_dict = get_detail_motor_number_list(equipment_name)
    return format_dashboard(motors_in_equipment, part_motor_number_dict, plc)
