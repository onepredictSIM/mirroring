"""세팅 클라이언트와 관련된 API 모음.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com.
"""
from datetime import datetime
from typing import Literal, Union

from api.crud.setting_client import (
    delete_parameters_by_plc,
    insert_parameter_by_plc,
    insert_plc_log,
    read_external_setting,
    read_fdc_config,
    read_memory_mapping,
    read_metadata,
    read_metadata_with_rms,
    read_minio_object,
    read_motor_category,
    read_parameter_inquery,
    read_plc_model,
    read_single_external_setting,
    read_single_tension_setting,
    read_single_variable_setting,
    read_tension_setting,
    read_total_motor_equipment,
    read_variable_setting,
    update_fdc_config,
    update_parameter_by_plc,
)
from db.plc.database import PLCSessionLocal
from db.plc.model import PLCModel
from db.service.database import SessionLocal
from db.service.model import (
    ExternalBearing,
    MotorBearing,
    TensionBearing,
    UniformSpeedThreshold,
    Variable,
    VariableSpeedThreshold,
)
from fastapi import APIRouter, HTTPException, status
from schemas.model import UniformSpeedMotor, VariableSpeedMotor
from schemas.setting import (
    FDCConfigDTO,
    MetadataDTO,
    MetadataRMSDTO,
    MinioObjectDTO,
    MotorEquipment,
    ParameterSettingModel,
    PLCModelRow,
)

router = APIRouter()


@router.get("/motor-equipment-category", response_model=Literal["u3e", "u3t", "v3"])
def load_motor_equipment_category(equipment_id: int, motor_number: int) -> str:
    """호기 번호와 호기별 모터 번호를 이용하여 해당 모터의 카테고리를 반환.

    - **equipment_id**: 호기 번호
    - **motor_number**: 호기별 모터 번호.
    """
    return read_motor_category(equipment_id, motor_number)


@router.get(
    "/single-setting-parameter",
    response_model=Union[UniformSpeedMotor, VariableSpeedMotor],
)
def load_single_motor_parameter(
    equipment_id: int,
    motor_number: int,
    category: Literal["u3e", "u3t", "v3"],
    plc: int,
) -> Union[UniformSpeedMotor, VariableSpeedMotor]:
    """특정 plc에 해당하는 모든 모터의 setting parameter를 읽어오는 api.

    알고리즘 서버에서도 사용 가능한 api.
    - **equipment_id**: 호기 번호
    - **motor_number**: 호기 별 모터 번호
    - **plc**: 모델 정보.
    """
    if category == "u3e":
        single_motor_parameter = read_single_external_setting(
            equipment_id,
            motor_number,
            plc,
        )

    elif category == "u3t":
        single_motor_parameter = read_single_tension_setting(
            equipment_id,
            motor_number,
            plc,
        )

    else:
        single_motor_parameter = read_single_variable_setting(
            equipment_id,
            motor_number,
            plc,
        )

    return single_motor_parameter


@router.get("/motor-equipment", response_model=list[MotorEquipment])
def load_motor_equipment() -> list[MotorEquipment]:
    """호기 번호와 호기별 모터 번호를 불러오는 api.

    리턴 값 키 설명
    - **number**: 호기별 모터 번호
    - **name**: 모터 이름
    - **equipment_id**: 호기 번호
    """
    return read_total_motor_equipment()


@router.get("/metadata", response_model=list[MetadataDTO])
def load_metadata(
    equipment_id: int,
    number: int,
    start: datetime,
    end: datetime,
) -> list[MetadataDTO]:
    """호기 번호와 호기별 모터 번호를 불러오는 api.

    리턴되는 딕셔너리 key
    - **equipment_id**: 호기 번호
    - **number**: 호기별 모터 번호
    - **start**: 조회구간 시작점 설정 날짜, iso8601format. e.g. 2021-03-15T15:53:00+09:00
    - **end**: 조회구간 마지막점 설정 날짜, iso8601format. e.g. 2023-03-15T15:53:00+09:00.
    """
    return read_metadata(equipment_id, number, start, end)


@router.get("/metadata-rms", response_model=list[MetadataRMSDTO])
def load_metadata_with_rms(
    equipment_id: int,
    number: int,
    start: datetime,
    end: datetime,
) -> list[MetadataRMSDTO]:
    """호기 번호와 호기별 모터 번호를 불러오는 api.

    리턴되는 딕셔너리 key
    - **equipment_id**: 호기 번호 e.g. 1
    - **number**: 호기별 모터 번호 e.g. 2
    - **start**: 조회구간 시작점 설정 날짜, iso8601format. e.g. 2023-01-18T16:10:00+09:00
    - **end**: 조회구간 마지막점 설정 날짜, iso8601format. e.g. 2023-01-19T16:10:00+09:00.
    """
    return read_metadata_with_rms(equipment_id, number, start, end)


