"""Define variable motor diagnosis api pydantic model.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com.
"""


from typing import Optional

from pydantic import BaseModel


class VariableDiagnosis(BaseModel):
    """변속 모터 진단 DTO 클래스.

    Attributes:
        acq_time : 얻은 시간(unix time)
        ad_coeff : current_corr_u
        ad_noise : current_noise_rms_u
        part : 파트
        name : 이름
        plc : plc 모드.
    """

    acq_time: Optional[list[str]] = None
    ad_coeff: Optional[list[float]] = None
    ad_noise: Optional[list[float]] = None
    part: Optional[str] = None
    name: Optional[str] = None
    plc: Optional[int] = None
