"""Define uniform diagnosis api pydantic model.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com.
"""


from typing import Optional

from pydantic import BaseModel


class UniformDiagnosis(BaseModel):
    """정속 모터 진단 인자 DTO 클래스.

    Attributes:
        acq_time : 얻은 시간(unix time)
        stator_result : stator_diagnosis
        b_g_result : motor_bearing_diagnosis
        gear_shaft_result : gear_shaft_diagnosis
        out_bear_result : pulley_bearing_diagnosis
        label : 라벨
        part : 파트
        name : 이름
        plc : plc 모드.
    """

    acq_time: Optional[list[str]] = None
    stator_result: Optional[list[int]] = None
    b_g_result: Optional[list[int]] = None
    gear_shaft_result: Optional[list[int]] = None
    out_bear_result: Optional[list[int]] = None
    label: Optional[str] = None
    part: Optional[str] = None
    name: Optional[str] = None
    plc: Optional[int] = None
