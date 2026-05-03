# Constants for the application

# Cache TTL (Time To Live) in seconds
CACHE_TTL_PROFILE = 120  # 2 minutes
CACHE_TTL_COMPANY = 300  # 5 minutes
CACHE_TTL_PRODUCTS = 180  # 3 minutes
CACHE_TTL_CATEGORIES = 300  # 5 minutes
CACHE_TTL_MENU = 600  # 10 minutes

# File Upload
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
UPLOAD_DIRECTORY = "uploads/images"
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/gif": "gif",
}

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Rate Limiting
RATE_LIMIT_LOGIN = "5/minute"
RATE_LIMIT_REGISTER = "3/minute"
RATE_LIMIT_READ = "60/minute"
RATE_LIMIT_WRITE = "30/minute"
RATE_LIMIT_DELETE = "10/minute"

# Database
DB_POOL_SIZE = 10
DB_MAX_OVERFLOW = 5
DB_POOL_TIMEOUT = 10
DB_POOL_RECYCLE = 1800

# Chunk size for file reading (1MB)
FILE_CHUNK_SIZE = 1024 * 1024
