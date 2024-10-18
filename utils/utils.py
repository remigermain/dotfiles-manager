import hashlib


def hashs(st) -> str:
    h = hashlib.new("md5")
    h.update(st.encode())
    return h.hexdigest()
