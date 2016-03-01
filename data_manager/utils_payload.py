
##
## Request helpers
##
def set_request_payload(request, key, value):
    if not hasattr(request, "collecster_payload"):
        request.collecster_payload = {}
    request.collecster_payload[key] = value; 

def get_request_payload(request, key, default=None):
    if hasattr(request, "collecster_payload") and key in request.collecster_payload:
        return request.collecster_payload[key] 
    return default 
