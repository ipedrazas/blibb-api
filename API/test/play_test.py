
from random import  sample
from string import digits, ascii_letters


def short_id(num):
    return "".join(sample(digits + ascii_letters, num))


print short_id(5)
