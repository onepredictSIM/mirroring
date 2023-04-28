"""Pre-Processing data before sending API.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
import re
from datetime import datetime

from db.service.database import SessionLocal
from db.service.model import Motor


def dt_to_unix(acq_time: datetime) -> str:
    """Datetime 객체를 unix time으로 변경해주는 함수.

    Args:
        acq_time (datetime): 계측된 시간

    Returns:
        str
    """
    unix_timestamp = datetime.timestamp(acq_time) * 1000
    return str(unix_timestamp)


def line_mtr_name(equipment_id: int, str_motor_number: str) -> str:
    """DB에 저장된 모터의 이름을 반환하는 함수.

    Args:
        equipment_id (int): 호기 번호
        str_motor_number (str): 모터 번호
    Returns:
        str
    """
    motor_number = int(re.sub(r"[^0-9]", "", str_motor_number))
    with SessionLocal() as session:
        query_results = (
            session.query(Motor.name)
            .filter(Motor.equipment_id == equipment_id, Motor.number == motor_number)
            .first()
        )

    motor_name = query_results[0]
    return motor_name
