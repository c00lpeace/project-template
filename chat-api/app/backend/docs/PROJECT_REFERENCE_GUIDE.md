# 🏗️ PLC-Program Mapping System - 프로젝트 참조 가이드

> **최종 업데이트:** 2025-10-30 (수요일) 오후 4시 30분  
> **목적:** Claude가 매번 파일을 검색하지 않고 빠르게 프로젝트 구조를 파악하기 위한 참조 문서

---

## 📂 프로젝트 루트 경로
```
D:\project-template\chat-api\app\backend\
```

---

## 🗂️ 디렉토리 구조

```
ai_backend/
├── api/                          # API Layer
│   ├── routers/                  # REST API 엔드포인트
│   │   ├── cache_router.py       # 캐시 관리 API
│   │   ├── chat_router.py        # LLM 채팅 API
│   │   ├── document_router.py    # 문서 관리 API
│   │   ├── group_router.py       # 그룹 관리 API
│   │   ├── pgm_history_router.py # 프로그램 매핑 이력 API
│   │   ├── plc_router.py         # PLC 관리 API
│   │   ├── program_router.py     # 프로그램 관리 API
│   │   ├── template_router.py    # 템플릿 관리 API
│   │   └── user_router.py        # 사용자 관리 API
│   │
│   └── services/                 # Business Logic Layer
│       ├── document_service.py   # 문서 관리 비즈니스 로직
│       ├── group_service.py      # 그룹 관리 비즈니스 로직
│       ├── llm_chat_service.py   # LLM 채팅 비즈니스 로직
│       ├── llm_provider_factory.py # LLM Provider 팩토리
│       ├── pgm_history_service.py # 매핑 이력 비즈니스 로직
│       ├── plc_service.py        # PLC 관리 비즈니스 로직
│       ├── program_service.py    # 프로그램 관리 비즈니스 로직
│       ├── template_service.py   # 템플릿 관리 비즈니스 로직 ✨
│       └── user_service.py       # 사용자 관리 비즈니스 로직
│
├── cache/                        # Cache Layer
│   └── redis_client.py           # Redis 클라이언트
│
├── config/                       # Configuration
│   └── simple_settings.py        # Pydantic Settings
│
├── core/                         # Core Components
│   ├── dependencies.py           # 의존성 주입 (Dependency Injection)
│   └── global_exception_handlers.py # 전역 예외 처리
│
├── database/                     # Database Layer
│   ├── base.py                   # SQLAlchemy Base 설정
│   │
│   ├── crud/                     # CRUD Operations
│   │   ├── chat_crud.py          # 채팅 CRUD
│   │   ├── document_crud.py      # 문서 CRUD
│   │   ├── group_crud.py         # 그룹 CRUD
│   │   ├── pgm_mapping_crud.py   # 매핑 이력 CRUD
│   │   ├── plc_crud.py           # PLC CRUD
│   │   ├── program_crud.py       # 프로그램 CRUD
│   │   ├── template_crud.py      # 템플릿 CRUD
│   │   └── user_crud.py          # 사용자 CRUD
│   │
│   └── models/                   # SQLAlchemy Models
│       ├── chat_models.py        # ChatHistory 모델
│       ├── document_models.py    # Document 모델
│       ├── group_models.py       # Group, GroupUser 모델
│       ├── pgm_mapping_models.py # PgmMappingHistory 모델
│       ├── plc_models.py         # PLCMaster 모델
│       ├── program_models.py     # Program 모델
│       ├── template_models.py    # PgmTemplate 모델
│       └── user_models.py        # User 모델
│
├── middleware/                   # Middleware
│   └── performance_middleware.py # 성능 모니터링
│
├── types/                        # Type Definitions (Pydantic)
│   ├── enums/                    # Enum 정의
│   │   ├── base.py
│   │   └── query.py
│   │
│   ├── request/                  # Request Models
│   │   ├── chat_request.py
│   │   ├── group_request.py
│   │   ├── plc_request.py
│   │   ├── program_request.py
│   │   └── user_request.py
│   │
│   └── response/                 # Response Models
│       ├── base.py               # 기본 응답 구조
│       ├── chat_response.py
│       ├── exceptions.py         # HandledException
│       ├── group_response.py
│       ├── pgm_history_response.py
│       ├── plc_response.py
│       ├── plc_hierarchy_response.py
│       ├── program_response.py
│       ├── response_code.py      # ResponseCode Enum
│       ├── template_response.py
│       └── user_response.py
│
├── utils/                        # Utility Functions
│   ├── logging_utils.py          # 로깅 유틸
│   ├── s3_client.py              # AWS S3 클라이언트
│   ├── storage_helper.py         # S3/로컬 스토리지 통합 헬퍼 ⭐ NEW
│   └── uuid_gen.py               # UUID 생성
│
└── main.py                       # FastAPI Application Entry Point

```

