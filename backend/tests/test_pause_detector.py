from app.ml.pause_detector import PauseDetector


def test_commits_after_confirm_frames_of_the_same_sign():
    d = PauseDetector(confirm_frames=3, cooldown_frames=5)
    assert d.update("HELLO", True) is False
    assert d.update("HELLO", True) is False
    assert d.update("HELLO", True) is True  # third confident frame commits


def test_does_not_commit_on_disagreeing_frames():
    d = PauseDetector(confirm_frames=3)
    assert d.update("HELLO", True) is False
    assert d.update("WORLD", True) is False
    assert d.update("HELLO", True) is False  # window no longer unanimous


def test_low_confidence_and_placeholder_signs_reset_the_window():
    d = PauseDetector(confirm_frames=2)
    d.update("HELLO", True)
    assert d.update("HELLO", False) is False  # not confident → cleared
    assert d.update("HELLO", True) is False   # only one confident frame again
    assert d.update("HELLO", True) is True
    d.reset()
    d.update("A", True)
    assert d.update("?", True) is False  # placeholder clears


def test_cooldown_blocks_immediate_recommit_of_the_same_sign():
    d = PauseDetector(confirm_frames=2, cooldown_frames=5)
    assert d.update("HELLO", True) is False
    assert d.update("HELLO", True) is True   # first commit, cooldown = 5
    # holding the same sign must not re-commit while the cooldown is still active
    early = [d.update("HELLO", True) for _ in range(3)]
    assert True not in early
    # once the cooldown fully elapses, the same held sign can commit again
    later = [d.update("HELLO", True) for _ in range(3)]
    assert True in later


def test_a_different_sign_can_commit_during_the_first_signs_cooldown():
    d = PauseDetector(confirm_frames=2, cooldown_frames=10)
    d.update("HELLO", True)
    d.update("HELLO", True)  # commit HELLO
    assert d.update("BYE", True) is False
    assert d.update("BYE", True) is True  # different sign is not cooled down
