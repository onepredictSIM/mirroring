"""Define dashboard api pydantic model.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""


from pydantic import BaseModel


class UniformDashboard(BaseModel):
    """정속 대쉬보드 DTO 클래스.

    Attributes:
        acq_time : 얻은 시간(unix time)
        b_g_result : motor_bearing_diagnosis
        gear_shaft_result : gear_shaft_diagnosis
        out_bear_result : pulley_bearing_diagnosis
        ad_result : final_diagnosis
        part : 파트
        name : 이름
        plc : plc 모드
    """

    acq_time: str = None
    b_g_result: int = None
    gear_shaft_result: int = None
    out_bear_result: int = None
    ad_result: int = None
    part: str = None
    name: str = None
    plc: int = None


class VariableDashboard(BaseModel):
    """변속 대쉬보드 DTO 클래스.

    Attributes:
        acq_time : 얻은 시간(unix time)
        ad_result : final_diagnosis
        part : 파트
        name : 이름
        plc : plc 모드
    """

    acq_time: str = None
    ad_result: int = None
    part: str = None
    name: str = None
    plc: int = None