---

## 🗄️ 데이터베이스 테이블

### 1. **PLC_MASTER** (plc_models.py)
```python
class PLCMaster:
    __tablename__ = "PLC_MASTER"
    
    # 기본 정보
    plc_id: str                    # PRIMARY KEY
    plant: str                     # Plant
    process: str                   # 공정
    line: str                      # Line
    equipment_group: str           # 장비그룹
    unit: str                      # 호기
    plc_name: str                  # PLC 명칭
    
    # 프로그램 매핑 (현재 상태)
    pgm_id: str                    # 현재 매핑된 프로그램 ID
    pgm_mapping_dt: datetime       # 마지막 매핑 일시
    pgm_mapping_user: str          # 마지막 매핑 사용자
    
    # 메타데이터
    is_active: bool                # 활성 상태
    create_dt: datetime            # 생성일시
    create_user: str               # 생성자
    update_dt: datetime            # 수정일시
    update_user: str               # 수정자
```

### 2. **PROGRAMS** (program_models.py)
```python
class Program:
    __tablename__ = "PROGRAMS"
    
    pgm_id: str                    # PRIMARY KEY
    pgm_name: str                  # 프로그램 명칭
    document_id: str               # 문서 ID (연결)
    pgm_version: str               # 프로그램 버전
    description: str               # 프로그램 설명
    create_dt: datetime            # 생성일시
    create_user: str               # 생성자
    update_dt: datetime            # 수정일시
    update_user: str               # 수정자
    notes: str                     # 비고
```

### 3. **PGM_MAPPING_HISTORY** (pgm_mapping_models.py)
```python
class PgmMappingHistory:
    __tablename__ = "PGM_MAPPING_HISTORY"
    
    history_id: int                # PRIMARY KEY (AUTO_INCREMENT)
    plc_id: str                    # PLC ID (INDEX)
    pgm_id: str                    # 프로그램 ID
    
    # 이력 메타데이터
    action: str                    # CREATE, UPDATE, DELETE, RESTORE
    action_dt: datetime            # 액션 일시 (INDEX)
    action_user: str               # 액션 사용자
    prev_pgm_id: str               # 이전 프로그램 ID
    notes: str                     # 비고
```

### 4. **DOCUMENTS** (document_models.py)
```python
class Document:
    __tablename__ = "DOCUMENTS"
    
    document_id: str               # PRIMARY KEY
    filename: str                  # 파일명
    file_path: str                 # 파일 경로
    file_size: int                 # 파일 크기
    document_type: str             # 문서 타입
    upload_dt: datetime            # 업로드 일시
    user_id: str                   # 업로드 사용자
    is_public: bool                # 공개 여부
    metadata_json: dict            # 메타데이터 (JSON) - S3 정보 포함
```

### 5. **PGM_TEMPLATE** (template_models.py)
```python
class PgmTemplate:
    __tablename__ = "PGM_TEMPLATE"
    
    template_id: int               # PRIMARY KEY (AUTO_INCREMENT)
    pgm_id: str                    # 프로그램 ID (INDEX)
    document_id: str               # 원본 문서 ID
    folder_id: str                 # Folder ID
    folder_name: str               # Folder 명칭
    sub_folder_id: str             # Sub Folder ID
    sub_folder_name: str           # Sub Folder 명칭
    logic_id: str                  # Logic ID
    logic_name: str                # Logic 명칭
    description: str               # 설명
    create_dt: datetime            # 생성일시
```

