"""Define LGES_Data Database Model.

Motor를 중심으로 하는 Star Schema 구조를 채택
추가 설명 요청 시 description 개선 가능
- Author: Sewon Kim
- Contact: sewon.kim@onepredict.com
- Reference: https://onepredict.atlassian.net/wiki/spaces/PROD/pages/1275167027/LAMI2.LG-ES+ERD
"""

from db.table import Base
from sqlalchemy import Column, DateTime, Float, Integer
from sqlalchemy.sql import func


class Trigger(Base):
    """진단 여부와 상관없이 전류 데이터에 대한 운행 판단 로직 상태 정보를 기록하는 테이블.

    참고 문서:
        [LGES.ESWA][PS-416] PLC 장비 RUN Trigger 기반 진단 로직 개발

    Attributes:
        equipment_id: 호기 번호
        motor_number: 모터 번호
        acq_time: 계측 시간
        plc: 배터리 셀 생산 모드 정보
        status: 정속/변속 판단 알고리즘 상태
        plc_status: plc 상태
        supply_freq_by_data: 공급 주파수.
        rms_u: rms_u 값
    """

    __tablename__ = "trigger"

    equipment_id = Column(Integer, primary_key=True)
    motor_number = Column(Integer, primary_key=True)
    acq_time = Column(DateTime(timezone=True), default=func.now(), primary_key=True)
    plc = Column(Integer, primary_key=True)
    status = Column(Integer, nullable=False)
    plc_status = Column(Integer, nullable=False)
    supply_freq_by_data = Column(Float, nullable=False)
    rms_u = Column(Float, nullable=False)


class UniformSpeedExternalFeature(Base):
    """텐션 베어링 포함되지 않은 정속 모터 특성인자 테이블(외부베어링 1개).

    Attributes:
        equipment_id: 호기 id
        motor_number: 호기당 모터 id
        acq_time: 데이터 취득 시간
        rolling_load: 회전 부하율
        signal_noise_ratio: SNR
        supply_freq_amp_unbalance: 3상의 FFT의 공급 주파수 세기의 불균형
        rotation_freq_amp_pvm: pvm FFT의 회전 주파수 세기
        gear_freq_amp_pvm: pvm FFT의 기어 주파수 세기
        external_bearing_feature: 추 후 수정 예정
        supply_freq_amp_unbalance_median: 3상의 FFT의 공급 주파수 세기의 불균형
                                        최근 sample_number의 중위값
        rotation_freq_amp_pvm_median: pvm FFT의 회전 주파수 세기
                                    최근 sample_number의 중위값
        gear_freq_amp_pvm_median: pvm FFT의 기어 주파수 세기 최근 sample_number의 중위값
        external_bearing_feature_median: 추 후 수정 예정
        stator_diagnosis: 고정자 진단 결과(supply_freq_amp_unbalance_median)
        gear_shaft_diagnosis: 기어 샤프트 진단 결과(gear_freq_amp_pvm_median)
        motor_bearing_diagnosis: 내부 베어링 진단 결과(rotation_freq_amp_pvm_median)
        external_bearing_diagnosis: 외부 베어링 진단 결과(추 후 수정 예정)
        final_diagnosis: 최종 진단 결과
    """

    __tablename__ = "uniform_speed_external_feature"

    equipment_id = Column(Integer, primary_key=True)
    motor_number = Column(Integer, primary_key=True)
    acq_time = Column(DateTime(timezone=True), default=func.now(), primary_key=True)
    plc = Column(Integer, primary_key=True)
    rms_u = Column(Float, nullable=False)
    rms_v = Column(Float, nullable=False)
    rms_w = Column(Float, nullable=False)
    rms_pvm = Column(Float, nullable=False)
    kurtosis_u = Column(Float, nullable=False)
    kurtosis_v = Column(Float, nullable=False)
    kurtosis_w = Column(Float, nullable=False)
    external_bpfo_1x = Column(Float, nullable=False)
    external_bpfo_2x = Column(Float, nullable=False)
    external_bpfo_3x = Column(Float, nullable=False)
    external_bpfo_4x = Column(Float, nullable=False)
    external_bpfo_5x = Column(Float, nullable=False)
    external_bpfi_1x = Column(Float, nullable=False)
    external_bpfi_2x = Column(Float, nullable=False)
    external_bpfi_3x = Column(Float, nullable=False)
    external_bpfi_4x = Column(Float, nullable=False)
    external_bpfi_5x = Column(Float, nullable=False)
    motor_bpfo_1x = Column(Float, nullable=False)
    motor_bpfo_2x = Column(Float, nullable=False)
    motor_bpfo_3x = Column(Float, nullable=False)
    motor_bpfo_4x = Column(Float, nullable=False)
    motor_bpfo_5x = Column(Float, nullable=False)
    motor_bpfi_1x = Column(Float, nullable=False)
    motor_bpfi_2x = Column(Float, nullable=False)
    motor_bpfi_3x = Column(Float, nullable=False)
    motor_bpfi_4x = Column(Float, nullable=False)
    motor_bpfi_5x = Column(Float, nullable=False)

    signal_noise_ratio = Column(Float, nullable=False)
    rolling_load_ratio = Column(Float, nullable=False)
    rolling_load = Column(Float, nullable=False)

    winding_supply_freq_amp_unbalance_ratio = Column(Float, nullable=False)
    winding_supply_freq_amp_unbalance_ratio_median = Column(Float, nullable=False)
    motor_bpfi_1x_median = Column(Float, nullable=False)
    gearbox_rotation_freq_amp = Column(Float, nullable=False)
    gearbox_rotation_freq_amp_median = Column(Float, nullable=False)
    external_bpfo_1x_median = Column(Float, nullable=False)
    coupling_supply_freq_amp = Column(Float, nullable=False)
    coupling_supply_freq_amp_median = Column(Float, nullable=False)
    belt_kurtosis_max = Column(Float, nullable=False)
    belt_kurtosis_max_median = Column(Float, nullable=False)

    stator_diagnosis = Column(Integer, nullable=False)
    motor_bearing_diagnosis = Column(Integer, nullable=False)
    gear_shaft_diagnosis = Column(Integer, nullable=False)
    external_bearing_diagnosis = Column(Integer, nullable=False)
    coupling_diagnosis = Column(Integer, nullable=False)
    belt_diagnosis = Column(Integer, nullable=False)
    final_diagnosis = Column(Integer, nullable=False)


