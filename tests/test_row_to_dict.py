import pickle
from pathlib import Path

from sqlalchemy.engine.row import Row
from util.utils import row_to_dict


def test_row_to_dict():
    file_path = Path("./tests/data_that_had_errors.pkl")

    with open(file_path, "rb") as f:
        errored_data: list[Row] = pickle.load(f)
        assert isinstance(errored_data, list)
        assert isinstance(errored_data[0], Row)
        dictionary_list = row_to_dict(errored_data)
        assert set(dictionary_list[0].keys()) == {
            "acq_time",
            "belt_diagnosis",
            "belt_kurtosis_max_median",
            "coupling_diagnosis",
            "coupling_supply_freq_amp_median",
            "equipment_id",
            "external_bearing_diagnosis",
            "external_bpfo_1x_median",
            "final_diagnosis",
            "gear_shaft_diagnosis",
            "gearbox_rotation_freq_amp_median",
            "motor_bearing_diagnosis",
            "motor_bpfi_1x_median",
            "motor_number",
            "plc",
            "rolling_load",
            "rolling_load_ratio",
            "signal_noise_ratio",
            "stator_diagnosis",
            "winding_supply_freq_amp_unbalance_ratio_median",
        }
