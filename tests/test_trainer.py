from sweeps.trainer import train


def test_train_is_deterministic():
    config = {"model": "resnet18", "learning_rate": 0.001, "epochs": 10}
    assert train(config, 42) == train(config, 42)


def test_train_scores_stay_in_range():
    result = train({"model": "resnet50", "learning_rate": 0.1, "epochs": 3}, 1)
    assert 0.0 <= result.val_accuracy <= 0.99
    assert result.val_loss >= 0.02
