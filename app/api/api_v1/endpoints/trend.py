"""트렌드와 관련된 API 모음.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
from datetime import datetime
from typing import Optional

from api.crud.setting_client import get_motors_in_equipment
from api.crud.util import get_detail_motor_number_list
from api.format.trend import (
    format_load,
    format_operating,
    format_uniform_diagnosis,
    format_variable_diagnosis,
)
from api.schemas.trend import HealthTrendInit, OperatingTrendInit
from fastapi import APIRouter

router = APIRouter()


@router.get("/variable_diagnosis")
async def variable_diagnosis_api(
    equipment_id: int,
    plc: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    """변속 진단 API.

    - **equipment_id**: 호기 번호
    - **plc**: plc 모델 번호, 기본 값으로는 PLC log 테이블에서
                현재 호기에 해당하는 가장 최신 plc값을 사용
    - **start**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜
    - **end**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜.
    """
    motors_in_equipment = get_motors_in_equipment(equipment_id)
    equipment_name = motors_in_equipment[0]["equipment_name"]
    part_motor_number_dict = get_detail_motor_number_list(equipment_name)
    return format_variable_diagnosis(
        motors_in_equipment,
        part_motor_number_dict,
        plc,
        start,
        end,
    )


@router.get("/uniform_diagnosis")
async def uniform_diagnosis_api(
    equipment_id: int,
    plc: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    """정속 진단 API.

    - **equipment_id**: 호기 번호
    - **plc**: plc 모델 번호, 기본 값으로는 PLC log 테이블에서
                현재 호기에 해당하는 가장 최신 plc값을 사용
    - **start**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜
    - **end**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜.
    """
    motors_in_equipment = get_motors_in_equipment(equipment_id)
    equipment_name = motors_in_equipment[0]["equipment_name"]
    part_motor_number_dict = get_detail_motor_number_list(equipment_name)
    return format_uniform_diagnosis(
        motors_in_equipment,
        part_motor_number_dict,
        plc,
        start,
        end,
    )


@router.get("/load")
async def load_api(
    equipment_id: int,
    plc: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    """부하 API.

    - **equipment_id**: 호기 번호
    - **plc**: plc 모델 번호, 기본 값으로는 PLC log 테이블에서
                현재 호기에 해당하는 가장 최신 plc값을 사용
    - **start**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜
    - **end**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜.
    """
    motors_in_equipment = get_motors_in_equipment(equipment_id)
    equipment_name = motors_in_equipment[0]["equipment_name"]
    part_motor_number_dict = get_detail_motor_number_list(equipment_name)
    return format_load(motors_in_equipment, part_motor_number_dict, plc, start, end)


@router.get("/operating")
async def operating_api(
    equipment_id: int,
    plc: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    """운영 인자 API.

    - **equipment_id**: 호기 번호
    - **plc**: plc 모델 번호, 기본 값으로는 PLC log 테이블에서
                현재 호기에 해당하는 가장 최신 plc값을 사용
    - **start**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜
    - **end**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜.
    """
    motors_in_equipment = get_motors_in_equipment(equipment_id)
    equipment_name = motors_in_equipment[0]["equipment_name"]
    part_motor_number_dict = get_detail_motor_number_list(equipment_name)
    return format_operating(
        motors_in_equipment,
        part_motor_number_dict,
        plc,
        start,
        end,
    )


@router.get("/trend-init")
async def trend_init_api() -> dict[str, list[int]]:
    """Trend 페이지 처음 누를 때 호출되어야하는 api."""
    return {
        "operating": OperatingTrendInit.apply_operating_prefix(),
        "health": HealthTrendInit.apply_health_prefix(),
    }
