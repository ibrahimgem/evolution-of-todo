"""Custom exception classes for the application."""

class BusinessException(Exception):
    """Exception for business logic failures."""

    def __init__(self, message: str, error_code: str = "BUSINESS_ERROR", status_code: int = 400):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)
