

def response_builder(status_code, response_body, response_header = None):
    if not response_header:
        response_header = {}
        
    response_header["Content-Type"] = "application/json"
    return {
        "statusCode": status_code,
        "headers": response_header,
        "body": response_body,
    }
