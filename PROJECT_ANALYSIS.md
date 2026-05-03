# Online Menu API - Project Analysis

**Tahlil sanasi:** 2026-05-03  
**Tahlilchi:** Senior Python Developer  
**Umumiy kod hajmi:** ~1773 qator

---

## 📋 PROJECT HAQIDA UMUMIY MA'LUMOT

### Nima qiladi?
Bu **Online Menu API** - restoran va kafeler uchun raqamli menyu tizimi. 

**Asosiy funksiyalar:**
1. **Admin panel** - kompaniyalarni boshqarish (CRUD)
2. **Company panel** - o'z menyusini boshqarish (kategoriya, mahsulotlar)
3. **Public API** - mijozlar uchun menyuni ko'rish (QR kod orqali)
4. **Authentication** - JWT token asosida (access + refresh token)
5. **File upload** - rasm yuklash tizimi
6. **Caching** - Redis orqali tezkor ishlash
7. **Rate limiting** - API cheklovlari (DDoS himoyasi)

### Texnologiyalar:
- **Backend:** FastAPI (Python 3.11)
- **Database:** PostgreSQL 15 (asyncpg)
- **ORM:** SQLAlchemy 2.x (async)
- **Cache:** Redis
- **Auth:** JWT (python-jose)
- **Migration:** Alembic
- **Server:** Uvicorn + Gunicorn

---

## 🏗️ ARXITEKTURA TAHLILI

### Struktura:
```
app/
├── core/          # Asosiy konfiguratsiya
│   ├── config.py      # Settings
│   ├── db.py          # Database connection
│   ├── security.py    # JWT, password hashing
│   ├── cache.py       # Redis cache
│   ├── rate_limit.py  # API limiting
│   └── enums.py       # Role enums
├── models/        # SQLAlchemy models
│   ├── user.py
│   ├── company.py
│   ├── category.py
│   └── products.py
├── schemas/       # Pydantic schemas (validation)
│   ├── auth.py
│   ├── company.py
│   ├── category.py
│   └── product.py
├── routes/        # API endpoints
│   ├── auth.py        # Login/register
│   ├── admin.py       # Admin CRUD
│   ├── company.py     # Company panel
│   ├── menu.py        # Public menu
│   └── upload.py      # File upload
├── services/      # Business logic
│   ├── auth_service.py
│   ├── company_service.py
│   ├── category_service.py
│   └── product_service.py
└── utils/         # Yordamchi funksiyalar
    └── file_upload.py
```

### ✅ Arxitektura afzalliklari:
1. **Layered Architecture** - routes → services → models (to'g'ri separation of concerns)
2. **Dependency Injection** - FastAPI Depends() yaxshi ishlatilgan
3. **Async/await** - to'liq async (database, cache)
4. **Type hints** - Pydantic schemas orqali validation

### ⚠️ Arxitektura kamchiliklari:
1. **Repository pattern yo'q** - service layer to'g'ridan-to'g'ri SQLAlchemy bilan ishlaydi
2. **Unit of Work pattern yo'q** - transaction management tarqoq
3. **Domain layer yo'q** - business logic service layer bilan aralash

---

## 💻 CODE QUALITY TAHLILI

### ✅ Yaxshi tomonlar:

#### 1. **Type Safety**
```python
# Pydantic schemas yaxshi ishlatilgan
class ProductCreate(BaseModel):
    title: str
    category_id: int
    new_price: Decimal = Field(..., decimal_places=2)
```

#### 2. **Async/Await**
```python
# To'liq async implementation
async def get_products(company_id: int, db: AsyncSession) -> List[Product]:
    result = await db.execute(...)
    return result.scalars().all()
```

#### 3. **Security**
- JWT token validation ✅
- Password hashing (bcrypt) ✅
- Token versioning (invalidation) ✅
- Role-based access control ✅
- Rate limiting ✅

#### 4. **Caching Strategy**
```python
# Redis cache yaxshi ishlatilgan
cached = await get_cache(cache_key)
if cached:
    return cached
```

