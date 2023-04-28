"""CRUD Util 모음.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
display num dict은 상세페이지에서 모터이름에 따른 디스플레이 순서를 담고 있는 변수이며,
싱글턴 패턴으로 정의되어있음.
STK, PKG 등이나 ESGM 때 수정되어야함.
"""
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, TypeVar, Union

import numpy as np
import yaml
from core.config import setting
from db.service.database import SessionLocal
from db.service.model import Equipment
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import sessionmaker

T = TypeVar("T")
display_num_dict = {
    "UpperElectrodeCuttingLinear": 1,
    "UpperElectrodeCutter": 2,
    "LowerElectrodeSeparatorNipRoller02": 3,
    "CenterElectrodeCuttingLinear": 1,
    "CenterElectrodeCutter": 2,
    "LowerElectrodeSeparatorNipRoller01": 3,
    "UpperLaminationRoller": 1,
    "LowerLaminationRoller": 2,
    "AxisSealingUpper": 3,
    "AxisSealingLower": 4,
    "CellCuttingLinear": 4,
    "CellCutter": 3,
    "UncutCellConveyor": 2,
    "CellConveyor": 1,
}


def merge_list_of_dictionary(dict_list: list[dict]) -> dict:
    """Merge all values from dict list into a single dict.

    Returns:
        dict
    """
    response = defaultdict(list)
    for _dict in dict_list:
        for key, value in _dict.items():
            if key == "acq_time":
                response[key].append(dt_to_unix(value))
            else:
                response[key].append(value)
    return response


def get_matching_part(
    part_motor_number_dict: dict[str, tuple[int]],
    motor_number: int,
) -> str:
    """모터 번호별로 어디 상세페이지에 속하는지 리턴해주는 함수.

    Args:
        part_motor_number_dict (dict[str, tuple[int]]):
                            상세페이지 파트별 모터 번호를 들고 있는 딕셔너리
        motor_number (int): 모터 번호
    Returns:
        str.
    """
    part_matching = {
        "pc": "lges.menu.positiveCutting",
        "nc": "lges.menu.negativeCutting",
        "lami": "lges.menu.laminationRoll",
        "fc": "lges.menu.finalCutting",
    }
    return part_matching[
        [key for key, value in part_motor_number_dict.items() if motor_number in value][
            0
        ]
    ]


def dt_to_unix(acq_time: datetime) -> str:
    """Datetime 객체를 unix time으로 변경.

    Args:
        acq_time (datetime): 계측 시간
    Returns:
        str
    """
    unix_timestamp = datetime.timestamp(acq_time) * 1000
    return str(unix_timestamp)


def get_equipment_name(equipment_id: int) -> str:
    """equipment_id를 이용하여 equipment_name을 조회하는 함수.

    13~14라인과 15라인의 모터 구성이 다르기 때문에 사용함.

    Args:
        equipment_id (int): 호기 번호
    Returns:
        str
    """
    with SessionLocal() as session:
        [name] = (
            session.query(Equipment.name).filter(Equipment.id == equipment_id).first()
        )

    return name


def get_detail_motor_number_list(equipment_name: str) -> dict[str, tuple[int, ...]]:
    """파트별 모터 리스트를 반환하는 함수.

    나중에 개선할 때에는 DB에 넣는 것이 바람직함.

    Args:
        equipment_name (str): 호기 이름
    Returns:
        Dict[str, Tuple[int]]:
    """
    line = equipment_name.split("-")[0]
    if line == "15":
        return {"pc": (3, 4), "nc": (1, 2), "lami": (5, 6), "fc": (7, 8, 9, 10)}
    else:
        return {
            "pc": (4, 5, 6),
            "nc": (1, 2, 3),
            "lami": (7, 8, 12, 13),
            "fc": (9, 10, 11, 14),
        }


def get_part_name(motor_param: dict[str, Union[str, int]]) -> str:
    """트렌드에서 파트 이름을 붙이기 위해 사용할 함수.

    나중에 개선할 때에는 DB에 넣는 것이 바람직함.

    Args:
        motor_param (dict[str, Union[str, int]]): 모터 파라미터.


    Returns:
        str
    """
    motor_number = motor_param["number"]
    equipment_name = motor_param["equipment_name"].split("-")[0]

    motor_mapping = {
        ("15", (3, 4)): "양극 커팅부",
        ("15", (1, 2)): "음극 커팅부",
        ("15", (5, 6)): "라미롤부",
        ("15", (7, 8, 9, 10)): "파이널 커팅부",
        ("13", (3, 4, 5)): "양극 커팅부",
        ("13", (1, 2, 6)): "음극 커팅부",
        ("13", (7, 8, 12, 13)): "라미롤부",
        ("13", (9, 10, 11, 14)): "파이널 커팅부",
        ("14", (3, 4, 5)): "양극 커팅부",
        ("14", (1, 2, 6)): "음극 커팅부",
        ("14", (7, 8, 12, 13)): "라미롤부",
        ("14", (9, 10, 11, 14)): "파이널 커팅부",
    }
    if (equipment_name, motor_number) in motor_mapping:
        return motor_mapping[(equipment_name, motor_number)]  # type: ignore[index]
    return ""


def determine_period(start: datetime, end: datetime) -> tuple[datetime, datetime]:
    """조회할 날짜 구간을 결정해주는 함수.

    Args:
        start (datetime): 조회 시작 시간
        end (datetime): 조회 끝 시간
    Returns:
        Tuple[datetime, datetime]
    """
    if end is None:
        end = datetime.now()  # noqa: DTZ005
        start = end - timedelta(days=30)
    else:
        pass
    return start, end


