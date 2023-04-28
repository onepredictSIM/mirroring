"""상세페이지와 관련된 API 모음.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
import sys
from collections import defaultdict
from datetime import datetime
from typing import Optional, Union

from api.crud.util import (
    display_num_dict,
    get_detail_motor_number_list,
    get_equipment_name,
)
from api.format.detail import format_detail, response_key_change
from api.schemas.detail import DetailInitAPIFactory
from fastapi import APIRouter, Depends, Request

router = APIRouter()


@router.get("/pc")
async def pc_api(
    equipment_id: int,
    plc: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    """양극 커팅부 API.

    - **equipment_id**: 호기 번호
    - **plc**: plc 모델 번호, 기본 값으로는 PLC log 테이블에서
                현재 호기에 해당하는 가장 최신 plc값을 사용
    - **start**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜
    - **end**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜.
    """
    equipment_name = get_equipment_name(equipment_id)
    part_name = sys._getframe().f_code.co_name.split("API")[0]  # noqa: SLF001
    motor_number_list = get_detail_motor_number_list(equipment_name)[part_name]

    response: dict = defaultdict(dict)

    for motor_number in motor_number_list:
        str_mtr_id = "".join(("motor", str(motor_number)))
        response[str_mtr_id] = response_key_change(
            format_detail(equipment_id, motor_number, plc, start, end),
        )

    for motor_number in response:
        for key, value in display_num_dict.items():
            if key in response[motor_number]["name"]:
                response[motor_number]["display_num"] = value

    return response


@router.get("/nc")
async def nc_api(
    equipment_id: int,
    plc: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    """음극 커팅부 API.

    - **equipment_id**: 호기 번호
    - **plc**: plc 모델 번호, 기본 값으로는 PLC log 테이블에서
                현재 호기에 해당하는 가장 최신 plc값을 사용
    - **start**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜
    - **end**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜.
    """
    equipment_name = get_equipment_name(equipment_id)
    part_name = sys._getframe().f_code.co_name.split("API")[0]  # noqa: SLF001
    motor_number_list = get_detail_motor_number_list(equipment_name)[part_name]

    response: dict = defaultdict(dict)

    for motor_number in motor_number_list:
        str_mtr_id = "".join(("motor", str(motor_number)))
        response[str_mtr_id] = response_key_change(
            format_detail(equipment_id, motor_number, plc, start, end),
        )

    for motor_number in response:
        for key, value in display_num_dict.items():
            if key in response[motor_number]["name"]:
                response[motor_number]["display_num"] = value

    return response


@router.get("/lami")
async def lami_api(
    equipment_id: int,
    plc: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    """라미롤부 API.

    - **equipment_id**: 호기 번호
    - **plc**: plc 모델 번호, 기본 값으로는 PLC log 테이블에서
                현재 호기에 해당하는 가장 최신 plc값을 사용
    - **start**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜
    - **end**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜.
    """
    equipment_name = get_equipment_name(equipment_id)
    part_name = sys._getframe().f_code.co_name.split("API")[0]  # noqa: SLF001
    motor_number_list = get_detail_motor_number_list(equipment_name)[part_name]

    response: dict = defaultdict(dict)

    for motor_number in motor_number_list:
        str_mtr_id = "".join(("motor", str(motor_number)))
        response[str_mtr_id] = response_key_change(
            format_detail(equipment_id, motor_number, plc, start, end),
        )

    for motor_number in response:
        for key, value in display_num_dict.items():
            if key in response[motor_number]["name"]:
                response[motor_number]["display_num"] = value

    return response


@router.get("/fc")
async def fc_api(
    equipment_id: int,
    plc: Optional[int] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> dict:
    """파이널 커팅부 API.

    - **equipment_id**: 호기 번호
    - **plc**: plc 모델 번호, 기본 값으로는 PLC log 테이블에서
                현재 호기에 해당하는 가장 최신 plc값을 사용
    - **start**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜
    - **end**: 특정 구간 조회할 경우(상세페이지 다운로드 때 사용) 시작 날짜.
    """
    equipment_name = get_equipment_name(equipment_id)
    part_name = sys._getframe().f_code.co_name.split("API")[0]  # noqa: SLF001
    motor_number_list = get_detail_motor_number_list(equipment_name)[part_name]

    response: dict = defaultdict(dict)

    for motor_number in motor_number_list:
        str_mtr_id = "".join(("motor", str(motor_number)))
        response[str_mtr_id] = response_key_change(
            format_detail(equipment_id, motor_number, plc, start, end),
        )

    for motor_number in response:
        for key, value in display_num_dict.items():
            if key in response[motor_number]["name"]:
                response[motor_number]["display_num"] = value

    return dict(sorted(response.items(), key=lambda x: x[1]["display_num"]))


def get_detail_init_api_factory(
    equipment_id: int,
    request: Request,
) -> DetailInitAPIFactory:
    """Detail_init_API_factory를 생성하는 함수.

    Args:
        equipment_id (int): 호기 번호
        request (Request): FastAPI Request 객체
    Returns:
        DetailInitAPIFactory
    """
    path = request.url.path
    part = path.split("/")[-1].split("-")[0]
    return DetailInitAPIFactory(equipment_id, part)


@router.get("/pc-init")
async def pc_init_api(
    equipment_id: int,  # noqa: ARG001
    detail_init_api_factory: DetailInitAPIFactory = Depends(
        get_detail_init_api_factory,
    ),
) -> dict[str, dict[str, Union[int, str, list[str]]]]:
    """양극 커팅부 상세페이지를 처음 눌렀을 때, 호출되어야 하는 api.

    - **equipment_id**: 호기 번호
    - **detail_init_api_factory**: DetailInitAPIFactory를
        호기번호와 파트 이름으로 초기화한 후, 필요 정보 리턴.
    """
    return detail_init_api_factory.init_api()


@router.get("/nc-init")
async def nc_init_api(
    equipment_id: int,  # noqa: ARG001
    detail_init_api_factory: DetailInitAPIFactory = Depends(
        get_detail_init_api_factory,
    ),
) -> dict[str, dict[str, Union[int, str, list[str]]]]:
    """음극 커팅부 상세페이지를 처음 눌렀을 때, 호출되어야 하는 api.

    - **equipment_id**: 호기 번호
    - **detail_init_api_factory**: DetailInitAPIFactory를
        호기번호와 파트 이름으로 초기화한 후, 필요 정보 리턴.
    """
    return detail_init_api_factory.init_api()


@router.get("/lami-init")
async def lami_init_api(
    equipment_id: int,  # noqa: ARG001
    detail_init_api_factory: DetailInitAPIFactory = Depends(
        get_detail_init_api_factory,
    ),
) -> dict[str, dict[str, Union[int, str, list[str]]]]:
    """라미롤부 상세페이지를 처음 눌렀을 때, 호출되어야 하는 api.

    - **equipment_id**: 호기 번호
    - **detail_init_api_factory**: DetailInitAPIFactory를
        호기번호와 파트 이름으로 초기화한 후, 필요 정보 리턴.
    """
    return detail_init_api_factory.init_api()


@router.get("/fc-init")
async def fc_init_api(
    equipment_id: int,  # noqa: ARG001
    detail_init_api_factory: DetailInitAPIFactory = Depends(
        get_detail_init_api_factory,
    ),
) -> dict[str, dict[str, Union[int, str, list[str]]]]:
    """파이널 커팅부 상세페이지를 처음 눌렀을 때, 호출되어야 하는 api.

    - **equipment_id**: 호기 번호
    - **detail_init_api_factory**: DetailInitAPIFactory 객체.
    """
    return detail_init_api_factory.init_api()
