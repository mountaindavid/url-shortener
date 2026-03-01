from app.shortcode import generate_short_code


def test_returns_string_of_default_length():
    code = generate_short_code()
    assert isinstance(code, str)
    assert len(code) == 5


def test_contains_only_alphanumeric():
    code = generate_short_code()
    assert code.isalnum()


def test_custom_length():
    code = generate_short_code(length=8)
    assert len(code) == 8

