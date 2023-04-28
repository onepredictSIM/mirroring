"""Define Database Model.

Motor를 중심으로 하는 Star Schema 구조를 채택
추가 설명 요청 시 description 개선 가능
- Author: Kibum Park
- Contact: kibum.park@onepredict.com
- Reference: https://onepredict.atlassian.net/wiki/spaces/PROD/pages/1247576300/LAMI2.LG-ES+ERD
             https://onepredict.atlassian.net/wiki/spaces/PROD/pages/1250754670/LAMI2.LG-ES.
"""

from db.table import Base
from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKeyConstraint,
    Integer,
    LargeBinary,
    String,
    UniqueConstraint,
)
from sqlalchemy.sql import func


class Line(Base):
    """라인 상태를 저장하는 테이블.

    Attributes:
        id: 라인 id
        category : 라미, 스태킹, 패키지 등의 분류
        name : 라인 이름.
    """

    __tablename__ = "line"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String, nullable=False)
    name = Column(String, nullable=False)


class Equipment(Base):
    """라인에 있는 호기 정보를 저장하는 테이블.

    Attributes:
        id: 호기 id
        line_id: 라인 id
        name : 호기 이름.
    """

    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, autoincrement=True)
    line_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)

    __table_args__: tuple = (
        ForeignKeyConstraint([line_id], [Line.id]),
        {},
    )


class Motor(Base):
    """모터 스펙의 현재 상태를 저장하는 테이블.

    Attributes:
        id: id
        equipment_id: 호기 id
        number : 특정 호기의 모터 번호
        updated_time : 모터 정보가 업데이트된 날짜
        name: 모터명
        category: 정속/변속(u/v), 단상/3상(1:3) 여부. ex) 정속 3상 = u3
        rated_current: 정격 전류
        supply_freq: 모터의 공급 주파수
        pole: 폴 수
        gear_ratio: 기어비
        max_current: 최대 전류
    """

    __tablename__ = "motor"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, nullable=False)
    number = Column(Integer, nullable=False)
    updated_time = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    rated_current = Column(Float, nullable=False)
    pole = Column(Integer)
    gear_ratio = Column(Float)
    max_current = Column(Float)

    __table_args__: tuple = (
        ForeignKeyConstraint(
            [equipment_id],
            [Equipment.id],
        ),
        UniqueConstraint("equipment_id", "number", name="equipment_id_motor_number"),
        {},
    )


class MotorBearing(Base):
    """모터 베어링 관련 스펙 및 파라미터 저장 테이블.

    Attributes:
        id: id
        plc: plc
        equipment_id: 호기 번호
        motor_number: 특정 호기의 모터 번호
        updated_time: 업데이트된 시간
        supply_freq: 공급 주파수
        moving_median_sample_number: 과거 N개 데이터 median
        motor_bearing_ball_diameter: 서보모터 베어링 볼 지름
        motor_bearing_pitch_diameter: 서보모터 베어링 피치 지름
        motor_bearing_ball_number: 서보모터 베어링 볼 개수
    """

    __tablename__ = "motor_bearing"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, nullable=False)
    motor_number = Column(Integer, nullable=False)
    plc = Column(Integer, nullable=False)
    updated_time = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    supply_freq = Column(Float, nullable=False)
    moving_median_sample_number = Column(Integer, nullable=False)
    motor_bearing_ball_diameter = Column(Float)
    motor_bearing_pitch_diameter = Column(Float)
    motor_bearing_ball_number = Column(Integer)

    __table_args__: tuple = (
        ForeignKeyConstraint(
            [equipment_id, motor_number],
            [Motor.equipment_id, Motor.number],
        ),
        UniqueConstraint(
            "equipment_id",
            "motor_number",
            "plc",
            name="motor_bearing_uk",
        ),
        {},
    )