### 6. **USERS** (user_models.py)
```python
class User:
    __tablename__ = "USERS"
    
    user_id: str                   # PRIMARY KEY
    username: str                  # 사용자명
    email: str                     # 이메일
    full_name: str                 # 전체 이름
    is_active: bool                # 활성 상태
    create_dt: datetime            # 생성일시
    update_dt: datetime            # 수정일시
```

### 7. **GROUPS** (group_models.py)
```python
class Group:
    __tablename__ = "GROUPS"
    
    group_id: str                  # PRIMARY KEY
    group_name: str                # 그룹명
    description: str               # 설명
    create_dt: datetime            # 생성일시
    create_user: str               # 생성자

class GroupUser:
    __tablename__ = "GROUP_USERS"
    
    group_id: str                  # FOREIGN KEY
    user_id: str                   # FOREIGN KEY
    join_dt: datetime              # 가입일시
```

### 8. **CHAT_HISTORY** (chat_models.py)
```python
class ChatHistory:
    __tablename__ = "CHAT_HISTORY"
    
    chat_id: str                   # PRIMARY KEY
    user_id: str                   # 사용자 ID
    message: str                   # 사용자 메시지
    response: str                  # AI 응답
    model_name: str                # 모델명
    create_dt: datetime            # 생성일시
    tokens_used: int               # 토큰 사용량
```

---

## 🔗 API 엔드포인트 (총 62개)

### Chat API (chat_router.py)
```
POST   /v1/chat/stream              # 스트리밍 채팅
POST   /v1/chat                     # 일반 채팅
GET    /v1/chat/history/{user_id}  # 채팅 이력
```

### Document API (document_router.py)
```
POST   /v1/upload                   # 문서 업로드 (S3/로컬 지원)
GET    /v1/documents                # 문서 목록
GET    /v1/documents/{document_id}  # 문서 조회
DELETE /v1/documents/{document_id}  # 문서 삭제 (S3/로컬)
POST   /v1/upload-zip               # ZIP 파일 업로드
GET    /v1/zip/{document_id}/contents  # ZIP 내부 파일 목록
GET    /v1/zip/{document_id}/extract/{file_path}  # ZIP 파일 추출
GET    /v1/documents/{document_id}/download  # 다운로드 (S3/로컬)
```

### PLC API (plc_router.py) - 16개
```
POST   /v1/plcs                     # PLC 생성
GET    /v1/plc/{plc_id}             # PLC 조회
GET    /v1/plcs                     # PLC 목록 (검색, 페이징)
PUT    /v1/plc/{plc_id}             # PLC 수정
DELETE /v1/plc/{plc_id}             # PLC 삭제 (Soft Delete)
POST   /v1/plc/{plc_id}/mapping     # 프로그램 매핑 (UPSERT)
DELETE /v1/plc/{plc_id}/mapping     # 매핑 해제
GET    /v1/plcs/tree                # 계층 구조 트리 조회
GET    /v1/plcs/unmapped/list       # 미매핑 PLC 목록
GET    /v1/programs/{pgm_id}/plcs   # 프로그램별 매핑된 PLC 목록
```

### Program API (program_router.py) - 5개
```
POST   /v1/programs                 # 프로그램 생성
GET    /v1/programs/{pgm_id}        # 프로그램 조회
GET    /v1/programs                 # 프로그램 목록 (검색, 페이징)
PUT    /v1/programs/{pgm_id}        # 프로그램 수정
DELETE /v1/programs/{pgm_id}        # 프로그램 삭제
```

### PGM History API (pgm_history_router.py) - 6개
```
GET /v1/pgm-history/plc/{plc_id}          # PLC별 매핑 이력
GET /v1/pgm-history/program/{pgm_id}      # 프로그램별 매핑 이력
GET /v1/pgm-history/user/{action_user}    # 사용자별 매핑 이력
GET /v1/pgm-history/recent                # 최근 매핑 이력
GET /v1/pgm-history/plc/{plc_id}/stats    # PLC 이력 통계
GET /v1/pgm-history/{history_id}          # 특정 이력 조회
```

