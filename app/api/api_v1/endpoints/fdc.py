"""fdc와 관련된 API 모음.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
from datetime import datetime

from api.crud.setting_client import read_feature_by_acq_time
from fastapi import APIRouter

router = APIRouter()


@router.get("/fdc-feature")
def load_fdc_feature(equipment_id: int, motor_number: int, acq_time: datetime) -> dict:
    """Fdc feature를 읽어오는 api, deprecated."""
    return read_feature_by_acq_time(equipment_id, motor_number, acq_time)[0]
