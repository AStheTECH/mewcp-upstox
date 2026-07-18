"""Standardized response envelope — every tool returns this shape:

    {"success": bool, "statusCode": int, "error": str | None, "data": ...}
"""


def ok(data, status_code=200):
    return {"success": True, "statusCode": status_code, "error": None, "data": data}


def err(message, status_code=500, data=None):
    return {"success": False, "statusCode": status_code, "error": str(message), "data": data}
