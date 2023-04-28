"""현재 plc 상태를 불러오는 함수.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
import logging

from db.plc.database import PLCSessionLocal
from db.plc.model import MemoryMapping, PLCLog


def load_current_plc_model(line_equipment: dict) -> int:
    """현재 plc 모델 상태를 불러오는 함수.

    Args:
        line_equipment (dict): 라인 번호, 호기 번호, "CellState_Model"을 포함한 딕셔너리
    Returns:
        int, 현재 plc 정보
    """
    with PLCSessionLocal() as session:
        mm_id = (session.query(MemoryMapping.id).filter_by(**line_equipment)).first()[0]
        query_result = (
            session.query(PLCLog.value)
            .filter_by(**{"mm_id": mm_id})
            .order_by(PLCLog.id.desc())
            .limit(1)
            .first()[0]
        )
        if not query_result:
            logging.error(
                "현재 plc 모델에 대한 정보가 빈 값으로 나옵니다. 디폴트 모델 값으로 설정합니다.",  # noqa: E501
            )
            return 3

        return int(query_result)