#### 5. **Database Optimization**
```python
# Eager loading (N+1 problem oldini olish)
.options(selectinload(Product.category))

# Composite indexes
Index("idx_products_company_title", "company_id", "title")
```

---

### ❌ KAMCHILIKLAR VA MUAMMOLAR

#### 1. **CRITICAL: Docker konfiguratsiyasi noto'g'ri**

**Dockerfile muammolari:**
```dockerfile
# ❌ NOTO'G'RI: Relative path ishlamaydi
COPY ../../requirements.txt .
COPY ../.. .
COPY ../../entrypoint.sh .
```

**Sabab:** Dockerfile `infra/docker/` ichida, lekin COPY context root dan boshlanadi.

**To'g'ri yechim:**
```dockerfile
FROM python:3.11-slim-bookworm
WORKDIR /app

RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x entrypoint.sh

EXPOSE 8000
CMD ["./entrypoint.sh"]
```

**docker-compose.yml muammolari:**
```yaml
# ❌ NOTO'G'RI: build context
services:
  web:
    build: ../..  # Bu infra/docker dan 2 level yuqoriga ko'taradi
    volumes:
      - .:/app  # Bu infra/docker ni mount qiladi, project root emas!
```

**To'g'ri yechim:**
```yaml
version: '3.8'

services:
  web:
    build:
      context: ../..
      dockerfile: infra/docker/Dockerfile
    container_name: fastapi_app
    ports:
      - "8000:8000"
    env_file:
      - ../../.env
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ../../app:/app/app
      - ../../uploads:/app/uploads
    networks:
      - app-network

  db:
    image: postgres:15
    container_name: postgres_db
    restart: always
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    container_name: redis_cache
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - app-network

volumes:
  postgres_data:
  redis_data:

networks:
  app-network:
    driver: bridge
```

**Environment variables muammosi:**
```bash
# ❌ .env da localhost ishlatilgan (Docker ichida ishlamaydi)
DATABASE_URL=postgresql+asyncpg://postgres:1234@localhost:6432/online_menu
REDIS_URL=redis://localhost:6379/0

# ✅ Docker uchun service name ishlatish kerak
DATABASE_URL=postgresql+asyncpg://postgres:1234@db:5432/online_menu
REDIS_URL=redis://redis:6379/0
```

---

#### 2. **Code Quality Issues**

##### a) **Mutation (immutability buzilgan)**
```python
# ❌ NOTO'G'RI: Object mutation
for key, value in update_data.items():
    setattr(product, key, value)  # Direct mutation

# ✅ TO'G'RI: Immutable approach
updated_product = product.copy(update=update_data)
```

##### b) **Error handling yetarli emas**
```python
# ❌ Generic exception catching
except Exception:
    raise HTTPException(500, "Failed to create company")

# ✅ Specific exceptions
except IntegrityError as e:
    if "unique constraint" in str(e):
        raise HTTPException(409, "Company already exists")
    raise HTTPException(500, f"Database error: {str(e)}")
```

##### c) **Magic numbers**
```python
# ❌ Magic numbers
await set_cache(cache_key, data, 120)  # 120 nima?

# ✅ Named constants
CACHE_TTL_PROFILE = 120  # seconds
await set_cache(cache_key, data, CACHE_TTL_PROFILE)
```

##### d) **Hardcoded values**
```python
# ❌ Hardcoded
MAX_FILE_SIZE_MB = 5
UPLOAD_DIRECTORY = "uploads/images"

# ✅ Config dan olish kerak
class Settings(BaseSettings):
    MAX_FILE_SIZE_MB: int = 5
    UPLOAD_DIRECTORY: str = "uploads/images"
```

##### e) **CORS wildcard (security risk)**
```python
# ❌ XAVFLI: Production da wildcard ishlatilmasligi kerak
allow_origins=["*"]

# ✅ TO'G'RI: Specific domains
allow_origins=[
    "https://yourdomain.com",
    "https://admin.yourdomain.com"
]
```

---

