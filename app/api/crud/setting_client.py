"""세팅 클라이언트와 관련된 CRUD 모음.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Optional, TypeVar, Union

from api.crud.util import (
    general_insert_multiple_value,
    general_insert_value,
    update_variable_with_float_template,
)
from api.format.setting_client import (
    format_external_bearing,
    format_motor_bearing,
    format_tension_bearing,
    format_uniform_threshold,
    generate_required_dict,
    matching_metadata_and_trigger,
)
from botocore.exceptions import ClientError
from core.config import setting
from db.fdc.database import FDCSessionLocal
from db.fdc.model import FDCConfig
from db.feature.database import FeatureSessionLocal
from db.feature.model import (
    Trigger,
    UniformSpeedExternalFeature,
    UniformSpeedTensionFeature,
    VariableSpeedPhase1Feature,
    VariableSpeedPhase3Feature,
)
from db.metadata.database import MetadataSessionLocal
from db.metadata.model import MetaData
from db.plc.database import PLCSessionLocal
from db.plc.model import MemoryMapping, PLCLog, PLCModel
from db.service.database import SessionLocal
from db.service.model import (
    Equipment,
    ExternalBearing,
    Motor,
    MotorBearing,
    TensionBearing,
    UniformSpeedThreshold,
    Variable,
    VariableSpeedThreshold,
)
from fastapi import HTTPException
from pytz import timezone, utc
from schemas.model import UniformSpeedMotor, VariableSpeedMotor
from schemas.setting import (
    FDCConfigDTO,
    MetadataDTO,
    MotorEquipment,
    ParameterSettingModel,
)
from sqlalchemy import and_
from sqlalchemy.engine.row import Row
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker
from util.minio import get_zstd_object
from util.utils import delete_key, extract_need_key, load_columns, row_to_dict

T = TypeVar("T")


def get_motors_in_equipment(equipment_id: int) -> list[dict[str, Union[int, str]]]:
    """특정 호기번호를 주었을 때, 거기 있는 모든 모터 정보 리턴."""
    return list(
        filter(
            lambda x: x["equipment_id"] == equipment_id,
            (x.dict() for x in read_total_motor_equipment()),
        ),
    )


def read_total_motor_equipment() -> list[MotorEquipment]:
    """모터 테이블에서 호기 번호, 모터 번호, 모터 이름 정보 전부 불러오기.

    Returns:
        List[MotorEquipment]
    """
    with SessionLocal() as session:
        query_results = (
            session.query(Motor, Equipment.name, Equipment.line_id)
            .join(Motor, Motor.equipment_id == Equipment.id)
            .order_by(Motor.equipment_id.asc(), Motor.number.asc())
            .all()
        )

    needed_keys = ["line_id", "equipment_id", "number", "name", "category"]
    response = []
    for row in query_results:
        motor_query_result, equipment_name, line_id = row
        motor_dict = [
            extract_need_key(row, needed_keys)
            for row in row_to_dict([motor_query_result])
        ]
        equipment_dict = {"equipment_name": equipment_name, "line_id": line_id}
        equipment_dict.update(motor_dict[0])
        motor_equipment = MotorEquipment(**equipment_dict)
        response.append(motor_equipment)

    return response


def read_metadata(
    equipment_id: int,
    motor_number: int,
    start: datetime,
    end: datetime,
) -> list[MetadataDTO]:
    """특정 호기, 특정 모터 번호의 조회 시작 구간(start)부터.

    끝 구간(end)까지 메타데이터 조회하기.

    Returns:
        List[MetadataDTO]
    """
    with MetadataSessionLocal() as session:
        query_results = (
            session.query(MetaData)
            .filter(
                and_(
                    MetaData.acq_time > start,
                    MetaData.acq_time < end,
                ),
            )
            .filter(MetaData.equipment_id == equipment_id)
            .filter(MetaData.motor_number == motor_number)
            .order_by(MetaData.acq_time.desc())
            .all()
        )
    return [MetadataDTO(**row) for row in row_to_dict(query_results)]


def read_metadata_with_rms(
    equipment_id: int,
    motor_number: int,
    start: datetime,
    end: datetime,
) -> list[dict[str, Any]]:
    """metadata-rms endpoint api에 사용되는 함수이며, legacy.

    추후 metadata-rms 기능을 개발하고 싶은 경우, 본 함수를 사용하는 것보다는
    trigger 테이블에서 rms_v, rms_w를 만드는 것이 바람직함.
    """
    with MetadataSessionLocal() as session:
        query_results = (
            session.query(MetaData)
            .filter(
                and_(
                    MetaData.acq_time > start,
                    MetaData.acq_time < end,
                ),
            )
            .filter(
                MetaData.equipment_id == equipment_id,
                MetaData.motor_number == motor_number,
            )
            .filter()
            .order_by(MetaData.acq_time.desc())
            .all()
        )

        metadata_query_results = row_to_dict(query_results)

    with FeatureSessionLocal() as session:
        query_results = (
            session.query(Trigger)
            .filter(
                and_(
                    Trigger.acq_time > start,
                    Trigger.acq_time < end,
                ),
            )
            .filter(Trigger.equipment_id == equipment_id)
            .filter(Trigger.motor_number == motor_number)
            .order_by(Trigger.acq_time.desc())
            .all()
        )

    trigger_query_results = row_to_dict(query_results)

    return matching_metadata_and_trigger(metadata_query_results, trigger_query_results)


def read_motor_category(equipment_id: int, motor_number: int) -> str:
    """equipment_id, motor_number를 이용해서 모터 카테고리 정보 받아오기.

    Returns:
        List[Dict[str, Union[int, str]]]
    """
    with SessionLocal() as session:
        [query_results] = (
            session.query(Motor.category)
            .filter(Motor.equipment_id == equipment_id, Motor.number == motor_number)
            .all()[0]
        )

    return query_results


def read_motor_equipment(equipment_id: int, motor_number: int) -> list[dict[str, Any]]:
    """모터 테이블에서 호기 번호, 모터 번호에 해당하는 이름 1개 불러오기.

    Args:
        equipment_id (int): 호기 번호
        motor_number (int): 모터 번호
    Returns:
        List[Dict[str, Union[int, str]]].
    """
    with SessionLocal() as session:
        query_results = (
            session.query(Motor, Equipment.name)
            .join(Motor, Motor.equipment_id == Equipment.id)
            .filter(Motor.equipment_id == equipment_id, Motor.number == motor_number)
            .all()
        )

    needed_keys = ["equipment_id", "number", "name"]
    response = []
    for row in query_results:
        motor_query_result, equipment_name = row
        motor_dict = [
            extract_need_key(row, needed_keys)
            for row in row_to_dict([motor_query_result])
        ]
        equipment_dict = {"equipment_name": equipment_name}
        equipment_dict.update(motor_dict[0])
        response.append(equipment_dict)

    return response


def read_minio_object(path: str) -> Optional[dict]:
    """Zstd 압축방식으로 압축된 minio object를 압축 해제 후 float list로 리턴하는 함수.

    Args:
        path (str): line_name/equipment_id/motor_number/year/month/day/HHMMSS_phase.zst


    Returns:
        List[Dict[str, Union[int, str]]]

    Examples:
        print(path)
        /13/02/03/2023/04/12/045137_u.zst

    """
    line_id, equipment_id, motor_number = path.split("/")[1:4]
    year, month, day, file_name = path.split("/")[4:]
    hhmmss, phase = file_name.split("_")
    phase = phase.split(".")[0]
    acq_time = f"{year}-{month}-{day} {hhmmss}"
    acq_time_date = datetime.strptime(acq_time, "%Y-%m-%d %H%M%S")  # noqa: DTZ007

    line_id = 1  # type: ignore[assignment]

    try:
        response_dict = {"current": get_zstd_object(path)}
    except ClientError as ex:
        if ex.response["Error"]["Code"] == "NoSuchKey":  # minio에 객체가 없음
            # MetaData에 실제로 해당 path가 존재하지 않는지 확인하기
            with MetadataSessionLocal() as session:
                query_result = (
                    session.query(MetaData).filter(
                        MetaData.line_id == line_id,
                        MetaData.equipment_id == equipment_id,
                        MetaData.motor_number == motor_number,
                        MetaData.phase == phase,
                    )
                ).all()

                if not query_result:  # minio에 없고, metadata RDS에도 없을 경우
                    logging.warning("Data not found in minio and metadata RDBMS")
                    raise HTTPException(
                        status_code=404,
                        detail="Data not found in minio and metadata RDBMS",
                    ) from ex
                # minio에는 없는데, metadata RDS에 해당 값이 존재할 경우, 해당 값 삭제
                if query_result:
                    session.query(MetaData).filter(
                        MetaData.line_id == line_id,
                        MetaData.equipment_id == equipment_id,
                        MetaData.motor_number == motor_number,
                        MetaData.phase == phase,
                    ).delete()
                    session.commit()

                    logging.warning("Data was in Metadata RDBMS but not in minio")
                    # minio 객체가 없으므로 에러 메시지 전송
                    raise HTTPException(
                        status_code=404,
                        detail="Data was in Metadata RDBMS but not in minio",
                    ) from ex
        else:
            logging.error("Data not found, need to check")
            raise HTTPException(status_code=404, detail="Data not found") from ex
    else:  # minio에 객체가 있음
        with MetadataSessionLocal() as session:
            query_result = (
                session.query(MetaData).filter(
                    MetaData.line_id == line_id,
                    MetaData.equipment_id == equipment_id,
                    MetaData.motor_number == motor_number,
                    MetaData.phase == phase,
                )
            ).all()

        if (
            not query_result
        ):  # minio에 객체가 있는데, metadata RDS에는 없을 경우 metadata RDS에 insert
            raw_data_dict = {
                "line_id": line_id,
                "equipment_id": equipment_id,
                "motor_number": motor_number,
                "phase": phase,
                "acq_time": acq_time_date,
                "file_path": path,
            }
            # 이 작업을 해주면 minio, metadata RDS에 둘다 존재함
            general_insert_value(MetadataSessionLocal, MetaData, raw_data_dict)

        # minio, metadata RDS에 둘다 존재함
        channel_dict = {"channel": path.split("_")[-1].split(".")[0]}
        equipment_id, motor_number = path.split("/")[2:4]
        response_dict.update(
            read_motor_equipment(int(equipment_id), int(motor_number))[0],
        )
        response_dict.update(channel_dict)
    return response_dict


def read_fdc_config() -> FDCConfigDTO:
    """Fdc config를 읽는 함수.

    Returns:
        FDCConfigDTO
    """
    with FDCSessionLocal() as session:
        query_results = session.query(FDCConfig).all()

    columns = load_columns(FDCConfig())
    columns.remove("id")
    columns.remove("updated_time")

    if not query_results:
        response = {key: "" for key in columns}

    else:
        response = {
            key: value
            for key, value in row_to_dict(query_results)[0].items()
            if key in columns
        }

    return response


def update_fdc_config(config: FDCConfigDTO) -> FDCConfigDTO:
    """FDC config를 업데이트하는 함수.

    Args:
        config (FDCConfigDTO): FDCConfig에 대한 DTO
    Returns:
        FDCConfigDTO
    """
    config = config.dict()
    config.update({"updated_time": datetime.now()})  # noqa: DTZ005
    with FDCSessionLocal() as session:
        session.query(FDCConfig).filter(FDCConfig.id == 1).update(config)
        session.commit()

    return FDCConfigDTO(**config)


def insert_plc_log(body: dict) -> None:
    """Plc log를 쌓는 함수.

    Args:
        body(dict): Kepware에서 보내는 plc log.
    """
    plc_log_dict = {}
    plc_log_dict["timestamp"] = body["timestamp"]
    body.pop("timestamp", None)

    for key, value in body.items():
        _, equipment_name, name = key.split(".")
        filtered_list = view_memory_mapping(
            matching_equipment_id_using_equipment_name(equipment_name),
        )
        for i in filtered_list:
            if i["name"] == name:
                plc_log_dict.update({"mm_id": i["id"], "value": value})
                general_insert_value(PLCSessionLocal, PLCLog, plc_log_dict)


def read_memory_mapping() -> dict[str, Union[int, str]]:
    """PLC DB의 memorymapping 테이블을 읽는 함수."""
    with PLCSessionLocal() as session:
        query_results = session.query(MemoryMapping).all()
    return row_to_dict(query_results)


def read_variable_setting(plc: int) -> list[VariableSpeedMotor]:
    """GET /api/v1/setting-client/setting-parameter에서 사용되는 함수.

    특정 plc 모델 값에 따른 모든 v3 모터의 파라미터를 불러오는 함수.

    Args:
        plc (int): plc model 값
    Returns:
        list[UniformSpeedMotor]
    """
    """"""
    with SessionLocal() as session:
        query_results = (
            session.query(Equipment, Motor, Variable, VariableSpeedThreshold)
            .select_from(Equipment)
            .join(Motor)
            .join(Variable)
            .join(VariableSpeedThreshold)
            .filter(
                Motor.category == "v3",  # 폴란드 api 기준으로는 v3, 오창에는 v1 포함
                Motor.equipment_id == Variable.equipment_id,
                Motor.number == Variable.motor_number,
                Motor.equipment_id == VariableSpeedThreshold.equipment_id,
                Motor.number == VariableSpeedThreshold.motor_number,
                VariableSpeedThreshold.plc == plc,
                Variable.plc == plc,
            )
        ).all()
    dict_list = row_to_dict(query_results)

    popped_column = ["id", "updated_time", "template"]

    setting_client_param_list = []

    for _dict in dict_list:
        equipment, motor, variable, variable_threshold = (
            _dict["Equipment"],
            _dict["Motor"],
            _dict["Variable"],
            _dict["VariableSpeedThreshold"],
        )
        equipment["equipment_name"] = equipment.pop("name")
        variable = update_variable_with_float_template(variable)
        setting_client_param_list.append(
            delete_key(
                equipment | motor | variable | variable_threshold,
                popped_column,
            ),
        )

    return [VariableSpeedMotor(**x) for x in setting_client_param_list]


def read_external_setting(plc: int) -> list[UniformSpeedMotor]:
    """GET /api/v1/setting-client/setting-parameter에서 사용되는 함수.

    특정 plc 모델 값에 따른 모든 u3e 모터의 파라미터를 불러오는 함수.

    Args:
        plc (int): plc model 값
    Returns:
        list[UniformSpeedMotor]
    """
    with SessionLocal() as session:
        query_results = (
            session.query(
                Equipment,
                Motor,
                MotorBearing,
                ExternalBearing,
                UniformSpeedThreshold,
            )
            .select_from(Equipment)
            .join(Motor)
            .join(MotorBearing)
            .join(ExternalBearing)
            .join(UniformSpeedThreshold)
            .filter(
                Motor.category == "u3e",
                Motor.equipment_id == MotorBearing.equipment_id,
                Motor.number == MotorBearing.motor_number,
                Motor.equipment_id == ExternalBearing.equipment_id,
                Motor.number == ExternalBearing.motor_number,
                Motor.equipment_id == UniformSpeedThreshold.equipment_id,
                Motor.number == UniformSpeedThreshold.motor_number,
                UniformSpeedThreshold.plc == plc,
                MotorBearing.plc == plc,
                ExternalBearing.plc == plc,
            )
        ).all()
    dict_list = row_to_dict(query_results)
    popped_column = ["id", "updated_time"]

    setting_client_param_list = []
    for _dict in dict_list:
        equipment, motor, motor_bearing, external_bearing, uniform_threshold = (
            _dict["Equipment"],
            _dict["Motor"],
            _dict["MotorBearing"],
            _dict["ExternalBearing"],
            _dict["UniformSpeedThreshold"],
        )
        equipment["equipment_name"] = equipment.pop("name")
        motor_bearing["motor_bearing_moving_median_sample_number"] = motor_bearing.pop(
            "moving_median_sample_number",
        )
        external_bearing[
            "external_bearing_moving_median_sample_number"
        ] = external_bearing.pop("moving_median_sample_number")
        setting_client_param_list.append(
            delete_key(
                equipment
                | motor
                | motor_bearing
                | external_bearing
                | uniform_threshold,
                popped_column,
            ),
        )

    return [UniformSpeedMotor(**x) for x in setting_client_param_list]


def read_tension_setting(plc: int) -> list[UniformSpeedMotor]:
    """GET /api/v1/setting-client/setting-parameter에서 사용되는 함수.

    특정 plc 모델 값에 따른 모든 u3t 모터의 파라미터를 불러오는 함수.

    Args:
        plc (int): plc model 값
    Returns:
        list[UniformSpeedMotor]
    """
    with SessionLocal() as session:
        query_results = (
            session.query(
                Equipment,
                Motor,
                MotorBearing,
                ExternalBearing,
                TensionBearing,
                UniformSpeedThreshold,
            )
            .select_from(Equipment)
            .join(Motor)
            .join(MotorBearing)
            .join(ExternalBearing)
            .join(TensionBearing)
            .join(UniformSpeedThreshold)
            .filter(
                Motor.category == "u3t",
                Motor.equipment_id == MotorBearing.equipment_id,
                Motor.number == MotorBearing.motor_number,
                Motor.equipment_id == ExternalBearing.equipment_id,
                Motor.number == ExternalBearing.motor_number,
                Motor.equipment_id == UniformSpeedThreshold.equipment_id,
                Motor.number == UniformSpeedThreshold.motor_number,
                Motor.equipment_id == TensionBearing.equipment_id,
                Motor.number == TensionBearing.motor_number,
                UniformSpeedThreshold.plc == plc,
                MotorBearing.plc == plc,
                ExternalBearing.plc == plc,
                TensionBearing.plc == plc,
            )
        ).all()

    dict_list = row_to_dict(query_results)
    popped_column = ["id", "updated_time"]

    setting_client_param_list = []
    for _dict in dict_list:
        (
            equipment,
            motor,
            motor_bearing,
            external_bearing,
            tension_bearing,
            uniform_threshold,
        ) = (
            _dict["Equipment"],
            _dict["Motor"],
            _dict["MotorBearing"],
            _dict["ExternalBearing"],
            _dict["TensionBearing"],
            _dict["UniformSpeedThreshold"],
        )
        motor_bearing["motor_bearing_moving_median_sample_number"] = motor_bearing.pop(
            "moving_median_sample_number",
        )
        external_bearing[
            "external_bearing_moving_median_sample_number"
        ] = external_bearing.pop("moving_median_sample_number")
        tension_bearing[
            "tension_bearing_moving_median_sample_number"
        ] = tension_bearing.pop("moving_median_sample_number")
        equipment["equipment_name"] = equipment.pop("name")
        setting_client_param_list.append(
            delete_key(
                equipment
                | motor
                | motor_bearing
                | external_bearing
                | tension_bearing
                | uniform_threshold,
                popped_column,
            ),
        )

    return [UniformSpeedMotor(**x) for x in setting_client_param_list]


def read_feature_by_acq_time(
    equipment_id: int,
    motor_number: int,
    acq_time: datetime,
) -> list[Row]:
    """GET /api/v1/fdc/fdc-feature api에서 사용되는 함수.

    현재 해당 API가 사용되지 않고 있음.

    Args:
        equipment_id (int): 호기 번호
        motor_number (int): 모터 번호
        acq_time (datetime): 시간

    Returns:
        list[Row]
    """
    with SessionLocal() as session:
        category = (
            session.query(Motor.category).filter(
                Motor.equipment_id == equipment_id,
                Motor.number == motor_number,
            )
        ).first()[0]

    _cls_list = {
        "v3": VariableSpeedPhase3Feature,
        "v1": VariableSpeedPhase1Feature,
        "u3e": UniformSpeedExternalFeature,
        "u3t": UniformSpeedTensionFeature,
    }

    _cls = _cls_list[category]

    with FeatureSessionLocal() as session:
        query_results = (
            session.query(_cls).filter(
                _cls.acq_time == acq_time,
                _cls.equipment_id == equipment_id,
                _cls.motor_number == motor_number,
            )
        ).all()
    return query_results


def read_plc_model() -> list[Row]:
    """GET /api/v1/setting-client/plc-model api에서 사용되는 함수.

    LGES_plc DB의 model 테이블을 불러오는 함수.

    Returns:
        list[Row]
    """
    with PLCSessionLocal() as session:
        query_results = session.query(PLCModel).order_by(PLCModel.model.asc()).all()
    return row_to_dict(query_results)


def read_single_variable_setting(
    equipment_id: int,
    motor_number: int,
    plc: int,
) -> VariableSpeedMotor:
    """GET /api/v1/setting-client/parameter api에서 사용되는 함수.

    현재 파일의 read_parameter_inquery 함수에서 사용되는 함수
    모터 카테고리가 v3일때 사용됨

    Args:
        equipment_id (int): 모터 번호
        motor_number (int): 호기 번호
        plc (int): plc_model 값
    Returns:
        UniformSpeedMotor
    """
    with SessionLocal() as session:
        query_results = (
            session.query(Equipment, Motor, Variable, VariableSpeedThreshold)
            .select_from(Equipment)
            .join(Motor)
            .join(Variable)
            .join(VariableSpeedThreshold)
            .filter(
                Motor.category == "v3",  # 폴란드 api 기준으로는 v3, 오창에는 v1 포함
                Motor.equipment_id == Variable.equipment_id,
                Motor.number == Variable.motor_number,
                Motor.equipment_id == VariableSpeedThreshold.equipment_id,
                Motor.number == VariableSpeedThreshold.motor_number,
                VariableSpeedThreshold.plc == plc,
                Variable.plc == plc,
                Motor.equipment_id == equipment_id,
                Motor.number == motor_number,
            )
        ).all()
    dict_list = row_to_dict(query_results)

    popped_column = ["id", "updated_time"]

    setting_client_param_list = []

    for _dict in dict_list:
        equipment, motor, variable, variable_threshold = (
            _dict["Equipment"],
            _dict["Motor"],
            _dict["Variable"],
            _dict["VariableSpeedThreshold"],
        )
        variable = update_variable_with_float_template(variable)
        equipment["equipment_name"] = equipment.pop("name")
        setting_client_param_list.append(
            delete_key(
                equipment | motor | variable | variable_threshold,
                popped_column,
            ),
        )

    return [VariableSpeedMotor(**x) for x in setting_client_param_list][0]


def read_single_tension_setting(
    equipment_id: int,
    motor_number: int,
    plc: int,
) -> UniformSpeedMotor:
    """GET /api/v1/setting-client/parameter api에서 사용되는 함수.

    현재 파일의 read_parameter_inquery 함수에서 사용되는 함수
    모터 카테고리가 u3t일때 사용됨

    Args:
        equipment_id (int): 모터 번호
        motor_number (int): 호기 번호
        plc (int): plc_model 값
    Returns:
        UniformSpeedMotor
    """
    with SessionLocal() as session:
        query_results = (
            session.query(
                Equipment,
                Motor,
                MotorBearing,
                ExternalBearing,
                TensionBearing,
                UniformSpeedThreshold,
            )
            .select_from(Equipment)
            .join(Motor)
            .join(MotorBearing)
            .join(ExternalBearing)
            .join(TensionBearing)
            .join(UniformSpeedThreshold)
            .filter(
                Motor.category == "u3t",
                Motor.equipment_id == MotorBearing.equipment_id,
                Motor.number == MotorBearing.motor_number,
                Motor.equipment_id == ExternalBearing.equipment_id,
                Motor.number == ExternalBearing.motor_number,
                Motor.equipment_id == UniformSpeedThreshold.equipment_id,
                Motor.number == UniformSpeedThreshold.motor_number,
                Motor.equipment_id == TensionBearing.equipment_id,
                Motor.number == TensionBearing.motor_number,
                UniformSpeedThreshold.plc == plc,
                MotorBearing.plc == plc,
                ExternalBearing.plc == plc,
                TensionBearing.plc == plc,
                Motor.equipment_id == equipment_id,
                Motor.number == motor_number,
            )
        ).all()

    dict_list = row_to_dict(query_results)
    popped_column = ["id", "updated_time"]

    setting_client_param_list = []
    for _dict in dict_list:
        (
            equipment,
            motor,
            motor_bearing,
            external_bearing,
            tension_bearing,
            uniform_threshold,
        ) = (
            _dict["Equipment"],
            _dict["Motor"],
            _dict["MotorBearing"],
            _dict["ExternalBearing"],
            _dict["TensionBearing"],
            _dict["UniformSpeedThreshold"],
        )
        motor_bearing["motor_bearing_moving_median_sample_number"] = motor_bearing.pop(
            "moving_median_sample_number",
        )
        external_bearing[
            "external_bearing_moving_median_sample_number"
        ] = external_bearing.pop("moving_median_sample_number")
        tension_bearing[
            "tension_bearing_moving_median_sample_number"
        ] = tension_bearing.pop("moving_median_sample_number")
        equipment["equipment_name"] = equipment.pop("name")
        external_bearing["external_bearing_number"] = external_bearing.pop(
            "bearing_number",
        )
        tension_bearing["tension_bearing_number"] = tension_bearing.pop(
            "bearing_number",
        )
        setting_client_param_list.append(
            delete_key(
                equipment
                | motor
                | motor_bearing
                | external_bearing
                | tension_bearing
                | uniform_threshold,
                popped_column,
            ),
        )

    return [UniformSpeedMotor(**x) for x in setting_client_param_list][0]


def read_single_external_setting(
    equipment_id: int,
    motor_number: int,
    plc: int,
) -> UniformSpeedMotor:
    """GET /api/v1/setting-client/parameter api에서 사용되는 함수.

    현재 파일의 read_parameter_inquery 함수에서 사용되는 함수
    모터 카테고리가 u3e일때 사용됨

    Args:
        equipment_id (int): 모터 번호
        motor_number (int): 호기 번호
        plc (int): plc_model 값
    Returns:
        UniformSpeedMotor
    """
    with SessionLocal() as session:
        query_results = (
            session.query(
                Equipment,
                Motor,
                MotorBearing,
                ExternalBearing,
                UniformSpeedThreshold,
            )
            .select_from(Equipment)
            .join(Motor)
            .join(MotorBearing)
            .join(ExternalBearing)
            .join(UniformSpeedThreshold)
            .filter(
                Motor.category == "u3e",
                Motor.equipment_id == MotorBearing.equipment_id,
                Motor.number == MotorBearing.motor_number,
                Motor.equipment_id == ExternalBearing.equipment_id,
                Motor.number == ExternalBearing.motor_number,
                Motor.equipment_id == UniformSpeedThreshold.equipment_id,
                Motor.number == UniformSpeedThreshold.motor_number,
                UniformSpeedThreshold.plc == plc,
                MotorBearing.plc == plc,
                ExternalBearing.plc == plc,
                Motor.equipment_id == equipment_id,
                Motor.number == motor_number,
            )
        ).all()
    dict_list = row_to_dict(query_results)
    popped_column = ["id", "updated_time"]

    setting_client_param_list = []
    for _dict in dict_list:
        equipment, motor, motor_bearing, external_bearing, uniform_threshold = (
            _dict["Equipment"],
            _dict["Motor"],
            _dict["MotorBearing"],
            _dict["ExternalBearing"],
            _dict["UniformSpeedThreshold"],
        )
        equipment["equipment_name"] = equipment.pop("name")
        motor_bearing["motor_bearing_moving_median_sample_number"] = motor_bearing.pop(
            "moving_median_sample_number",
        )
        external_bearing[
            "external_bearing_moving_median_sample_number"
        ] = external_bearing.pop("moving_median_sample_number")
        external_bearing["external_bearing_number"] = external_bearing.pop(
            "bearing_number",
        )
        setting_client_param_list.append(
            delete_key(
                equipment
                | motor
                | motor_bearing
                | external_bearing
                | uniform_threshold,
                popped_column,
            ),
        )

    return [UniformSpeedMotor(**x) for x in setting_client_param_list][0]


def read_parameter_inquery(equipment_id: int, motor_number: int, plc: int) -> dict:
    """GET /api/v1/setting-client/parameter api에서 사용되는 함수.

    Args:
        equipment_id (int): 모터 번호
        motor_number (int): 호기 번호
        plc (int): plc_model 값
    Returns:
        dict
        ParameterSettingModel의 딕셔너리 형태와 같음
    """
    with SessionLocal() as session:
        category = (
            session.query(Motor.category).filter(
                Motor.equipment_id == equipment_id,
                Motor.number == motor_number,
            )
        ).first()[0]

        response: dict = defaultdict(dict)
        with PLCSessionLocal() as plcsession:
            name, description = (
                plcsession.query(PLCModel.name, PLCModel.description).filter(
                    PLCModel.model == plc,
                )
            ).first()

        response["model"] = {"model": plc, "name": name, "description": description}

        if category == "v3":
            vari_setting = read_single_variable_setting(
                equipment_id=equipment_id,
                motor_number=motor_number,
                plc=plc,
            ).dict()
            column_dict = {
                "Motor": [
                    "equipment_id",
                    "number",
                    "rated_current",
                    "pole",
                    "name",
                    "category",
                    "gear_ratio",
                    "max_current",
                ],
                "Variable": ["moving_median_sample_number"],
                "VariableSpeedThreshold": [
                    key for key in vari_setting if "current_" in key
                ],
            }
            response["motor"] = {key: vari_setting[key] for key in column_dict["Motor"]}
            response["parameter"] = {
                key: vari_setting[key] for key in column_dict["Variable"]
            }
            response["threshold"] = {
                key: vari_setting[key] for key in column_dict["VariableSpeedThreshold"]
            }

        elif category == "u3e":
            external_setting = read_single_external_setting(
                equipment_id=equipment_id,
                motor_number=motor_number,
                plc=plc,
            ).dict()
            column_dict = {
                "Motor": [
                    "equipment_id",
                    "number",
                    "rated_current",
                    "pole",
                    "name",
                    "category",
                    "gear_ratio",
                    "max_current",
                ],
                "MotorBearing": [
                    "supply_freq",
                    "motor_bearing_moving_median_sample_number",
                    "motor_bearing_ball_diameter",
                    "motor_bearing_ball_number",
                    "motor_bearing_pitch_diameter",
                ],
                "ExternalBearing": [
                    "external_bearing_moving_median_sample_number",
                    "external_bearing_ball_diameter",
                    "external_bearing_pitch_diameter",
                    "external_bearing_ball_number",
                    "external_bearing_number",
                ],
                "UniformSpeedThreshold": [
                    key
                    for key in external_setting
                    if (key.endswith("_warning") or key.endswith("_caution"))
                    and not key.startswith("tension_")
                ],
            }

            response["motor"] = {
                key: external_setting[key] for key in column_dict["Motor"]
            }
            response["parameter"] = {
                key: external_setting[key] for key in column_dict["MotorBearing"]
            } | {key: external_setting[key] for key in column_dict["ExternalBearing"]}
            response["threshold"] = {
                key: external_setting[key]
                for key in column_dict["UniformSpeedThreshold"]
            }
        elif category == "u3t":
            tension_setting = read_single_tension_setting(
                equipment_id=equipment_id,
                motor_number=motor_number,
                plc=plc,
            ).dict()
            column_dict = {
                "Motor": [
                    "equipment_id",
                    "number",
                    "rated_current",
                    "pole",
                    "name",
                    "category",
                    "gear_ratio",
                    "max_current",
                ],
                "MotorBearing": [
                    "supply_freq",
                    "motor_bearing_moving_median_sample_number",
                    "motor_bearing_ball_diameter",
                    "motor_bearing_ball_number",
                    "motor_bearing_pitch_diameter",
                ],
                "ExternalBearing": [
                    "external_bearing_moving_median_sample_number",
                    "external_bearing_ball_diameter",
                    "external_bearing_pitch_diameter",
                    "external_bearing_ball_number",
                    "external_bearing_number",
                ],
                "UniformSpeedThreshold": [
                    key
                    for key in tension_setting
                    if (key.endswith("_warning") or key.endswith("_caution"))
                ],
                "TensionBearing": [
                    key
                    for key in tension_setting
                    if key.startswith("tension_")
                    and not (key.endswith("_warning") or key.endswith("_caution"))
                    or key.startswith("tension_bearing_feature")
                ],
            }

            response["motor"] = {
                key: tension_setting[key] for key in column_dict["Motor"]
            }
            response["parameter"] = (
                {key: tension_setting[key] for key in column_dict["MotorBearing"]}
                | {key: tension_setting[key] for key in column_dict["ExternalBearing"]}
                | {key: tension_setting[key] for key in column_dict["TensionBearing"]}
            )
            response["threshold"] = {
                key: tension_setting[key]
                for key in column_dict["UniformSpeedThreshold"]
            }
    return response


def update_parameter_by_plc(body: dict) -> Optional[ParameterSettingModel]:
    """PUT /api/v1/setting-client/parameter api에서 사용되는 함수.

    Args:
        body (dict): setting client의 Parameter setting 부분에서의 body
    Note:
        body["model"]["model"] == 31로 적힌 부분은
        원래 고객사 측에서 세팅클라이언트를 사용할 때,
        원프레딕트가 설정한 기본 plc model값에 대한 파라미터는
        건드릴 수 없도록 설정하기 위해
        body["model"]["model"] == 3으로 설정하였으나,
        현장 구축 당시에 해당 부분 때문에 plc model값이 3일때
        업데이트할 수 없어서 저런 상태로
        수정되었음
    Returns:
        Optional[ParameterSettingModel]
    """
    # 1. body 정보로 plc를 조회했을 때,
    # 기본 모델(plc.model의 model이 1인 경우)은 수정 못하도록 바로 처리
    default_value = 31
    if body["model"]["model"] == default_value:
        logging.info("default는 수정할 수 없습니다")
        return None

    # 2. default가 아닌 plc의 경우 업데이트 진행
    category = body["motor"]["category"]
    aware_now = utc.localize(datetime.utcnow()).astimezone(  # noqa: DTZ003
        timezone(setting.timezone),
    )

    category_functions = {
        "u3e": update_uniform_parameter,
        "u3t": update_uniform_parameter,
        "v3": update_variable_parameter,
    }

    # PLC 부분 업데이트
    with PLCSessionLocal() as plcsession:
        plcsession.query(PLCModel).filter(
            PLCModel.model == body["model"]["model"],
            PLCModel.equipment_id == body["motor"]["equipment_id"],
        ).update(body["model"])
        category_functions[category](body, aware_now)
        plcsession.commit()
    return ParameterSettingModel(**body)


def update_uniform_parameter(body: dict, aware_now: datetime) -> None:
    """PUT /api/v1/setting-client/parameter api에서 사용되는 함수.

    현재 파일의 update_parameter_by_plc함수에서
    body의 모터 카테고리가 정속(u3e, u3t)일 때 사용됨.

    Args:
        body (dict): setting client의 Parameter setting 부분에서의 body
        aware_now (datetime): aware datetime 값
    """
    with SessionLocal() as session:
        session.query(Motor).filter(
            Motor.equipment_id == body["motor"]["equipment_id"],
            Motor.number == body["motor"]["number"],
        ).update(body["motor"] | {"updated_time": aware_now})

        motor_bearing = format_motor_bearing(body, aware_now)

        session.query(MotorBearing).filter(
            MotorBearing.equipment_id == body["motor"]["equipment_id"],
            MotorBearing.motor_number == body["motor"]["number"],
            MotorBearing.plc == body["model"]["model"],
        ).update(motor_bearing | {"updated_time": aware_now})

        external_bearing = format_external_bearing(body, aware_now)

        session.query(ExternalBearing).filter(
            ExternalBearing.equipment_id == body["motor"]["equipment_id"],
            ExternalBearing.motor_number == body["motor"]["number"],
            ExternalBearing.plc == body["model"]["model"],
        ).update(external_bearing | {"updated_time": aware_now})

        uniform_threshold = format_uniform_threshold(body, aware_now)

        session.query(UniformSpeedThreshold).filter(
            UniformSpeedThreshold.equipment_id == body["motor"]["equipment_id"],
            UniformSpeedThreshold.motor_number == body["motor"]["number"],
            UniformSpeedThreshold.plc == body["model"]["model"],
        ).update(uniform_threshold | {"updated_time": aware_now})

        # 텐션 베어링이 포함된 경우
        if "tension_bearing_number" in body["parameter"]:
            tension_bearing = format_tension_bearing(body, aware_now)
            session.query(TensionBearing).filter(
                TensionBearing.equipment_id == body["motor"]["equipment_id"],
                TensionBearing.motor_number == body["motor"]["number"],
                TensionBearing.plc == body["model"]["model"],
            ).update(tension_bearing | {"updated_time": aware_now})

        session.commit()


def update_variable_parameter(body: dict, aware_now: datetime) -> None:
    """PUT /api/v1/setting-client/parameter api에서 사용되는 함수.

    현재 파일의 update_parameter_by_plc함수에서
    body의 모터 카테고리가 변속(v3)일 때 사용됨.

    Args:
        body (dict): setting client의 Parameter setting 부분에서의 body
        aware_now (datetime): aware datetime 값
    """
    with SessionLocal() as session:
        session.query(Motor).filter(
            Motor.equipment_id == body["motor"]["equipment_id"],
            Motor.number == body["motor"]["number"],
        ).update(body["motor"] | {"updated_time": aware_now})

        variable_threshold = {
            key: body["threshold"][key]
            for key in body["threshold"]
            if not key.startswith("external_bearing")
        }
        session.query(VariableSpeedThreshold).filter(
            VariableSpeedThreshold.equipment_id == body["motor"]["equipment_id"],
            VariableSpeedThreshold.motor_number == body["motor"]["number"],
            VariableSpeedThreshold.plc == body["model"]["model"],
        ).update(variable_threshold | {"updated_time": aware_now})

        # parameter 업데이트
        session.query(Variable).filter(
            Variable.equipment_id == body["motor"]["equipment_id"],
            Variable.motor_number == body["motor"]["number"],
            Variable.plc == body["model"]["model"],
        ).update(body["parameter"] | {"updated_time": aware_now})

        session.commit()


def insert_variable_parameter(body: dict, aware_now: datetime) -> None:
    """POST /api/v1/setting-client/parameter api에서 사용되는 함수.

    현재 파일의 insert_parameter_by_plc함수에서
    body의 모터 카테고리가 변속(v3)일 때 사용됨.

    Args:
        body (dict): setting client의 Parameter setting 부분에서의 body
        aware_now (datetime): aware datetime 값
    """
    with SessionLocal():
        required_dict = generate_required_dict(body, aware_now)
        cls_format_dict = {
            Variable: (body["parameter"] | required_dict),
            VariableSpeedThreshold: (
                body["threshold"] | required_dict | {"phase_number": 3}
            ),
        }
        general_insert_multiple_value(SessionLocal, cls_format_dict)


def insert_uniform_parameter(body: dict, aware_now: datetime) -> None:
    """POST /api/v1/setting-client/parameter api에서 사용되는 함수.

    현재 파일의 insert_parameter_by_plc함수에서
    body의 모터 카테고리가 정속(u3e, u3t)일 때 사용됨.

    Args:
        body (dict): setting client의 Parameter setting 부분에서의 body
        aware_now (datetime): aware datetime 값
    """
    motor_bearing = format_motor_bearing(body, aware_now)
    external_bearing = format_external_bearing(body, aware_now)
    uniform_threshold = format_uniform_threshold(body, aware_now)
    if "tension_bearing_feature_warning" not in body["parameter"].keys():
        cls_format_dict = {
            MotorBearing: motor_bearing,
            ExternalBearing: external_bearing,
            UniformSpeedThreshold: uniform_threshold,
        }
        general_insert_multiple_value(SessionLocal, cls_format_dict)

    else:
        tension_bearing = format_tension_bearing(body, aware_now)

        cls_format_dict = {
            MotorBearing: motor_bearing,
            ExternalBearing: external_bearing,
            TensionBearing: tension_bearing,
            UniformSpeedThreshold: uniform_threshold,
        }
        general_insert_multiple_value(SessionLocal, cls_format_dict)


def unique_key_already_exists(
    SessionLocal: sessionmaker,
    class_type: DeclarativeMeta,
    key_value: dict,
) -> list[Row]:
    """중복된 키가 존재하는지 안하는지 확인하는 함수.

    Args:
        SessionLocal (sessionmaker): 세션 메이커 객체
        class_type (DeclarativeMeta): orm class
        key_value (dict): where문 조건으로 사용되는 값.
    """
    with SessionLocal() as session:
        query_results = session.query(class_type).filter_by(**key_value).all()
    return query_results


def delete_parameters_by_plc(
    SessionLocal: sessionmaker,
    class_type: DeclarativeMeta,
    plc: int,
) -> None:
    """DELETE /api/v1/setting-client/parameter api에서 사용되는 함수.

    Args:
        SessionLocal (sessionmaker): 세션 메이커 객체
        class_type (DeclarativeMeta): orm class
        plc (int): plc model 값
    """
    with SessionLocal() as session:
        if class_type.__name__ != "PLCModel":
            session.query(class_type).filter_by(**{"plc": plc}).delete()
        else:
            session.query(class_type).filter_by(**{"model": plc}).delete()
        session.commit()


def insert_parameter_by_plc(body: dict) -> Optional[ParameterSettingModel]:
    """POST /api/v1/setting-client/parameter api에서 사용되는 함수.

    Args:
        body (dict): setting client의 Parameter setting 부분에서의 body
    Returns:
        Optional[ParameterSettingModel]
    """
    category = body["motor"]["category"]
    if category != read_motor_category(
        body["motor"]["equipment_id"],
        body["motor"]["number"],
    ):

        real_category = read_motor_category(
            body["motor"]["equipment_id"],
            body["motor"]["number"],
        )
        raise HTTPException(
            status_code=403,
            detail=(
                f"해당 모터의 카테고리값이 DB에 들어있는 카테고리값과 다릅니다. {real_category} 카테고리로 수정해주세요."  # noqa: E501
            ),
        )

    aware_now = utc.localize(datetime.utcnow()).astimezone(  # noqa: DTZ003
        timezone(setting.timezone),
    )

    category_functions = {
        "u3e": insert_uniform_parameter,
        "u3t": insert_uniform_parameter,
        "v3": insert_variable_parameter,
    }

    required_dict = {
        "equipment_id": body["motor"]["equipment_id"],
        "motor_number": body["motor"]["number"],
        "plc": body["model"]["model"],
    }

    if "u3" in category:
        if unique_key_already_exists(SessionLocal, MotorBearing, required_dict):
            logging.info("해당 호기와 해당 모터 번호에 해당하는 모델 파라미터가 이미 존재합니다.")  # noqa: E501
            raise HTTPException(
                status_code=409,
                detail="해당 호기와 해당 모터 번호에 해당하는 모델 파라미터가 이미 존재합니다.",  # noqa: E501
            )

    elif unique_key_already_exists(SessionLocal, Variable, required_dict):
        logging.info("해당 호기와 해당 모터 번호에 해당하는 모델 파라미터가 이미 존재합니다.")  # noqa: E501
        raise HTTPException(
            status_code=409,
            detail="해당 호기와 해당 모터 번호에 해당하는 모델 파라미터가 이미 존재합니다.",  # noqa: E501
        )

    if unique_key_already_exists(
        PLCSessionLocal,
        PLCModel,
        {key: value for key, value in body["model"].items() if key == "model"},
    ):
        logging.info("모델 번호가 중첩됩니다.")
        raise HTTPException(status_code=409, detail=("PLC 모델 번호가 중첩됩니다."))

    try:
        # insert 함수 실행
        category_functions[category](body, aware_now)
    except Exception as err:
        logging.info("업데이트하려는 파라미터가 조건에 부합하지 않습니다.")
        raise HTTPException(
            status_code=403,
            detail=("업데이트하려는 파라미터가 조건에 부합하지 않습니다."),
        ) from err
    else:
        with PLCSessionLocal() as plcsession:
            plcsession.add(
                PLCModel(
                    **(
                        body["model"]
                        | {"line_id": 1, "equipment_id": required_dict["equipment_id"]}
                    ),
                ),
            )
            plcsession.commit()
            logging.info("모델별 파라미터 추가를 성공하였습니다.")
            return ParameterSettingModel(**body)


def view_memory_mapping(line_equipment: dict) -> list[dict]:
    """특정 라인번호, 호기 번호에 해당하는 memory mapping 테이블 row를 불러오는 함수.

    Args:
        line_equipment (dict): matching_equipment_id_using_equipment_name의 리턴값.
    """
    with PLCSessionLocal() as session:
        query_results = session.query(MemoryMapping).filter_by(**line_equipment).all()
    return row_to_dict(query_results)


def matching_equipment_id_using_equipment_name(equipment_name: str) -> dict:
    """PLC log를 insert할 때 사용되는 body에 적혀있는 key의 equipment_name을 기준으로.

    equipment table에서의 equipment_id와 line_id를 리턴하는 함수.

    Args:
        equipment_name(str): /setting-client/plc(POST)에서 사용되는
                            body의 key에 들어있는 equipment_name
    """
    with SessionLocal() as session:
        query_results = session.query(Equipment).all()

    equipment_table = row_to_dict(query_results)
    for equipment_row in equipment_table:
        if equipment_row["name"] == equipment_name:
            return {
                "equipment_id": equipment_row["id"],
                "line_id": equipment_row["line_id"],
            }
    return None  # type: ignore[return-value]
