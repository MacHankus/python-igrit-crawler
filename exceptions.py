
class PageChangedException(Exception):
    """Raised when page not match with expectations. Means probably page changed since last script modification."""
    