"""Run ids in the form runlog uses, r001 and up."""


def run_id(index: int) -> str:
    return f"r{index:03d}"