class UniformSpeedTensionFeature(Base):
    """텐션 베어링 포함된 정속 모터 특성인자 테이블(외부베어링 2개).

    Attributes:
        equipment_id: 호기 id
        motor_number: 호기당 모터 id
        acq_time: 데이터 취득 시간
        rolling_load: 회전 부하율
        signal_noise_ratio: SNR
        supply_freq_amp_unbalance: 3상의 FFT의 공급 주파수 세기의 불균형
        rotation_freq_amp_pvm: pvm FFT의 회전 주파수 세기
        gear_freq_amp_pvm: pvm FFT의 기어 주파수 세기
        external_bearing_feature: 추 후 수정 예정
        supply_freq_amp_unbalance_median: 3상의 FFT의 공급 주파수 세기의 불균형
                                        최근 sample_number의 중위값
        rotation_freq_amp_pvm_median: pvm FFT의 회전 주파수 세기
                                    최근 sample_number의 중위값
        gear_freq_amp_pvm_median: pvm FFT의 기어 주파수 세기 최근 sample_number의 중위값
        external_bearing_feature_median: 추 후 수정 예정
        stator_diagnosis: 고정자 진단 결과(supply_freq_amp_unbalance_median)
        gear_shaft_diagnosis: 기어 샤프트 진단 결과(gear_freq_amp_pvm_median)
        motor_bearing_diagnosis: 내부 베어링 진단 결과(rotation_freq_amp_pvm_median)
        external_bearing_diagnosis: 외부 베어링 진단 결과(추 후 수정 예정)
        final_diagnosis: 최종 진단 결과
    """

    __tablename__ = "uniform_speed_tension_feature"

    equipment_id = Column(Integer, primary_key=True)
    motor_number = Column(Integer, primary_key=True)
    acq_time = Column(DateTime(timezone=True), default=func.now(), primary_key=True)
    plc = Column(Integer, primary_key=True)
    rms_u = Column(Float, nullable=False)
    rms_v = Column(Float, nullable=False)
    rms_w = Column(Float, nullable=False)
    rms_pvm = Column(Float, nullable=False)
    kurtosis_u = Column(Float, nullable=False)
    kurtosis_v = Column(Float, nullable=False)
    kurtosis_w = Column(Float, nullable=False)
    external_bpfo_1x = Column(Float, nullable=False)
    external_bpfo_2x = Column(Float, nullable=False)
    external_bpfo_3x = Column(Float, nullable=False)
    external_bpfo_4x = Column(Float, nullable=False)
    external_bpfo_5x = Column(Float, nullable=False)
    external_bpfi_1x = Column(Float, nullable=False)
    external_bpfi_2x = Column(Float, nullable=False)
    external_bpfi_3x = Column(Float, nullable=False)
    external_bpfi_4x = Column(Float, nullable=False)
    external_bpfi_5x = Column(Float, nullable=False)
    tension_bpfo_1x = Column(Float, nullable=False)
    tension_bpfo_2x = Column(Float, nullable=False)
    tension_bpfo_3x = Column(Float, nullable=False)
    tension_bpfo_4x = Column(Float, nullable=False)
    tension_bpfo_5x = Column(Float, nullable=False)
    tension_bpfi_1x = Column(Float, nullable=False)
    tension_bpfi_2x = Column(Float, nullable=False)
    tension_bpfi_3x = Column(Float, nullable=False)
    tension_bpfi_4x = Column(Float, nullable=False)
    tension_bpfi_5x = Column(Float, nullable=False)
    motor_bpfo_1x = Column(Float, nullable=False)
    motor_bpfo_2x = Column(Float, nullable=False)
    motor_bpfo_3x = Column(Float, nullable=False)
    motor_bpfo_4x = Column(Float, nullable=False)
    motor_bpfo_5x = Column(Float, nullable=False)
    motor_bpfi_1x = Column(Float, nullable=False)
    motor_bpfi_2x = Column(Float, nullable=False)
    motor_bpfi_3x = Column(Float, nullable=False)
    motor_bpfi_4x = Column(Float, nullable=False)
    motor_bpfi_5x = Column(Float, nullable=False)

    signal_noise_ratio = Column(Float, nullable=False)
    rolling_load_ratio = Column(Float, nullable=False)
    rolling_load = Column(Float, nullable=False)

    winding_supply_freq_amp_unbalance_ratio = Column(Float, nullable=False)
    winding_supply_freq_amp_unbalance_ratio_median = Column(Float, nullable=False)
    motor_bpfi_1x_median = Column(Float, nullable=False)
    gearbox_rotation_freq_amp = Column(Float, nullable=False)
    gearbox_rotation_freq_amp_median = Column(Float, nullable=False)
    external_bpfo_1x_median = Column(Float, nullable=False)
    tension_bpfo_1x_median = Column(Float, nullable=False)
    coupling_supply_freq_amp = Column(Float, nullable=False)
    coupling_supply_freq_amp_median = Column(Float, nullable=False)
    belt_kurtosis_max = Column(Float, nullable=False)
    belt_kurtosis_max_median = Column(Float, nullable=False)

    stator_diagnosis = Column(Integer, nullable=False)
    motor_bearing_diagnosis = Column(Integer, nullable=False)
    gear_shaft_diagnosis = Column(Integer, nullable=False)
    external_main_bearing_diagnosis = Column(Integer, nullable=False)
    external_tension_bearing_diagnosis = Column(Integer, nullable=False)
    coupling_diagnosis = Column(Integer, nullable=False)
    belt_diagnosis = Column(Integer, nullable=False)
    final_diagnosis = Column(Integer, nullable=False)


