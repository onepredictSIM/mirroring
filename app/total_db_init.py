from core.config import setting
from core.logger import make_logger

logger = make_logger(__name__)


def servicedb_initialization_lami():
    from api.crud.util import general_insert_value_yaml
    from core.config import setting
    from db.service.database import SessionLocal, engine
    from db.service.model import (
        Base,
        Equipment,
        ExternalBearing,
        Line,
        Motor,
        MotorBearing,
        TensionBearing,
        UniformSpeedThreshold,
        Variable,
        VariableSpeedThreshold,
    )
    from sqlalchemy import create_engine
    from sqlalchemy_utils import create_database, database_exists

    if database_exists(setting.servicedb_uri):
        print("servicedb already exists")
        return

    if not database_exists(setting.servicedb_uri):
        create_database(setting.servicedb_uri)
    Base.metadata.create_all(bind=engine)

    cls_list = [
        Line,
        Equipment,
        Motor,
        MotorBearing,
        ExternalBearing,
        TensionBearing,
        UniformSpeedThreshold,
        Variable,
        VariableSpeedThreshold,
    ]

    for _cls in cls_list:
        print(_cls.__name__)
        general_insert_value_yaml(SessionLocal, _cls)


def featuredb_intialization_lami():
    from api.crud.util import general_insert_value_yaml
    from core.config import setting
    from db.feature.database import FeatureSessionLocal, engine
    from db.feature.model import (
        Base,
        Trigger,
        UniformSpeedExternalFeature,
        UniformSpeedTensionFeature,
        VariableSpeedPhase3Feature,
    )
    from sqlalchemy_utils import create_database, database_exists

    if database_exists(setting.featuredb_uri):
        print("featuredb already exists")
        return

    if not database_exists(setting.featuredb_uri):
        create_database(setting.featuredb_uri)
    Base.metadata.create_all(bind=engine)

    cls_list = [
        VariableSpeedPhase3Feature,
        # VariableSpeedPhase1Feature,
        UniformSpeedExternalFeature,
        UniformSpeedTensionFeature,
        # Trigger,
    ]

    for _cls in cls_list:
        print(_cls.__name__)
        general_insert_value_yaml(FeatureSessionLocal, _cls)


def metadatadb_initialization_dev():
    from core.config import setting
    from db.metadata.database import MetadataSessionLocal, engine
    from db.metadata.model import Base
    from sqlalchemy_utils import create_database, database_exists

    if database_exists(setting.metadatadb_uri):
        print("metadatadb already exists")
        return

    if not database_exists(setting.metadatadb_uri):
        create_database(setting.metadatadb_uri)
    Base.metadata.create_all(bind=engine)

    from datetime import datetime

    import numpy as np
    from pytz import timezone, utc
    from util.minio import connect_minio_resource, generate_minio_key, zstd_compress

    utc_naive_now = datetime.utcnow()
    utc_aware_now = utc.localize(utc_naive_now)
    kst_aware_now = utc.localize(utc_naive_now).astimezone(timezone("Europe/Warsaw"))
    acq_time = kst_aware_now

    # print(utc_naive_now)
    # print(utc_aware_now)
    # print(kst_aware_now)
    sampling_rate = 5000
    time_interval = 5

    s3 = connect_minio_resource()
    bucket_name = "lami"
    tmp_current = np.random.rand(sampling_rate * time_interval)
    zstd_current = zstd_compress(tmp_current)
    # print(acq_time)

    from api.crud.setting_client import read_total_motor_equipment

    target_keys = ("equipment_id", "number", "line_id")

    target_rows = [
        {key: value for key, value in row.dict().items() if key in target_keys}
        for row in read_total_motor_equipment()
    ]
    line_id_list = set([row["line_id"] for row in target_rows])
    equipment_id_list = set([row["equipment_id"] for row in target_rows])
    motor_number_list = set([row["number"] for row in target_rows])
    phase_list = ["u", "v", "w"]

    import urllib3
    from api.crud.util import general_insert_value
    from db.metadata.database import MetadataSessionLocal
    from db.metadata.model import MetaData

    urllib3.disable_warnings()
    import warnings

    warnings.filterwarnings(action="ignore")
    from datetime import timedelta

    for line_id in line_id_list:
        for equipment_id in equipment_id_list:
            for motor_number in motor_number_list:
                for phase in phase_list:
                    key = generate_minio_key(
                        line_id, equipment_id, motor_number, acq_time, phase
                    )
                    raw_data_dict = {
                        "line_id": line_id,
                        "equipment_id": equipment_id,
                        "motor_number": motor_number,
                        "phase": phase,
                        "acq_time": acq_time,
                        "file_path": key,
                        "sampling_rate": 5000,
                        "sample_size": 25000,
                    }
                    general_insert_value(MetadataSessionLocal, MetaData, raw_data_dict)
                    s3.Object(bucket_name, key).put(Body=zstd_current)