#### 3. **Missing Features**

##### a) **Logging yo'q**
```python
# Hech qayerda logging yo'q!
# ✅ Qo'shish kerak:
import logging

logger = logging.getLogger(__name__)

async def create_product(...):
    logger.info(f"Creating product for company {company_id}")
    try:
        ...
    except Exception as e:
        logger.error(f"Failed to create product: {e}", exc_info=True)
        raise
```

##### b) **Tests yo'q**
```
test/ folder mavjud lekin bo'sh!
- Unit tests yo'q
- Integration tests yo'q
- E2E tests yo'q
```

##### c) **API Documentation yetarli emas**
```python
# ❌ Docstring yo'q
@router.post("/products")
async def create_product(...):
    ...

# ✅ Docstring qo'shish
@router.post("/products", 
    summary="Create new product",
    description="Create a new product for the authenticated company",
    response_description="Created product details"
)
async def create_product(...):
    """
    Create a new product.
    
    - **title**: Product name
    - **category_id**: Category ID (must belong to company)
    - **new_price**: Current price
    """
```

##### d) **Validation yetarli emas**
```python
# ❌ Price validation yo'q
new_price: Decimal = Field(..., decimal_places=2)

# ✅ Validation qo'shish
new_price: Decimal = Field(
    ..., 
    decimal_places=2,
    gt=0,  # Must be positive
    description="Product price in currency units"
)
```

##### e) **Pagination yo'q (performance issue)**
```python
# ❌ Barcha mahsulotlarni qaytaradi (1000+ bo'lsa?)
async def get_products(company_id: int, db: AsyncSession):
    result = await db.execute(
        select(Product).where(Product.company_id == company_id)
    )
    return result.scalars().all()  # Memory issue!

# ✅ Pagination qo'shish
async def get_products(
    company_id: int, 
    db: AsyncSession,
    limit: int = 20,
    offset: int = 0
):
    result = await db.execute(
        select(Product)
        .where(Product.company_id == company_id)
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()
```

---

#### 4. **Security Issues**

##### a) **Secret key hardcoded**
```bash
# ❌ .env da oddiy string
SECRET_KEY="online-menu-secret-key"

# ✅ Strong random key ishlatish kerak
# python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY="xK8vN2pQ9mR5tY7wZ3aB6cD1eF4gH0iJ2kL5mN8oP1qR4sT7uV0wX3yZ6"
```

##### b) **SQL Injection risk yo'q (SQLAlchemy himoya qiladi) ✅**

##### c) **File upload validation yetarli emas**
```python
# ❌ Faqat MIME type tekshiriladi (spoofing mumkin)
def _validate_image_type(self, content_type: str):
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(...)

# ✅ File content ham tekshirish kerak
from PIL import Image

async def upload_image(self, file: UploadFile):
    # Validate MIME type
    self._validate_image_type(file.content_type)
    
    # Validate actual file content
    try:
        image = Image.open(file.file)
        image.verify()  # Verify it's a valid image
    except Exception:
        raise HTTPException(400, "Invalid image file")
```

---

#### 5. **Database Issues**

##### a) **Migration yo'q**
```bash
# alembic/ folder mavjud lekin migration fayllar ko'rinmaydi
# Tekshirish kerak: alembic/versions/
```

##### b) **Connection pool settings**
```python
# ✅ Pool settings yaxshi
pool_size=10,
max_overflow=5,
pool_timeout=10,
pool_recycle=1800,
pool_pre_ping=True,
```

##### c) **Transaction management tarqoq**
```python
# ❌ Har bir service function o'z commit qiladi
try:
    await db.commit()
    await db.refresh(new_product)
except Exception:
    await db.rollback()
    raise

# ✅ Unit of Work pattern ishlatish yaxshiroq
```

---

## 📊 SENIOR LEVEL BAHOLASH

### Code Quality Score: **6.5/10**