class VariableSpeedPhase1Feature(Base):
    """단상 변속 모터 특성인자 테이블.

    Attributes:
        equipment_id: 호기 id
        motor_number: 호기당 모터 id
        acq_time: 데이터 취득 시간
        avg_load: 평균 부하율
        peak_load: 최대 부하율
        cutting_interval: cutting간 시간 간격
        current_corr_u: u상 전류 유사도
        current_noise_rms_u: u상 전류 노이즈 rms
        current_corr_u_median: u상 전류 유사도 최근 sample_number의 중위값
        current_noise_rms_u_median: u상 전류 노이즈 rms 최근 sample_number의 중위값
        current_corr_u_diagnosis: u상 전류 유사도 진단 결과
        current_noise_rms_u_diagnosis: u상 전류 노이즈 rms 진단 결과
        final_diagnosis: 최종 진단 결과
    """

    __tablename__ = "variable_speed_phase1_feature"

    equipment_id = Column(Integer, primary_key=True)
    motor_number = Column(Integer, primary_key=True)
    acq_time = Column(DateTime(timezone=True), default=func.now(), primary_key=True)
    plc = Column(Integer, primary_key=True)
    avg_load = Column(Float, nullable=False)
    peak_load = Column(Float, nullable=False)
    cutting_interval = Column(Float, nullable=False)
    current_corr_u = Column(Float, nullable=False)
    current_noise_rms_u = Column(Float, nullable=False)
    current_corr_u_median = Column(Float, nullable=False)
    current_noise_rms_u_median = Column(Float, nullable=False)
    current_corr_u_diagnosis = Column(Integer, nullable=False)
    current_noise_rms_u_diagnosis = Column(Integer, nullable=False)
    final_diagnosis = Column(Integer, nullable=False)


