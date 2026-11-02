class ApiError(Exception):
    """Base - mọi lỗi business kế thừa class này."""
    status_code = 500
    code = "internal_error"

    def __init__(self, code=None, message="", status=None):
        super().__init__(message)
        if code: 
            self.code = code
        if status: 
            self.status_code = status
        self.message = message

class NotFound(ApiError):
    status_code = 404
    code = "not_found"

class Conflict(ApiError):
    status_code = 409
    code = "conflict"

class OutOfStock(ApiError):
    status_code = 409
    code = "out_of_stock"