### Template API (template_router.py) - 5개
```
GET    /v1/templates/{pgm_id}        # 프로그램별 템플릿 트리 구조 조회
GET    /v1/templates                 # 템플릿 목록 조회 (검색, 페이징)
DELETE /v1/templates/{pgm_id}        # 프로그램별 템플릿 삭제
GET    /v1/templates-summary         # 모든 프로그램 템플릿 통계
GET    /v1/templates/count/{pgm_id}  # 프로그램별 템플릿 개수 조회
```

### User API (user_router.py)
```
POST   /v1/users                    # 사용자 생성
GET    /v1/users/{user_id}          # 사용자 조회
GET    /v1/users                    # 사용자 목록
PUT    /v1/users/{user_id}          # 사용자 수정
DELETE /v1/users/{user_id}          # 사용자 삭제
```

### Group API (group_router.py)
```
POST   /v1/groups                   # 그룹 생성
GET    /v1/groups/{group_id}        # 그룹 조회
GET    /v1/groups                   # 그룹 목록
PUT    /v1/groups/{group_id}        # 그룹 수정
DELETE /v1/groups/{group_id}        # 그룹 삭제
POST   /v1/groups/{group_id}/users  # 그룹에 사용자 추가
DELETE /v1/groups/{group_id}/users/{user_id}  # 사용자 제거
```

### Cache API (cache_router.py)
```
DELETE /v1/cache/{key}              # 캐시 삭제
DELETE /v1/cache                    # 전체 캐시 삭제
GET    /v1/cache/stats              # 캐시 통계
```

---

## 🏗️ 아키텍처 패턴

### Layered Architecture
```
Client (HTTP)
    ↓
Router (FastAPI)          # API Layer - REST 엔드포인트
    ↓
Service                   # Business Logic Layer
    ↓
CRUD                      # Data Access Layer
    ↓
Model (SQLAlchemy)        # ORM Layer
    ↓
Database (MySQL)          # Database Layer

Storage (로컬/S3)         # File Storage Layer
    ↑
StorageHelper ⭐          # 통합 스토리지 유틸리티
```

### 의존성 주입 (Dependency Injection)
```python
# dependencies.py

def get_db() -> Session:
    """데이터베이스 세션"""
    
def get_plc_service(db: Session) -> PlcService:
    """PLC 서비스"""
    
def get_program_service(db: Session) -> ProgramService:
    """프로그램 서비스"""
    
def get_pgm_history_service(db: Session) -> PgmHistoryService:
    """매핑 이력 서비스"""
    
def get_template_service(db: Session) -> TemplateService:
    """템플릿 서비스"""
```

### 에러 처리
```python
# exceptions.py

class HandledException(Exception):
    """API 예외 처리 기본 클래스"""
    status_code: int
    error_code: str
    message: str

# response_code.py

class ResponseCode(Enum):
    SUCCESS = (200, "SUCCESS", "성공")
    NOT_FOUND = (404, "NOT_FOUND", "찾을 수 없음")
    CONFLICT = (409, "CONFLICT", "중복")
    # ...
```

---

## 🔧 설정 파일

### .env
```bash
# Database
DATABASE_HOST=localhost
DATABASE_PORT=3306
DATABASE_USER=root
DATABASE_PASSWORD=password
DATABASE_NAME=plc_db

# Redis Cache
CACHE_ENABLED=true
REDIS_HOST=localhost
REDIS_PORT=6379

# LLM Provider
LLM_PROVIDER=openai  # openai, anthropic
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Storage Configuration
STORAGE_TYPE=local                    # local 또는 s3
UPLOAD_BASE_PATH=./uploads
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=ap-northeast-2            # 서울 리전
S3_BUCKET_NAME=plc-documents
S3_PREFIX=uploads/                   # 버킷 내 폴더

# Application
APP_DEBUG=true
APP_LOG_LEVEL=INFO
SERVER_LOG_LEVEL=WARNING
```

