def document_endpoint(*args, **kwargs):
    def decorator(func):
        return func
    return decorator

def document_response(*args, **kwargs):
    return None 