def servicedb_initialization() -> None:
    """Initializes the service database and the required tables.
    The service database initialization requires insertions of pre-defined rows.
    """
    from api.crud.util import general_insert_value_yaml
    from core.config import setting
    from db.service.database import SessionLocal, engine
    from db.service.not_lami.model import Base, Equipment, Line, Motor
    from sqlalchemy import create_engine
    from sqlalchemy_utils import create_database, database_exists

    if database_exists(setting.servicedb_uri):
        print("servicedb already exists")
        return

    if not database_exists(setting.servicedb_uri):
        create_database(setting.servicedb_uri)
    Base.metadata.create_all(bind=engine)

    cls_list = [
        Line,
        Equipment,
        Motor,
    ]

    for _cls in cls_list:
        print(_cls.__name__)
        general_insert_value_yaml(SessionLocal, _cls)


def metadatadb_initialization_lami():
    from core.config import setting
    from db.metadata.database import MetadataSessionLocal, engine
    from db.metadata.model import Base
    from sqlalchemy_utils import create_database, database_exists

    if database_exists(setting.metadatadb_uri):
        print("metadatadb already exists")
        return

    if not database_exists(setting.metadatadb_uri):
        create_database(setting.metadatadb_uri)
    Base.metadata.create_all(bind=engine)


def PLCDB_initialization_lami():
    from core.config import setting
    from db.plc.database import PLCSessionLocal, engine
    from db.plc.model import Base
    from sqlalchemy_utils import create_database, database_exists

    if database_exists(setting.plcdb_uri):
        print("plcdb already exists")
        return

    if not database_exists(setting.plcdb_uri):
        create_database(setting.plcdb_uri)
    Base.metadata.create_all(bind=engine)

    from api.crud.util import general_insert_value, general_insert_value_yaml
    from db.plc.database import PLCSessionLocal
    from db.plc.model import MemoryMapping, PLCLog, PLCModel

    cls_list = [PLCModel, MemoryMapping, PLCLog]

    for _cls in cls_list:
        print(_cls.__name__)
        general_insert_value_yaml(PLCSessionLocal, _cls)


def FDCDB_initialization_lami():
    from core.config import setting
    from db.fdc.database import FDCSessionLocal, engine
    from db.fdc.model import Base
    from sqlalchemy_utils import create_database, database_exists

    if database_exists(setting.fdcdb_uri):
        print("fdcdb already exists")
        return

    if not database_exists(setting.fdcdb_uri):
        create_database(setting.fdcdb_uri)
    Base.metadata.create_all(bind=engine)

    from datetime import datetime

    import yaml
    from api.crud.util import general_insert_value
    from db.fdc.database import FDCSessionLocal, engine
    from db.fdc.model import FDCConfig

    with open(f"./yaml/Config-{setting.line_num}.yml") as f:
        config = yaml.safe_load(f)[0]

    config.update({"id": 1})
    config.update({"updated_time": datetime.now()})

    general_insert_value(FDCSessionLocal, FDCConfig, config)


def main():
    if setting.bucket_name == "lami":
        servicedb_initialization_lami()
        featuredb_intialization_lami()
        metadatadb_initialization_lami()
        # metadatadb_initialization_dev()
        PLCDB_initialization_lami()
        FDCDB_initialization_lami()
    else:
        servicedb_initialization()
        metadatadb_initialization_lami()
        PLCDB_initialization_lami()


if __name__ == "__main__":
    cnt = 0

    # 최대 5회 시도
    while cnt != 5:
        tmp = cnt
        try:
            main()
        except Exception as e:
            logger.error(e)
            cnt += 1
        finally:
            # 생성됐으면 탈출 조건
            if cnt == tmp:
                break
            else:
                pass

    if cnt == 5:
        logger.error(f"The number of retrying to initialize db is {cnt}")

    else:
        logger.info(f"init db done")