### simple_settings.py
```python
class Settings(BaseSettings):
    # Database
    database_host: str
    database_port: int
    database_user: str
    database_password: str
    database_name: str
    
    # Cache
    cache_enabled: bool
    redis_host: str
    redis_port: int
    
    # LLM
    llm_provider: str
    openai_api_key: str
    anthropic_api_key: str
    
    # Storage (S3)
    storage_type: str = Field(default="local", env="STORAGE_TYPE")
    upload_base_path: str = Field(default="./uploads", env="UPLOAD_BASE_PATH")
    aws_access_key_id: str = Field(default="", env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="ap-northeast-2", env="AWS_REGION")
    s3_bucket_name: str = Field(default="", env="S3_BUCKET_NAME")
    s3_prefix: str = Field(default="uploads/", env="S3_PREFIX")
    
    # Application
    app_debug: bool
    app_log_level: str
    server_log_level: str
    
    class Config:
        env_file = ".env"
```

---

## 📝 주요 패턴 및 규칙

### 1. **Naming Convention**
- **테이블명**: UPPER_SNAKE_CASE (예: `PLC_MASTER`, `PROGRAMS`)
- **컬럼명**: UPPER_SNAKE_CASE (예: `PLC_ID`, `PGM_NAME`)
- **파일명**: snake_case (예: `plc_router.py`, `program_service.py`)
- **클래스명**: PascalCase (예: `PlcService`, `ProgramCrud`)
- **함수명**: snake_case (예: `get_plc`, `create_program`)

### 2. **Import Convention**
```python
# 절대 경로 사용
from ai_backend.database.models.plc_models import PLCMaster
from ai_backend.api.services.plc_service import PlcService
from ai_backend.types.response.exceptions import HandledException
from ai_backend.utils.s3_client import S3Client
from ai_backend.utils.storage_helper import StorageHelper  # ⭐ NEW
```

### 3. **CRUD 메서드 패턴**
```python
class ExampleCrud:
    @staticmethod
    def create_xxx(db: Session, data: dict) -> Model
    
    @staticmethod
    def get_xxx_by_id(db: Session, id: str) -> Optional[Model]
    
    @staticmethod
    def get_xxx_list(db: Session, skip: int, limit: int) -> List[Model]
    
    @staticmethod
    def update_xxx(db: Session, id: str, data: dict) -> Optional[Model]
    
    @staticmethod
    def delete_xxx(db: Session, id: str) -> bool
```

### 4. **Service 메서드 패턴**
```python
class ExampleService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_xxx(...) -> Model:
        # 1. 입력 검증
        # 2. 비즈니스 로직
        # 3. CRUD 호출
        # 4. 로깅
        # 5. 반환
    
    def get_xxx(...) -> Model:
        # 1. CRUD 호출
        # 2. 존재 여부 확인 (없으면 HandledException)
        # 3. 반환
```

### 5. **Router 패턴**
```python
@router.post("/xxx", response_model=XxxResponse)
def create_xxx(
    request: XxxCreateRequest,
    service: XxxService = Depends(get_xxx_service)
):
    result = service.create_xxx(...)
    return XxxResponse.model_validate(result)
```

---

## 🎯 핵심 기능 Flow

### ⭐ NEW: StorageHelper를 사용한 S3/로컬 파일 처리 (2025-10-30)
```
# 메모리 기반 처리 (작은 파일 < 10MB)
from ai_backend.utils.storage_helper import StorageHelper

stream = StorageHelper.get_file_stream(document)
df = pd.read_excel(stream)

---

# 임시 파일 기반 처리 (큰 파일 >= 10MB)
with StorageHelper.download_to_temp(document, suffix='.xlsx') as tmp_path:
    df = pd.read_excel(tmp_path)
    # 처리...
# with 블록 종료 시 임시 파일 자동 삭제

---

# 하이브리드 전략 (template_service.py)
file_size = document.get('file_size', 0)
THRESHOLD = 10 * 1024 * 1024  # 10MB

if file_size < THRESHOLD:
    # 메모리 기반
    stream = StorageHelper.get_file_stream(document)
    df = pd.read_excel(stream)
else:
    # 임시 파일 기반
    with StorageHelper.download_to_temp(document) as path:
        df = pd.read_excel(path)
```