class ExternalBearing(Base):
    """외부 베어링 관련 스펙 및 파라미터 저장 테이블.

    Attributes:
        id: id
        plc: plc
        equipment_id: 호기 번호
        motor_number: 특정 호기의 모터 번호
        updated_time: 업데이트된 시간
        supply_freq: 공급 주파수
        moving_median_sample_number: 과거 N개 데이터 median
        extenal_bearing_ball_diameter: 외부베어링 베어링 볼 지름
        extenal_bearing_pitch_diameter: 외부베어링 베어링 피치 지름
        extenal_bearing_ball_number: 외부베어링 베어링 볼 개수
    """

    __tablename__ = "external_bearing"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, nullable=False)
    motor_number = Column(Integer, nullable=False)
    plc = Column(Integer, nullable=False)
    updated_time = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    bearing_number = Column(Integer, nullable=False)
    moving_median_sample_number = Column(Integer, nullable=False)
    external_bearing_ball_diameter = Column(Float)
    external_bearing_pitch_diameter = Column(Float)
    external_bearing_ball_number = Column(Integer)
    external_bearing_feature_warning = Column(Float, nullable=False)
    external_bearing_feature_caution = Column(Float, nullable=False)

    __table_args__: tuple = (
        ForeignKeyConstraint(
            [equipment_id, motor_number],
            [Motor.equipment_id, Motor.number],
        ),
        UniqueConstraint(
            "equipment_id",
            "motor_number",
            "plc",
            name="external_bearing_uk",
        ),
        {},
    )


class TensionBearing(Base):
    """외부 베어링 관련 스펙 및 파라미터 저장 테이블.

    Attributes:
        id: id
        plc: plc
        equipment_id: 호기 번호
        motor_number: 특정 호기의 모터 번호
        updated_time: 업데이트된 시간
        supply_freq: 공급 주파수
        moving_median_sample_number: 과거 N개 데이터 median
        extenal_bearing_ball_diameter: 외부베어링 베어링 볼 지름
        extenal_bearing_pitch_diameter: 외부베어링 베어링 피치 지름
        extenal_bearing_ball_number: 외부베어링 베어링 볼 개수
    """

    __tablename__ = "tension_bearing"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, nullable=False)
    motor_number = Column(Integer, nullable=False)
    plc = Column(Integer, nullable=False)
    updated_time = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    bearing_number = Column(Integer, nullable=False)
    moving_median_sample_number = Column(Integer, nullable=False)
    tension_bearing_ball_diameter = Column(Float)
    tension_bearing_pitch_diameter = Column(Float)
    tension_bearing_ball_number = Column(Integer)
    tension_bearing_feature_warning = Column(Float, nullable=False)
    tension_bearing_feature_caution = Column(Float, nullable=False)

    __table_args__: tuple = (
        ForeignKeyConstraint(
            [equipment_id, motor_number],
            [Motor.equipment_id, Motor.number],
        ),
        UniqueConstraint(
            "equipment_id",
            "motor_number",
            "plc",
            name="tension_bearing_uk",
        ),
        {},
    )


class Variable(Base):
    """변속 모터 스펙 및 파라미터 저장하는 테이블.

    Attributes:
        id: id
        plc: plc
        equipment_id: 호기 번호
        motor_number: 특정 호기의 모터 번호
        updated_time: 업데이트된 시간
        moving_median_sample_number: 과거 N개 데이터 median
        template: 변속 템플릿
    """

    __tablename__ = "variable"

    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, nullable=False)
    motor_number = Column(Integer, nullable=False)
    plc = Column(Integer, nullable=False)
    updated_time = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    moving_median_sample_number = Column(Integer, nullable=False)
    template = Column(LargeBinary)

    __table_args__: tuple = (
        ForeignKeyConstraint(
            [equipment_id, motor_number],
            [Motor.equipment_id, Motor.number],
        ),
        UniqueConstraint("equipment_id", "motor_number", "plc", name="variable_uk"),
        {},
    )