class VariableSpeedPhase3Feature(Base):
    """3상 변속 모터 특성인자 테이블.

    Attributes:
        equipment_id: 호기 id
        motor_number: 호기당 모터 id
        acq_time: 데이터 취득 시간
        avg_load: 평균 부하율
        peak_load: 최대 부하율
        cutting_interval: cutting간 시간 간격
        current_corr_u: u상 전류 유사도
        current_noise_rms_u: u상 전류 노이즈 rms
        current_corr_v: v상 전류 유사도
        current_noise_rms_v: v상 전류 노이즈 rms
        current_corr_w: w상 전류 유사도
        current_noise_rms_w: w상 전류 노이즈 rms
        current_corr_pvm: pvm: 전류 유사도
        current_noise_rms_pvm: pvm 전류 노이즈 rms
        current_corr_pvm_median: pvm 전류 유사도 최근 sample_number의
                                최근 sample_number의 중위값
        current_noise_rms_pvm_median: pvm 전류 노이즈 rms 최근 sample_number의
                                    최근 sample_number의 중위값
        current_corr_pvm_diagnosis: pvm 전류 유사도 진단 결과
        current_noise_rms_pvm_diagnosis: pvm 전류 노이즈 rms 진단 결과
        final_diagnosis: 최종 진단 결과
    """

    __tablename__ = "variable_speed_phase3_feature"

    equipment_id = Column(Integer, primary_key=True)
    motor_number = Column(Integer, primary_key=True)
    acq_time = Column(DateTime(timezone=True), default=func.now(), primary_key=True)
    plc = Column(Integer, primary_key=True)
    avg_load = Column(Float, nullable=False)
    peak_load = Column(Float, nullable=False)
    avg_load_ratio = Column(Float, nullable=False)
    peak_load_ratio = Column(Float, nullable=False)
    cutting_interval = Column(Float, nullable=False)
    current_corr_pvm = Column(Float, nullable=False)
    current_noise_rms_pvm = Column(Float, nullable=False)
    current_corr_pvm_median = Column(Float, nullable=False)
    current_noise_rms_pvm_median = Column(Float, nullable=False)
    current_corr_pvm_diagnosis = Column(Integer, nullable=False)
    current_noise_rms_pvm_diagnosis = Column(Integer, nullable=False)
    final_diagnosis = Column(Integer, nullable=False)
