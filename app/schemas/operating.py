"""Define operating api pydantic model.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com.
"""


from typing import Optional

from pydantic import BaseModel


class UniformOperating(BaseModel):
    """정속 모터 운영 인자 DTO 클래스.

    Attributes:
        motor_id : 모터 아이디
        acq_time : 얻은 시간(unix time)
        snr : snr
        label : 라벨
        part : 파트
        name : 이름
        plc : plc 모드.
    """

    acq_time: Optional[list[str]] = None
    snr: Optional[list[float]] = None
    label: Optional[str] = None
    part: Optional[str] = None
    name: Optional[str] = None
    plc: Optional[int] = None


class VariableOperating(BaseModel):
    """변속 모터 운영 인자 DTO 클래스.

    Attributes:
        motor_id : 모터 아이디
        acq_time : 얻은 시간(unix time)
        c2c : 커팅 시간
        label : 라벨
        part : 파트
        name : 이름
        plc : plc 모드.
    """

    acq_time: Optional[list[str]] = None
    c2c: Optional[list[float]] = None
    label: Optional[str] = None
    part: Optional[str] = None
    name: Optional[str] = None
    plc: int
