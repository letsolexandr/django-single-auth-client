import collections

from django.conf import settings
from django.core import signing


def check_authorization(f):
    def wrapper(*args):
        print(args[0].url)
        return f(*args)

    return wrapper


def encrypt_data(data):
    return signing.dumps(data, key=settings.AUTH_SERVER_SECRET_KEY)


def decrypt_data(data):
    return signing.loads(data, key=settings.AUTH_SERVER_SECRET_KEY)


def nested_convert_to_dict(input: [dict, collections.OrderedDict]):
    if isinstance(input, collections.OrderedDict):
        res = dict(input)
    else:
        res = input
    try:
        for key, value in res.items():
            res[key] = nested_convert_to_dict(value)
            if isinstance(value, list):
                new_value = []
                for item in value:
                    if isinstance(item, collections.OrderedDict):
                        item = nested_convert_to_dict(item)
                    new_value.append(item)
                res[key] = new_value
    except AttributeError:
        pass
    return res


def convert_to_list(obj):
    if type(obj) == type(list()):
        return obj
    else:
        return [obj]
