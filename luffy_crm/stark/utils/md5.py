import hashlib


def gen_md5(origin):
    ha = hashlib.md5(b'zhfanfagkea')
    ha.update(origin.encode('utf-8'))
    return ha.hexdigest()
