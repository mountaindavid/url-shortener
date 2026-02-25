import random
import string
# from app.models import ShortUrl


def generate_short_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


# def is_short_code_unique(short_code: str):
#     return not ShortUrl.query.filter_by(short_code=short_code).first()