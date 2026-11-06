from sweeps.grid import expand


def test_expand_gives_every_combination():
    configs = expand({"a": [1, 2], "b": ["x", "y", "z"]})
    assert len(configs) == 6
    assert {"a": 2, "b": "z"} in configs


def test_expand_keeps_the_key_order():
    assert expand({"a": [1], "b": ["x"]})[0] == {"a": 1, "b": "x"}