### 1. **S3 파일 업로드/다운로드 Flow**
```
Client → POST /v1/upload (파일 업로드)
    ↓
document_router.upload_document_request()
    ↓
document_service.upload_document()
    ↓
[Storage Type 체크: S3 or Local]
    ↓
if storage_type == "s3":
    S3Client.upload_file() → S3 버킷에 업로드
    DOCUMENTS.metadata_json에 s3_key, s3_url 저장
else:
    로컬 파일 시스템에 저장
    
---

Client → GET /v1/documents/{document_id}/download
    ↓
document_router.download_document()
    ↓
document_service.download_document()
    ↓
[StorageHelper로 S3/로컬 자동 판단] ⭐ NEW
    ↓
StorageHelper.get_file_bytes(document)
    ↓
Response: StreamingResponse (파일 스트림)
```

### 2. **PLC-프로그램 매핑 Flow**
```
Client → POST /v1/plc/{plc_id}/mapping
    ↓
plc_router.upsert_plc_program_mapping()
    ↓
plc_service.upsert_program_mapping()
    ↓
plc_crud.update_program_mapping()  # PLC_MASTER.pgm_id 업데이트
    ↓
mapping_crud.create_history()      # PGM_MAPPING_HISTORY 기록
```

### 3. **프로그램 생성 Flow**
```
Client → POST /v1/programs
    ↓
program_router.create_program()
    ↓
program_service.create_program()
    ↓
program_crud.create_program()      # PROGRAMS 테이블에 INSERT
```

### 4. **매핑 이력 조회 Flow**
```
Client → GET /v1/pgm-history/plc/{plc_id}
    ↓
pgm_history_router.get_plc_mapping_history()
    ↓
pgm_history_service.get_histories_by_plc()
    ↓
mapping_crud.get_histories_by_plc()  # PGM_MAPPING_HISTORY 조회
```

### 5. **Excel 템플릿 업로드 Flow (하이브리드 전략 적용)** ⭐
```
Client → POST /v1/upload (document_type="pgm_template")
    ↓
document_router.upload_document_request()
    ↓
document_service.upload_document()
    ↓
document_service.create_document_from_file() → DOCUMENTS 저장
    ↓
template_service.parse_and_save() → Excel 파싱
    ↓
[StorageHelper 하이브리드 전략] ⭐
    ↓
if file_size < 10MB:
    # 메모리 기반 (빠름)
    stream = StorageHelper.get_file_stream(document)
    df = pd.read_excel(stream)
else:
    # 임시 파일 기반 (안정)
    with StorageHelper.download_to_temp(document) as path:
        df = pd.read_excel(path)
    ↓
template_crud.bulk_create() → PGM_TEMPLATE Bulk Insert
```

---

## 🚀 개발 가이드

### 새로운 기능 추가 시
1. **Model 생성** (`database/models/`)
2. **CRUD 생성** (`database/crud/`)
3. **Request/Response 타입 생성** (`types/request/`, `types/response/`)
4. **Service 생성** (`api/services/`)
5. **Router 생성** (`api/routers/`)
6. **Dependency 등록** (`core/dependencies.py`)
7. **Router 등록** (`main.py`)

### 파일 수정 시 주의사항
- **Model 변경** → DB 마이그레이션 필요
- **Service 추가** → dependencies.py에 등록 필요
- **Router 추가** → main.py에 등록 필요
- **Response 타입 변경** → API 문서 자동 업데이트됨

---

## 📚 참고 문서

### Swagger UI
```
http://localhost:8000/docs
```

### 서버 실행
```bash
cd D:\project-template\chat-api\app\backend
python -m uvicorn ai_backend.main:app --reload --port 8000
```

### 로그 파일
```
D:\project-template\chat-api\app\backend\logs\app.log
```

---

## ✨ 최근 변경사항

### 2025-10-30 (오후 4:30) - S3 파일 처리 개선 (Phase 1-3 완료) ⭐ NEW

**구현 완료된 컴포넌트:**

