from rest_framework.response import Response


def api_response(success, message, data=None, status_code=200):
    """Standardized API response format."""
    response_data = {
        "success": success,
        "message": message,
    }
    if data is not None:
        response_data["data"] = data
    return Response(response_data, status=status_code)
