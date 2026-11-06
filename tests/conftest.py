import pytest

ROWS = """run_id,date,model,learning_rate,epochs,val_accuracy,val_loss
r001,2026-09-01,resnet18,0.001,10,0.871,0.412
r002,2026-09-02,resnet18,0.0005,20,0.903,0.335
r003,2026-09-03,bert-base,0.00002,3,0.912,0.301
r004,2026-09-04,bert-base,0.00003,3,0.896,0.318
"""


@pytest.fixture
def runs_csv(tmp_path):
    path = tmp_path / "runs.csv"
    path.write_text(ROWS, encoding="utf-8")
    return path