def general_insert_value(
    SessionLocal: sessionmaker,
    class_type: DeclarativeMeta,
    row: dict[str, Union[float, str]],
) -> None:
    """SessionLocal, ORM cls, row가 주어지면 해당 테이블에 데이터를 insert할 수 있는 함수.

    Args:
        SessionLocal (sessionmaker): *.db.database의 SessionLocal 객체
        class_type (DeclarativeMeta): 사용자 정의 sqlalchemy ORM 클래스,
                                    DB 테이블 이름과 동일
        row (Dict[str, Union[float, str]]): 테이블에 들어갈 값
    """
    row = class_type(**row)
    with SessionLocal() as session:
        session.begin()
        try:
            session.add(row)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            logging.error(e)
        except Exception as e:
            session.rollback()
            logging.error(e)


def general_insert_multiple_value(
    SessionLocal: sessionmaker,
    test_dict: dict[DeclarativeMeta, dict],
) -> None:
    """DB에 연결된 1개의 세션에서 여러 개의 insert가 수행되어야 하고.

    1개의 insert라도 실패할 경우 해당 세션에서 발생한 모든 insert를 취소하는 것을
    보장할 수 있는 함수.
    """
    with SessionLocal() as session:
        session.begin()
        try:
            for class_type, row in test_dict.items():
                session.add(class_type(**row))
        except:  # noqa: E722
            session.rollback()
        else:
            session.commit()


def load_variable_template(npy_file: str) -> bytes:
    """지정된 경로에 존재하는 npy 파일을 읽어서 bytes로 바꿔주는 함수.

    Note:
        general_insert_value_yaml함수와 주로 같이 쓰임

    Args:
        npy_file (str): 변속 템플릿 경로
    """
    template_current = np.load(npy_file)
    np_data = np.asarray(template_current, np.float64)
    binary_data = np_data.tobytes()
    return binary_data


def load_yaml_using_class_type(class_type: DeclarativeMeta) -> list[dict[str, Any]]:
    """Class 타입을 전달받아서 해당 클래스의 yaml 파일을 불러오는 함수.

    Note:
        general_insert_value_yaml함수와 주로 같이 쓰임
    Args:
        class_type (DeclarativeMeta): ORM class
    Return:
        List[Dict[str, Any]]
    """
    if setting.bucket_name == "lami":
        yaml_path = (
            f"./yaml/{setting.bucket_name}/{class_type.__name__}-{setting.line_num}.yml"
        )
    else:
        yaml_path = f"./yaml/{setting.bucket_name}/{class_type.__name__}.yml"
    with Path.open(yaml_path) as f:  # type: ignore[call-overload]
        row_list: list[dict[str, Any]] = yaml.safe_load(f)

    if class_type.__name__ == "Variable":
        for row in row_list:
            row["template"] = load_variable_template(row["template"])

    return row_list


def general_insert_value_yaml(
    SessionLocal: sessionmaker,
    class_type: DeclarativeMeta,
) -> None:
    """Yaml 파일 기반으로 DB 초기 세팅 하는 함수.

    Note:
        Variable.yml은 template 경로를 저장하고 있으므로,
        저장 경로를 이용하여 template 불러온 뒤에 DB에 넣어야함.


    Args:
        SessionLocal (sessionmaker): *.db.database의 SessionLocal 객체
        class_type (DeclarativeMeta): 사용자 정의 sqlalchemy ORM 클래스,
                                    DB 테이블 이름과 동일
    """
    row_list = load_yaml_using_class_type(class_type)

    for row in row_list:
        row_db = class_type(**row)
        with SessionLocal() as session:
            session.begin()
            session.add(row_db)
            session.commit()


def change_value_in_yaml(
    yaml_file_list: list[list[dict[str, Any]]],
    target_column: str,
    target_value: float,
) -> list[list[dict[str, Any]]]:
    """Yaml 파일 기반으로 특정 컬럼의 값을 특정 값으로 모두 업데이트 해주는 함수.

    Note:
        Variable.yml은 template 경로를 저장하고 있으므로,
        저장 경로를 이용하여 template 불러온 뒤에 DB에 넣어야함.


    Args:
        yaml_file_list (List[List[Dict[str,Any]]]):
            load_yaml_using_class_type()의 리턴 값을 주로 사용
        target_column (str): 특정 컬럼명
        target_value (float): 특정 값
    """
    for yaml_file in yaml_file_list:
        for row in yaml_file:
            row[target_column] = target_value
    return yaml_file_list


def update_variable_with_float_template(variable: dict) -> dict:
    """DB의 variable 테이블에 있는 template(bytes)을 3차원 전류 데이터로 변형.

    Args:
        variable (dict): 변속 모터 파라미터가 담긴 딕셔너리
    Returns:
        dict
    """
    import numpy as np

    template_uvw = np.frombuffer(variable["template"])
    template_uvw = np.frombuffer(variable["template"]).reshape(
        3,
        template_uvw.shape[0] // 3,
    )
    phases = ["template_u", "template_v", "template_w"]
    template_dict = {}
    for phase, template in zip(phases, template_uvw):
        template_dict[phase] = template.tolist()

    variable.pop("template")
    variable.update(template_dict)
    return variable
