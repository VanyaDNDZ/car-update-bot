import random
import string
from collections import OrderedDict

PREFILTERED = OrderedDict()


def generate_random_query_name():
    query_id = "".join([random.choice(string.ascii_letters) for _ in range(0, 10)])
    return "/query_" + query_id


def save_query(query):
    name = generate_random_query_name()
    while name in PREFILTERED:
        name = generate_random_query_name()
    if len(PREFILTERED.keys()) > 30:
        PREFILTERED.popitem(last=False)
    PREFILTERED.update({name: query})
    PREFILTERED.move_to_end(name)
    return name


def get_saved(name):
    return PREFILTERED.get(name)