| Mezon | Ball | Izoh |
|-------|------|------|
| Architecture | 7/10 | Layered, lekin Repository pattern yo'q |
| Code Style | 7/10 | Type hints yaxshi, lekin mutation bor |
| Security | 6/10 | JWT yaxshi, lekin CORS wildcard, weak secret |
| Performance | 7/10 | Async, caching yaxshi, lekin pagination yo'q |
| Testing | 0/10 | **Tests yo'q!** |
| Documentation | 5/10 | Docstrings yo'q, API docs minimal |
| Error Handling | 5/10 | Generic exceptions |
| Logging | 0/10 | **Logging yo'q!** |
| Docker | 2/10 | **Konfiguratsiya noto'g'ri** |

---

## 🎯 TAVSIYALAR (Priority order)

### 🔴 CRITICAL (Darhol tuzatish kerak):
1. **Docker konfiguratsiyasini tuzatish** (yuqorida ko'rsatilgan)
2. **Environment variables** (localhost → service names)
3. **Tests yozish** (kamida 80% coverage)
4. **Logging qo'shish** (structured logging)

### 🟡 HIGH (Tez orada):
5. **CORS wildcard o'chirish** (production security)
6. **Secret key o'zgartirish** (strong random)
7. **Pagination qo'shish** (performance)
8. **Error handling yaxshilash** (specific exceptions)
9. **File upload validation** (content verification)

### 🟢 MEDIUM (Keyinroq):
10. **Repository pattern** (clean architecture)
11. **Unit of Work pattern** (transaction management)
12. **API documentation** (docstrings, OpenAPI)
13. **Validation yaxshilash** (Pydantic validators)
14. **Constants extraction** (magic numbers)

---

## 🤖 AI INTEGRATION REJASI

### Vazifa:
Admin rasm yuklayotganda AI orqali rasmni yaxshilash:
- Fonni olib tashlash
- Tarelkani chiroyli qilish
- Taomni o'zgartirmaslik

### Texnologiya: Google Gemini API

### Arxitektura:

```
Client → /api/upload/image-with-ai → AI Service → Gemini API
                                    ↓
                                Save original
                                    ↓
                                Process with AI
                                    ↓
                                Save enhanced
                                    ↓
                                Return both paths
```

### Implementation Plan:

#### 1. **Environment Setup**
```bash
# .env ga qo'shish
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-1.5-pro
AI_ENABLED=true
```

#### 2. **Dependencies**
```bash
# Pipfile ga qo'shish
google-generativeai = "*"
pillow = "*"
```

#### 3. **Config Update**
```python
# app/core/config.py
class Settings(BaseSettings):
    # ... existing fields
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    AI_ENABLED: bool = os.getenv("AI_ENABLED", "false").lower() == "true"
```

#### 4. **AI Service yaratish**
```python
# app/services/ai_image_service.py
import google.generativeai as genai
from PIL import Image
import io
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

class AIImageService:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def enhance_food_image(self, image_path: str) -> bytes:
        """
        Enhance food image using Gemini AI.
        - Remove background
        - Enhance plate presentation
        - Keep food unchanged
        """
        # Load image
        image = Image.open(image_path)
        
        # Prepare prompt
        prompt = """
        You are a professional food photographer AI assistant.
        
        Task: Enhance this food image for a restaurant menu:
        1. Remove or blur the background (make it clean/neutral)
        2. Enhance the plate and presentation (lighting, colors)
        3. DO NOT modify the actual food/dish
        4. Keep the composition natural and appetizing
        
        Return the enhanced image maintaining original dimensions.
        """
        
        # Call Gemini API
        response = await self.model.generate_content([prompt, image])
        
        # Extract enhanced image from response
        enhanced_image_data = response.parts[0].inline_data.data
        
        return enhanced_image_data
```

#### 5. **Upload endpoint yangilash**
```python
# app/routes/upload.py
from app.services.ai_image_service import AIImageService

ai_service = AIImageService()

@router.post("/image-with-ai")
async def upload_image_with_ai(
    file: UploadFile = File(...),
    enhance: bool = True  # AI enhancement flag
):
    """
    Upload image with optional AI enhancement.
    
    Returns:
    - original_path: Original uploaded image
    - enhanced_path: AI-enhanced image (if enhance=True)
    """
    # 1. Save original image
    original_path = await upload_service.upload_image(file)
    
    if not enhance or not settings.AI_ENABLED:
        return {
            "success": True,
            "original_path": original_path,
            "enhanced_path": None
        }
    
    # 2. Enhance with AI
    try:
        full_path = f".{original_path}"  # Convert URL path to file path
        enhanced_data = await ai_service.enhance_food_image(full_path)
        
        # 3. Save enhanced image
        enhanced_path = original_path.replace(".jpg", "_enhanced.jpg")
        full_enhanced_path = f".{enhanced_path}"
        
        with open(full_enhanced_path, "wb") as f:
            f.write(enhanced_data)
        
        return {
            "success": True,
            "original_path": original_path,
            "enhanced_path": enhanced_path
        }
    
    except Exception as e:
        # If AI fails, return original
        return {
            "success": True,
            "original_path": original_path,
            "enhanced_path": None,
            "ai_error": str(e)
        }
```

#### 6. **Product schema yangilash**
```python
# app/schemas/product.py
class ProductCreate(BaseModel):
    # ... existing fields
    image: Optional[str] = None
    image_enhanced: Optional[str] = None  # AI enhanced image
```

#### 7. **Database migration**
```bash
# Add new column
alembic revision --autogenerate -m "add_enhanced_image_column"
alembic upgrade head
```

```python
# Migration file
def upgrade():
    op.add_column('products', 
        sa.Column('image_enhanced', sa.String(), nullable=True)
    )

def downgrade():
    op.drop_column('products', 'image_enhanced')
```

### AI Integration Flow:

```
1. Admin uploads image → POST /api/upload/image-with-ai
2. Backend saves original → /uploads/images/2026/05/03/abc123.jpg
3. Backend sends to Gemini → enhance_food_image()
4. Gemini processes → removes background, enhances plate
5. Backend saves enhanced → /uploads/images/2026/05/03/abc123_enhanced.jpg
6. Response returns both paths:
   {
     "original_path": "/uploads/images/2026/05/03/abc123.jpg",
     "enhanced_path": "/uploads/images/2026/05/03/abc123_enhanced.jpg"
   }
7. Frontend shows both → admin chooses which to use
8. Admin creates product → uses chosen image path
```

### Alternative: Real-time processing
```python
# Agar admin faqat enhanced image ni ko'rmoqchi bo'lsa:
@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    auto_enhance: bool = True
):
    path = await upload_service.upload_image(file)
    
    if auto_enhance and settings.AI_ENABLED:
        enhanced_data = await ai_service.enhance_food_image(f".{path}")
        # Overwrite original with enhanced
        with open(f".{path}", "wb") as f:
            f.write(enhanced_data)
    
    return {"success": True, "path": path}
```

---

## 📝 XULOSA

### Umumiy holat:
Project **mid-level** darajada yozilgan. Asosiy funksiyalar ishlaydi, lekin production-ready emas.

### Asosiy muammolar:
1. ❌ **Docker ishlamaydi** (critical)
2. ❌ **Tests yo'q** (critical)
3. ❌ **Logging yo'q** (critical)
4. ⚠️ **Security gaps** (CORS, secrets)
5. ⚠️ **Performance issues** (pagination yo'q)

### Kuchli tomonlar:
1. ✅ Async/await to'liq ishlatilgan
2. ✅ Type hints va Pydantic validation
3. ✅ JWT authentication yaxshi
4. ✅ Redis caching
5. ✅ Rate limiting

### AI integration uchun tayyor:
Project AI integratsiyasiga tayyor. Yuqoridagi plan bo'yicha Gemini API ni osongina qo'shish mumkin.

### Keyingi qadamlar:
1. Docker ni tuzatish
2. AI service qo'shish
3. Tests yozish
4. Production deploy

---

**Savol-javob uchun tayorman!** 🚀
