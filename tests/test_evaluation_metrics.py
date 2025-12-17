from evaluation.metrics import exact_match, contains_frac, length_ratio


def test_exact_match():
    assert exact_match("a b c", "a b c") == 1
    assert exact_match("abc", "a b c") == 0


def test_contains_frac():
    assert contains_frac("hello world", "hello") == 1.0
    assert contains_frac("hello there", "hello world") == 0.5


def test_length_ratio():
    assert length_ratio("helloworld", "hello") == 2.0
    assert length_ratio("", "hello") == 0.0