@router.get("/raw-data", response_model=MinioObjectDTO)
def load_minio_object(path: str) -> MinioObjectDTO:
    """Zstd 압축방식으로 압축한 minio object를 압축 해제 후 float list로 리턴하는 api.

    파라미터 값 설명
    - **path**: minio key

    리턴 값 키 설명
    - **equipment_id**: 호기 번호
    - **number**: 호기별 모터 번호
    - **name**: 해당 호기 번호의 모터 번호에 해당하는 이름
    - **current**: 1D float list 전류 데이터
    """
    return read_minio_object(path)


@router.get("/fdc-config", response_model=FDCConfigDTO)
def load_fdc() -> FDCConfigDTO:
    """Fdc DB의 config table을 읽어오는 api."""
    return read_fdc_config()


@router.post("/fdc-config", response_model=FDCConfigDTO)
def update_fdc(config: FDCConfigDTO) -> FDCConfigDTO:
    """FDC config를 업데이트하는 api.

    featuredb_uri는 postgreSQL db uri 조건을 만족해야함.

    Examples:
        featuredb_uri: postgresql://guardione:onepredict1!@10.10.20.24:5432/LGES_feature
    """
    return update_fdc_config(config)


@router.get(
    "/setting-parameter",
    response_model=list[Union[UniformSpeedMotor, VariableSpeedMotor]],
)
def load_setting_parameter(
    plc: int,
) -> list[Union[UniformSpeedMotor, VariableSpeedMotor]]:
    """특정 plc에 해당하는 모든 모터의 setting parameter를 읽어오는 api.

    알고리즘 서버에서도 사용 가능한 api.
    - **plc**: 모델 정보.
    """
    uniform_external_setting = read_external_setting(plc)
    uniform_tension_setting = read_tension_setting(plc)
    variable_setting = read_variable_setting(plc)
    return uniform_external_setting + uniform_tension_setting + variable_setting


@router.get("/mapping-memory", status_code=status.HTTP_200_OK)
def load_memory_mapping() -> list[dict[str, Union[int, str]]]:
    """Memory mapping 테이블 전체를 읽어오는 함수."""
    return read_memory_mapping()


@router.post("/plc", status_code=status.HTTP_201_CREATED)
def insert_plc(body: dict) -> None:
    """PLC log 테이블에 plc 값을 insert하는 함수.

    - **timestamp** : 현재 로그 타임스탬프
    - **기타**:  "PLC.13-1.CellState_Model" 식의 구조로 body의 키가 채워져서 옴.
    """
    insert_plc_log(body)


@router.get("/plc-model", response_model=list[PLCModelRow])
def load_plc_model() -> list[PLCModelRow]:
    """Plc DB의 model table을 읽어오는 api.

    리턴 값 키 설명
    - **line_id**: 라인 번호
    - **equipment_id**: 호기 번호
    - **model**: 모델 번호
    - **name**: 모델 이름
    - **description**: 모델 설명
    """
    return read_plc_model()


@router.get("/parameter", response_model=ParameterSettingModel)
def load_parameter_inquery(
    equipment_id: int,
    motor_number: int,
    plc: int,
) -> ParameterSettingModel:
    """주어진 호기 번호, 모터 번호, plc 모델에 해당하는 모터 스펙 및 파라미터 리턴.

    - **equipment_id**: 호기 번호
    - **motor_number**: 호기별 모터 번호
    - **plc**: plc 모델 번호.
    """
    return read_parameter_inquery(equipment_id, motor_number, plc)


@router.put("/parameter", response_model=ParameterSettingModel)
def update_plc_model_parameter(body: dict) -> ParameterSettingModel:
    """모델 조회 이후에 업데이트, input은 response model과 동일."""
    return update_parameter_by_plc(body)


@router.post(
    "/parameter",
    status_code=status.HTTP_201_CREATED,
    response_model=ParameterSettingModel,
)
def create_plc_model_parameter(body: dict) -> None:
    """신규 모델 생성 및 해당 모델에 대한 파라미터도 입력.

    input은 response model과 동일.
    """
    return insert_parameter_by_plc(body)


@router.delete("/parameter", status_code=status.HTTP_200_OK)
def delete_plc_model_parameter(plc: int) -> None:
    """특정 PLC 모델 삭제, 디버깅용으로 자주 쓰는 api.

    - **plc**: plc 모델
    """
    if plc == 3:  # noqa: PLR2004
        raise HTTPException(
            status_code=403,
            detail="디폴트 파라미터는 삭제가 불가능합니다.",
        )

    cls_list = [
        ExternalBearing,
        MotorBearing,
        TensionBearing,
        UniformSpeedThreshold,
        Variable,
        VariableSpeedThreshold,
    ]
    for _cls in cls_list:
        delete_parameters_by_plc(SessionLocal, _cls, plc=plc)

    delete_parameters_by_plc(PLCSessionLocal, PLCModel, plc=plc)
