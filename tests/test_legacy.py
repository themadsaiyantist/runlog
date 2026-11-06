from legacy.old_best import best

HEADER = "run_id,date,model,learning_rate,epochs,val_accuracy,val_loss\n"


def test_old_best_ranks_as_its_docstring_says(tmp_path):
    path = tmp_path / "runs.csv"
    path.write_text(HEADER + "a,d,m,0.1,1,0.9,0.1\nb,d,m,0.1,1,0.89,0.1\n", encoding="utf-8")
    assert best(path)[0] == "a"   # 0.9 does win
    path.write_text(HEADER + "a,d,m,0.1,1,.9,0.1\nb,d,m,0.1,1,0.89,0.1\n", encoding="utf-8")
    assert best(path)[0] == "b"   # .9 loses to 0.89, compared as text