#### 1. StorageHelper 유틸리티 생성 (Phase 1)
```
파일: ai_backend/utils/storage_helper.py

주요 기능:
✅ S3/로컬 스토리지 통합 인터페이스
✅ 메모리 기반 처리 (BytesIO)
   - get_file_bytes() - 파일을 bytes로 다운로드
   - get_file_stream() - BytesIO 스트림 반환
   - get_file_text() - 텍스트 파일 읽기
   
✅ 임시 파일 다운로드 (자동 정리)
   - download_to_temp() - Context Manager
   - with 블록 종료 시 자동 삭제
   
✅ 싱글톤 S3 클라이언트
   - _get_s3_client() - 단일 인스턴스 관리

특징:
• metadata_json.storage_type 기반 자동 판단
• S3와 로컬을 동일 인터페이스로 처리
• 에러 핸들링 및 로깅 내장
```

#### 2. template_service.py 하이브리드 전략 적용 (Phase 2)
```
파일: ai_backend/api/services/template_service.py

주요 변경:
✅ StorageHelper 통합
✅ 하이브리드 전략 구현
   - 작은 파일 (< 10MB): 메모리 기반 (빠름)
   - 큰 파일 (>= 10MB): 임시 파일 기반 (안정)

코드:
```python
THRESHOLD_SIZE = 10 * 1024 * 1024  # 10MB

if file_size < THRESHOLD_SIZE:
    # 메모리 기반
    stream = StorageHelper.get_file_stream(document)
    df = pd.read_excel(stream)
else:
    # 임시 파일 기반
    with StorageHelper.download_to_temp(document, '.xlsx') as path:
        df = pd.read_excel(path)
```

장점:
• 작은 파일: 빠른 처리 (메모리)
• 큰 파일: 안정적 처리 (임시 파일)
• 메모리 사용량 최적화
```

#### 3. document_service.py 통합 (Phase 3)
```
파일: ai_backend/api/services/document_service.py

주요 변경:
✅ pgm_template 타입 자동 파싱
✅ template_service.parse_and_save() 호출
✅ StorageHelper를 통한 S3/로컬 통합 처리

플로우:
1. 문서 업로드 → DOCUMENTS 저장
2. document_type == "pgm_template" 체크
3. template_service로 Excel 파싱
4. StorageHelper가 S3/로컬 자동 처리
5. PGM_TEMPLATE 테이블에 저장
```

**주요 개선사항:**
```
✅ 코드 중복 제거
   - S3/로컬 처리 로직을 StorageHelper로 통합
   
✅ 성능 최적화
   - 하이브리드 전략으로 파일 크기별 최적 처리
   
✅ 유지보수성 향상
   - 스토리지 변경 시 StorageHelper만 수정
   
✅ 에러 처리 강화
   - 통합된 에러 핸들링 및 로깅
```

**사용 예시:**
```python
# 서비스 레이어에서 사용
from ai_backend.utils.storage_helper import StorageHelper

# 1. 메모리 스트림
stream = StorageHelper.get_file_stream(document)
df = pd.read_excel(stream)

# 2. 임시 파일 (자동 정리)
with StorageHelper.download_to_temp(document) as path:
    df = pd.read_excel(path)
    # 처리...
# with 종료 시 임시 파일 자동 삭제

# 3. 텍스트 파일
text = StorageHelper.get_file_text(document, encoding='utf-8')
```

---

### 2025-10-28 - S3 스토리지 통합 완료

**구현 완료된 컴포넌트:**
```
1. ✅ utils/s3_client.py - S3 클라이언트 생성
   - upload_file() - S3 업로드
   - download_file() - S3 다운로드
   - delete_file() - S3 삭제
   - file_exists() - 존재 확인
   - get_file_metadata() - 메타데이터 조회

2. ✅ requirements.txt - boto3 패키지 추가
   - boto3>=1.34.0
   - botocore>=1.34.0

3. ✅ simple_settings.py - S3 설정 필드 추가
   - storage_type (local/s3)
   - aws_access_key_id
   - aws_secret_access_key
   - aws_region
   - s3_bucket_name
   - s3_prefix

4. ✅ .env - S3 환경 변수 추가
   - STORAGE_TYPE=local (기본값)
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
   - AWS_REGION=ap-northeast-2
   - S3_BUCKET_NAME=plc-documents

5. ✅ shared_core/services.py - DocumentService S3 지원
   - __init__() - storage_type 체크 및 S3 클라이언트 초기화
   - create_document_from_file() - S3/로컬 선택 저장
   - download_document() - S3/로컬 선택 다운로드
   - delete_document() - S3/로컬 선택 삭제
```

