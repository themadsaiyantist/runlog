from sweeps.ids import run_id


def test_run_id_pads_to_three_digits():
    assert run_id(7) == "r007"
    assert run_id(123) == "r123"
