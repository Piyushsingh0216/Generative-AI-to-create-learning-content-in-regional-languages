class UnsupportedFileTypeError(Exception):
    """Raised when the uploaded file type is not supported."""


class TextExtractionError(Exception):
    """Raised when text extraction fails for a supported file."""


class AIServiceError(Exception):
    """Raised when AI generation fails."""
