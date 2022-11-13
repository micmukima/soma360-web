import uuid

def generate_code(prefix = None, size = 10):
    code = str(uuid.uuid4()).replace('-', '')
    if prefix:
        code = "%s-%s" %(prefix, code)
    return code.upper()[:size].upper()
