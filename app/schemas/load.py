"""Define uniform load api pydantic model.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com.
"""


from typing import Optional

from pydantic import BaseModel


class UniformLoad(BaseModel):
    """정속 모터 부하 인자 DTO 클래스.

    Attributes:
        acq_time : 얻은 시간(unix time)
        rolling_load : 회전 부하율
        label : 라벨
        part : 파트
        name : 이름
        plc : plc 모드.
    """

    acq_time: Optional[list[str]] = None
    rolling_load: Optional[list[float]] = None
    label: Optional[str] = None
    part: Optional[str] = None
    name: Optional[str] = None
    plc: Optional[int] = None


class VariableLoad(BaseModel):
    """변속 모터 부하 인자 DTO 클래스.

    Attributes:
        acq_time : 얻은 시간(unix time)
        cutting_load1 : avg_load
        cutting_load2 : peak_load
        label : 라벨
        part : 파트
        name : 이름
        plc : plc 모드.
    """

    acq_time: Optional[list[str]] = None
    cutting_load1: Optional[list[float]] = None
    cutting_load2: Optional[list[float]] = None
    label: Optional[str] = None
    part: Optional[str] = None
    name: Optional[str] = None
    plc: Optional[int] = None
