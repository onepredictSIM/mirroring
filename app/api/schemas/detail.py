"""DetailInitAPI와 관련된 모듈 모음.

- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
"""
from api.crud.detail import MotorInfo
from api.crud.util import (
    display_num_dict,
    get_detail_motor_number_list,
    get_equipment_name,
)
from api.format.detail import parse_for_detail_init
from schemas.detail import DetailInitFactory


class DetailInitAPIFactory:
    """상세페이지 init API를 생산하는 팩토리 클래스.

    Note:
        schemas.detail 참고
    """

    def __init__(self, equipment_id: int, part_name: str) -> None:
        """호기 번호와 파트 이름을 통해 팩토리 객체 생성.

        Args:
            equipment_id (int):호기 번호
            part_name (str): 파트 이름
        """
        self.equipment_id = equipment_id
        self.part_name = part_name

    def init_api(self) -> dict:
        """호기번호와 파트이름을 통해 API를 쉽게 생성하며, 엔드포인트에서 depends로 관리.

        Returns:
            dict
        """
        equipment_name = get_equipment_name(self.equipment_id)
        motor_number_list = get_detail_motor_number_list(equipment_name)[self.part_name]
        response = {}
        for motor_number in motor_number_list:
            str_mtr_id = "".join(("motor", str(motor_number)))
            motor_info = MotorInfo(self.equipment_id, motor_number)
            motor_param = motor_info.read_motor_parameter()
            response[str_mtr_id] = parse_for_detail_init(motor_param)
            detail_init = DetailInitFactory.create_detail(
                response[str_mtr_id]["category"],
            )
            response[str_mtr_id].update(detail_init.dict())

        for motor_number in response:
            for key, value in display_num_dict.items():
                if key in response[motor_number]["name"]:
                    response[motor_number]["display_num"] = value
        return response