---

### 2025-10-21 13:50 - PLC 트리 API 응답 구조 개선

**변경사항:**
```
1. ✅ plc_service.py - _build_hierarchy() 메서드
   - Unit 내부 PLC 정보를 info 리스트로 감쌈
   - create_dt를 ISO 포맷으로 변환

2. ✅ plc_service.py - _convert_to_response() 메서드
   - 키 이름 축약 (plant→plt, processes→procList 등)
   - JSON 응답 크기 약 20% 감소

3. ✅ plc_router.py - get_plcs_tree() API
   - docstring 업데이트
   - 새 응답 구조 예시 추가
```

---

### 2025-10-20 01:31 - Excel 업로드 및 에러 처리 개선

**수정된 컴포넌트:**
```
1. ✅ document_service.py - metadata 처리 개선
2. ✅ template_service.py - HandledException 사용법 수정
3. ✅ requirements.txt - openpyxl 추가
```

---

### 2025-10-19 15:23 - 템플릿 관리 기능 구현 완료

**구현 완료된 컴포넌트:**
```
1. ✅ template_models.py - PgmTemplate 모델
2. ✅ template_crud.py - CRUD 작업
3. ✅ template_response.py - Response 타입
4. ✅ template_service.py - 비즈니스 로직
5. ✅ document_service.py - 업로드 통합
6. ✅ template_router.py - API 엔드포인트
7. ✅ dependencies.py - 의존성 주입
8. ✅ main.py - Router 등록
```

---

### 2025-10-19 02:19 - PLC 트리 조회 API 구현 완료

**구현 완료된 컴포넌트:**
```
1. ✅ plc_router.py - get_plcs_tree() 엔드포인트
2. ✅ plc_service.py - get_plcs_tree() 메서드
3. ✅ plc_response.py - PlcTreeResponse 타입
4. ✅ plc-tree.html - 트리 시각화 페이지
```

---

### 2025-10-18 - PLC API 엔드포인트 단수/복수 구분

**변경사항:**
```
1. ✅ 단일 PLC: /plcs/{plc_id} → /plc/{plc_id}
2. ✅ 컬렉션: /plcs (유지)
3. ✅ HTML 테스트 페이지 추가 (plc-tree.html)
4. ✅ PostgreSQL 대소문자 구분 이슈 해결
```

---

### 2025-10-17 - 프로그램 관리 기능 구현 완료

**구현 완료된 컴포넌트:**
```
1. ✅ Program 모델 생성
2. ✅ PgmMappingHistory 모델 생성
3. ✅ program_crud.py, mapping_crud.py 생성
4. ✅ program_service.py, pgm_history_service.py 생성
5. ✅ program_router.py, pgm_history_router.py 생성
6. ✅ Program API 5개 엔드포인트 추가
7. ✅ PGM History API 6개 엔드포인트 추가
```

---

## 🔍 빠른 검색 키워드

- **PLC 관련**: plc_models.py, plc_crud.py, plc_service.py, plc_router.py
- **프로그램 관련**: program_models.py, program_crud.py, program_service.py, program_router.py
- **매핑 이력**: pgm_mapping_models.py, pgm_mapping_crud.py, pgm_history_service.py, pgm_history_router.py
- **템플릿 관련**: template_models.py, template_crud.py, template_service.py, template_router.py
- **문서 관리**: document_models.py, document_service.py, document_router.py
- **스토리지 통합**: storage_helper.py, s3_client.py ⭐ NEW
- **채팅**: chat_models.py, llm_chat_service.py, chat_router.py
- **설정**: simple_settings.py, dependencies.py, .env
- **에러 처리**: exceptions.py, response_code.py, global_exception_handlers.py

---

**이 문서를 활용하면 Claude가 매번 파일을 검색하지 않고도 프로젝트 구조를 빠르게 파악할 수 있습니다!** 🚀