class UniformSpeedThreshold(Base):
    """정속 threshold를 저장하는 테이블.

    Attributes:
        equipment_id: 호기 번호
        motor_number: 특정 호기의 모터 번호
        plc: plc
        updated_time:threshold 업데이트된 기록
        stator_feature_upper_warning: 고정자 고장 인자의 1차 상한
        stator_feature_upper_caution: 고정자 고장 인자의 2차 상한
        motor_bearing_feature_lower_warning: 내부 베어링 고장 인자의 1차 하한
        motor_bearing_feature_lower_caution: 내부 베어링 고장 인자의 2차 하한
        gear_feature_upper_warning: 기어 샤프트 고장 인자의 1차 상한
        gear_feature_upper_caution: 기어 샤프트 고장 인자의 2차 상한
        extenal_bearing_feature_upper_warning: 외부 베어링 고장 인자의 1차 상한
        extenal_bearing_feature_upper_caution: 외부 베어링 고장 인자의 2차 상한
    """

    __tablename__ = "uniform_speed_threshold"

    equipment_id = Column(Integer, primary_key=True)
    motor_number = Column(Integer, primary_key=True)
    plc = Column(Integer, primary_key=True)
    updated_time = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    stator_feature_warning = Column(Float, nullable=False)
    stator_feature_caution = Column(Float, nullable=False)
    motor_bearing_feature_warning = Column(Float, nullable=False)
    motor_bearing_feature_caution = Column(Float, nullable=False)
    gear_shaft_feature_warning = Column(Float, nullable=False)
    gear_shaft_feature_caution = Column(Float, nullable=False)
    coupling_feature_warning = Column(Float, nullable=False)
    coupling_feature_caution = Column(Float, nullable=False)
    belt_feature_warning = Column(Float, nullable=False)
    belt_feature_caution = Column(Float, nullable=False)
    __table_args__: tuple = (
        ForeignKeyConstraint(
            [equipment_id, motor_number],
            [Motor.equipment_id, Motor.number],
        ),
        UniqueConstraint(
            "equipment_id",
            "motor_number",
            "plc",
            name="uniform_threshold_uk",
        ),
        {},
    )


class VariableSpeedThreshold(Base):
    """변속 threshold를 저장하는 테이블.

    Attributes:
        equipment_id: 호기 번호
        motor_number: 특정 호기의 모터 번호
        plc: plc
        updated_time:threshold 업데이트된 기록
        phase_number: 단상/3상 여부
        current_corr_lower_warning: 전류 유사도의 1차 하한
        current_corr_lower_caution: 전류 유사도의 2차 하한
        current_noise_rms_upper_warning: 전류 노이즈 rms의 1차 상한
        current_noise_rms_upper_caution: 전류 노이즈 rms의 2차 싱한
        current_noise_rms_lower_warning: 전류 노이즈 rms의 1차 하한
        current_noise_rms_lower_caution: 전류 노이즈 rms의 2차 하한
    """

    __tablename__ = "variable_speed_threshold"

    equipment_id = Column(Integer, primary_key=True)
    motor_number = Column(Integer, primary_key=True)
    plc = Column(Integer, primary_key=True)
    updated_time = Column(DateTime(timezone=True), default=func.now(), nullable=False)
    phase_number = Column(Integer, nullable=False)
    current_corr_pvm_lower_warning = Column(Float, nullable=False)
    current_corr_pvm_lower_caution = Column(Float, nullable=False)
    current_noise_rms_upper_warning = Column(Float, nullable=False)
    current_noise_rms_upper_caution = Column(Float, nullable=False)
    current_noise_rms_lower_warning = Column(Float, nullable=False)
    current_noise_rms_lower_caution = Column(Float, nullable=False)

    __table_args__: tuple = (
        ForeignKeyConstraint(
            [equipment_id, motor_number],
            [Motor.equipment_id, Motor.number],
        ),
        UniqueConstraint(
            "equipment_id",
            "motor_number",
            "plc",
            name="variable_threshold_uk",
        ),
        {},
    )
