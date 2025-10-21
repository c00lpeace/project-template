# 🔄 shared_core 완전 통합 계획서

> **작성일:** 2025-10-21  
> **목적:** shared_core 패키지를 chat-api 프로젝트에 완전히 통합하여 독립적인 단일 프로젝트로 전환

---

## 📋 목차

1. [현황 분석](#-현황-분석)
2. [통합 전략](#-통합-전략)
3. [작업 체크리스트](#-작업-체크리스트)
4. [통합 후 구조](#-통합-후-구조)
5. [예상 소요 시간](#-예상-소요-시간)
6. [주의사항](#-주의사항)

---

## 📊 현황 분석

### shared_core 패키지 구성

```
D:\project-template\shared_core/
├── models.py         # Document, DocumentChunk, ProcessingJob 모델
├── crud.py          # DocumentCRUD, DocumentChunkCRUD, ProcessingJobCRUD
├── services.py      # DocumentService, DocumentChunkService, ProcessingJobService
├── database.py      # DatabaseManager (PostgreSQL 전용)
├── __init__.py
├── setup.py
└── requirements.txt
```

### chat-api의 shared_core 사용 현황

#### 1. **models.py** 사용
```python
# ai_backend/database/base.py
from shared_core.models import Base as SharedBase
SharedBase.metadata.create_all(bind=self._engine, checkfirst=checkfirst)

# ai_backend/api/services/document_service.py
from shared_core import Document
if document_type not in Document.VALID_DOCUMENT_TYPES:
    raise HandledException(...)
```

#### 2. **crud.py** 사용
```python
# shared_core/services.py에서 간접 사용
from .crud import DocumentCRUD, DocumentChunkCRUD, ProcessingJobCRUD
```

#### 3. **services.py** 사용 (⭐ 중요!)
```python
# ai_backend/api/services/document_service.py
from shared_core import DocumentService as BaseDocumentService

class DocumentService(BaseDocumentService):  # ← 상속받아서 사용 중!
    def __init__(self, db: Session, upload_base_path: str = None):
        super().__init__(db, upload_base_path)  # 부모 클래스 초기화
```

#### 4. **database.py** 사용
```
❌ 사용하지 않음
chat-api는 자체 Database 클래스 사용 (ai_backend/database/base.py)
```

---

## 🎯 통합 전략

### 통합 방침

**완전 통합 (Option 1) 선택 이유:**
1. ✅ doc-processor는 별개 프로젝트로 제거 예정
2. ✅ 단일 프로젝트 관리 용이
3. ✅ 의존성 단순화
4. ✅ 배포 간소화
5. ✅ 디버깅 용이

### 파일별 통합 방법

| shared_core 파일 | 통합 여부 | 통합 방법 | 난이도 |
|-----------------|----------|----------|--------|
| models.py | ✅ 필수 | 3개 파일로 분리 | 중 |
| crud.py | ✅ 필수 | 3개 파일로 분리 | 중 |
| services.py | ✅ 필수 | 1개 병합 + 2개 신규 | 높음 ⭐ |
| database.py | ❌ 불필요 | 통합 안 함 | - |

---

## ✅ 작업 체크리스트

### Phase 1: Models 통합 (30분)

#### 1-1. document_models.py 생성
- [ ] `shared_core/models.py`에서 `Document` 클래스 복사
- [ ] 파일 생성: `ai_backend/database/models/document_models.py`
- [ ] Base import 수정:
```python
# 변경 전
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# 변경 후
from ai_backend.database.base import Base
```

#### 1-2. chunk_models.py 생성
- [ ] `shared_core/models.py`에서 `DocumentChunk` 클래스 복사
- [ ] 파일 생성: `ai_backend/database/models/chunk_models.py`
- [ ] Base import 수정 (위와 동일)

#### 1-3. job_models.py 생성
- [ ] `shared_core/models.py`에서 `ProcessingJob` 클래스 복사
- [ ] 파일 생성: `ai_backend/database/models/job_models.py`
- [ ] Base import 수정 (위와 동일)

---

### Phase 2: CRUD 통합 (30분)

#### 2-1. document_crud.py 생성
- [ ] `shared_core/crud.py`에서 `DocumentCRUD` 클래스 복사
- [ ] 파일 생성: `ai_backend/database/crud/document_crud.py`
- [ ] Import 경로 수정:
```python
# 변경 전
from .models import Document, DocumentChunk, ProcessingJob

# 변경 후
from ai_backend.database.models.document_models import Document
```

#### 2-2. chunk_crud.py 생성
- [ ] `shared_core/crud.py`에서 `DocumentChunkCRUD` 클래스 복사
- [ ] 파일 생성: `ai_backend/database/crud/chunk_crud.py`
- [ ] Import 경로 수정:
```python
from ai_backend.database.models.chunk_models import DocumentChunk
```

#### 2-3. job_crud.py 생성
- [ ] `shared_core/crud.py`에서 `ProcessingJobCRUD` 클래스 복사
- [ ] 파일 생성: `ai_backend/database/crud/job_crud.py`
- [ ] Import 경로 수정:
```python
from ai_backend.database.models.job_models import ProcessingJob
```

---

### Phase 3: Services 통합 (60분) ⭐ 가장 중요

#### 3-1. document_service.py 대폭 수정

**현재 구조 (상속 구조):**
```python
from shared_core import DocumentService as BaseDocumentService

class DocumentService(BaseDocumentService):
    def __init__(self, db: Session, upload_base_path: str = None):
        super().__init__(db, upload_base_path)
    
    def upload_document(...):  # FastAPI 전용 메서드
        ...
```

**변경 후 (평탄화된 단일 클래스):**
```python
class DocumentService:
    """문서 관리 서비스"""
    
    def __init__(self, db: Session, upload_base_path: str = None):
        # ❌ 제거: super().__init__(db, upload_base_path)
        
        # ✅ 추가: BaseDocumentService의 __init__ 내용 복사
        self.db = db
        self.upload_base_path = Path(upload_base_path) if upload_base_path else Path("uploads")
        self.upload_base_path.mkdir(parents=True, exist_ok=True)
        self.document_crud = DocumentCRUD(db)
        self.chunk_crud = DocumentChunkCRUD(db)
        self.job_crud = ProcessingJobCRUD(db)
    
    # ✅ 추가: BaseDocumentService의 모든 메서드 복사
    def _get_file_extension(self, filename: str) -> str:
        """파일 확장자 추출"""
        return Path(filename).suffix.lower().lstrip(".")
    
    def _get_mime_type(self, filename: str) -> str:
        """MIME 타입 추출"""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or "application/octet-stream"
    
    def _calculate_file_hash(self, file_content: bytes) -> str:
        """파일 해시값 계산"""
        hash_md5 = hashlib.md5()
        for i in range(0, len(file_content), 4096):
            chunk = file_content[i : i + 4096]
            hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _generate_file_key(self, user_id: str, filename: str = None) -> str:
        """파일 키 생성"""
        return f"{user_id}/{filename}"
    
    def _get_upload_path(self, file_key: str) -> Path:
        """실제 업로드 경로 생성"""
        return self.upload_base_path / file_key
    
    def create_document_from_file(...):
        """파일 내용으로부터 문서 생성"""
        # shared_core/services.py의 전체 구현 복사
        ...
    
    def create_document_from_path(...):
        """파일 경로로부터 문서 생성"""
        # shared_core/services.py의 전체 구현 복사
        ...
    
    def get_document(...):
        """문서 정보 조회"""
        # shared_core/services.py의 전체 구현 복사
        ...
    
    def get_user_documents(...):
        """사용자의 문서 목록 조회"""
        # shared_core/services.py의 전체 구현 복사
        ...
    
    def search_documents(...):
        """문서 검색"""
        # shared_core/services.py의 전체 구현 복사
        ...
    
    def download_document(...):
        """문서 다운로드"""
        # shared_core/services.py의 전체 구현 복사
        ...
    
    def delete_document(...):
        """문서 삭제"""
        # shared_core/services.py의 전체 구현 복사
        ...
    
    def update_document_processing_status(...):
        """문서 처리 상태 업데이트"""
        # shared_core/services.py의 전체 구현 복사
        ...
    
    def get_document_processing_stats(...):
        """사용자 문서 처리 통계 조회"""
        # shared_core/services.py의 전체 구현 복사
        ...
    
    def _document_to_dict(...):
        """Document 객체를 딕셔너리로 변환"""
        # shared_core/services.py의 전체 구현 복사
        ...
    
    # 기존 메서드 유지
    def upload_document(self, file: UploadFile, ...):
        """FastAPI UploadFile 전용 업로드"""
        # 기존 구현 유지
        ...
```

**작업 체크리스트:**
- [ ] shared_core import 제거
- [ ] 상속 구조 제거 (`(BaseDocumentService)` 삭제)
- [ ] `super().__init__()` 제거
- [ ] BaseDocumentService의 `__init__` 내용 복사
- [ ] BaseDocumentService의 모든 메서드 복사 (12개 메서드)
- [ ] Import 경로 수정:
```python
from ai_backend.database.crud.document_crud import DocumentCRUD
from ai_backend.database.crud.chunk_crud import DocumentChunkCRUD
from ai_backend.database.crud.job_crud import ProcessingJobCRUD
from ai_backend.database.models.document_models import Document
```

#### 3-2. chunk_service.py 생성
- [ ] `shared_core/services.py`에서 `DocumentChunkService` 클래스 복사
- [ ] 파일 생성: `ai_backend/api/services/chunk_service.py`
- [ ] Import 경로 수정

#### 3-3. job_service.py 생성
- [ ] `shared_core/services.py`에서 `ProcessingJobService` 클래스 복사
- [ ] 파일 생성: `ai_backend/api/services/job_service.py`
- [ ] Import 경로 수정

---

### Phase 4: base.py 수정 (10분)

```python
# ai_backend/database/base.py

# ❌ 제거할 코드
from shared_core.models import Base as SharedBase

def create_database(self, checkfirst=True):
    try:
        # Backend 모델들 생성
        Base.metadata.create_all(bind=self._engine, checkfirst=checkfirst)
        
        # shared_core 모델들도 생성  ← 이 부분 제거
        from shared_core.models import Base as SharedBase
        SharedBase.metadata.create_all(bind=self._engine, checkfirst=checkfirst)
        
        logger.info("✅ 모든 테이블 생성 완료 (Backend + shared_core)")
    except Exception as e:
        ...

# ✅ 변경 후
def create_database(self, checkfirst=True):
    try:
        # 모든 모델들을 명시적으로 import (테이블 등록)
        from ai_backend.database.models.plc_models import PLCMaster
        from ai_backend.database.models.program_models import Program
        from ai_backend.database.models.user_models import User
        from ai_backend.database.models.group_models import Group, GroupUser
        from ai_backend.database.models.chat_models import ChatHistory
        from ai_backend.database.models.mapping_models import PgmMappingHistory
        from ai_backend.database.models.document_models import Document
        from ai_backend.database.models.chunk_models import DocumentChunk
        from ai_backend.database.models.job_models import ProcessingJob
        
        # 하나의 Base로 모든 테이블 생성
        Base.metadata.create_all(bind=self._engine, checkfirst=checkfirst)
        
        logger.info("✅ 모든 테이블 생성 완료")
    except Exception as e:
        logger.error("❌ 테이블 생성 실패: " + str(e))
        raise e
```

**작업 체크리스트:**
- [ ] SharedBase import 제거
- [ ] SharedBase.metadata.create_all() 제거
- [ ] Document, DocumentChunk, ProcessingJob 모델 import 추가
- [ ] 로그 메시지 수정

---

### Phase 5: Import 경로 전체 수정 (30분)

프로젝트 전체에서 `shared_core` import 검색 및 제거:

#### 5-1. 검색 대상 파일
```bash
grep -r "from shared_core" ai_backend/
grep -r "import shared_core" ai_backend/
```

#### 5-2. 예상 수정 파일
- [ ] `ai_backend/api/services/document_service.py`
- [ ] `ai_backend/api/routers/document_router.py` (있다면)
- [ ] `ai_backend/database/base.py`
- [ ] 기타 shared_core를 import하는 모든 파일

#### 5-3. Import 변경 패턴
```python
# 변경 전
from shared_core import Document
from shared_core import DocumentService as BaseDocumentService
from shared_core.crud import DocumentCRUD
from shared_core.models import Base as SharedBase

# 변경 후
from ai_backend.database.models.document_models import Document
from ai_backend.database.crud.document_crud import DocumentCRUD
# DocumentService는 더 이상 상속하지 않으므로 import 불필요
# Base는 ai_backend.database.base에서 import
```

---

### Phase 6: 의존성 제거 (10분)

#### 6-1. requirements.txt 수정
```bash
# ai_backend/requirements.txt

# ❌ 제거
shared_core @ file:///D:/project-template/shared_core
# 또는
-e D:/project-template/shared_core
```

#### 6-2. pip uninstall
```bash
cd D:\project-template\chat-api\app\backend
pip uninstall shared_core -y
```

#### 6-3. setup.py 확인 (있다면)
```python
# setup.py에서 shared_core 의존성 제거
install_requires=[
    # 'shared_core',  ← 제거
    ...
]
```

---

### Phase 7: 테스트 (20분)

#### 7-1. 서버 시작 확인
```bash
cd D:\project-template\chat-api\app\backend
python -m uvicorn ai_backend.main:app --reload --port 8000

# ✅ 성공 기준:
# - ImportError 없음
# - shared_core 관련 에러 없음
# - 서버 정상 시작
```

#### 7-2. API 테스트
```bash
# 문서 업로드 테스트
curl -X POST http://localhost:8000/v1/upload \
  -F "file=@test.pdf" \
  -F "user_id=test_user" \
  -F "document_type=common"

# 문서 조회 테스트
curl http://localhost:8000/v1/documents

# ✅ 성공 기준:
# - API 정상 응답
# - Document 테이블 생성 확인
# - 파일 업로드 정상 동작
```

#### 7-3. 데이터베이스 테이블 확인
```sql
-- MySQL 접속 후
SHOW TABLES;

-- 확인 대상 테이블:
-- DOCUMENTS
-- DOCUMENT_CHUNKS
-- PROCESSING_JOBS
```

#### 7-4. 로그 확인
```bash
# logs/app.log 확인
tail -f logs/app.log

# ✅ 체크 포인트:
# - shared_core import 에러 없음
# - 테이블 생성 성공 로그
# - API 호출 정상 로그
```

---

## 🗂️ 통합 후 최종 구조

```
ai_backend/
├── database/
│   ├── models/
│   │   ├── plc_models.py
│   │   ├── program_models.py
│   │   ├── user_models.py
│   │   ├── group_models.py
│   │   ├── chat_models.py
│   │   ├── mapping_models.py
│   │   ├── document_models.py     # ✨ NEW (from shared_core)
│   │   ├── chunk_models.py        # ✨ NEW (from shared_core)
│   │   └── job_models.py          # ✨ NEW (from shared_core)
│   │
│   ├── crud/
│   │   ├── plc_crud.py
│   │   ├── program_crud.py
│   │   ├── user_crud.py
│   │   ├── group_crud.py
│   │   ├── chat_crud.py
│   │   ├── mapping_crud.py
│   │   ├── document_crud.py       # ✨ 수정 (shared_core import 제거)
│   │   ├── chunk_crud.py          # ✨ NEW (from shared_core)
│   │   └── job_crud.py            # ✨ NEW (from shared_core)
│   │
│   └── base.py                    # ✨ 수정 (SharedBase 제거)
│
├── api/
│   ├── services/
│   │   ├── plc_service.py
│   │   ├── program_service.py
│   │   ├── user_service.py
│   │   ├── llm_chat_service.py
│   │   ├── document_service.py    # ✨ 대폭 수정 (상속 → 평탄화)
│   │   ├── chunk_service.py       # ✨ NEW (from shared_core)
│   │   └── job_service.py         # ✨ NEW (from shared_core)
│   │
│   └── routers/
│       ├── plc_router.py
│       ├── program_router.py
│       ├── user_router.py
│       ├── chat_router.py
│       ├── document_router.py     # ✨ 소폭 수정 (import 경로만)
│       └── ...
│
├── types/
│   ├── request/
│   └── response/
│
├── config/
├── core/
├── middleware/
├── utils/
└── main.py
```

---

## ⏱️ 예상 소요 시간

| Phase | 작업 내용 | 예상 시간 | 난이도 |
|-------|----------|----------|--------|
| Phase 1 | Models 통합 | 30분 | 중 |
| Phase 2 | CRUD 통합 | 30분 | 중 |
| Phase 3 | Services 통합 ⭐ | 60분 | 높음 |
| Phase 4 | base.py 수정 | 10분 | 낮음 |
| Phase 5 | Import 경로 수정 | 30분 | 중 |
| Phase 6 | 의존성 제거 | 10분 | 낮음 |
| Phase 7 | 테스트 | 20분 | 중 |
| **총합** | | **약 3시간** | |

---

## ⚠️ 주의사항

### 1. 백업 필수
```bash
# 작업 시작 전 전체 프로젝트 백업
cp -r D:\project-template\chat-api D:\project-template\chat-api_backup_$(date +%Y%m%d)

# Git 커밋 (작업 전)
cd D:\project-template\chat-api
git add .
git commit -m "backup: shared_core 통합 작업 전 백업"
```

### 2. Phase별 커밋 권장
```bash
# Phase 1 완료 후
git add ai_backend/database/models/
git commit -m "feat: shared_core models 통합 (Document, Chunk, Job)"

# Phase 2 완료 후
git add ai_backend/database/crud/
git commit -m "feat: shared_core crud 통합"

# Phase 3 완료 후
git add ai_backend/api/services/
git commit -m "feat: shared_core services 통합 (상속 구조 평탄화)"

# ... 각 Phase마다 커밋
```

### 3. Base 클래스 충돌 주의
```python
# ❌ 잘못된 예
from ai_backend.database.base import Base           # Backend Base
from shared_core.models import Base as SharedBase   # Shared Base (제거 필요)

# ✅ 올바른 예 (통합 후)
from ai_backend.database.base import Base  # 하나의 Base만 사용
```

### 4. CRUD Import 주의
```python
# document_service.py에서 CRUD import

# ✅ 올바른 경로
from ai_backend.database.crud.document_crud import DocumentCRUD
from ai_backend.database.crud.chunk_crud import DocumentChunkCRUD
from ai_backend.database.crud.job_crud import ProcessingJobCRUD

# ❌ 잘못된 경로
from shared_core.crud import DocumentCRUD  # 제거 필요
```

### 5. 순환 Import 방지
```python
# base.py에서 모델 import 시 순환 import 발생 가능
# 해결: create_database() 메서드 내부에서 import
def create_database(self, checkfirst=True):
    # ✅ 메서드 내부에서 import
    from ai_backend.database.models.document_models import Document
    ...
```

### 6. Migration 필요 여부 확인
- 테이블이 이미 생성되어 있다면 괜찮음
- 모델 변경이 있다면 Alembic migration 필요
- 필요 시 별도 migration 파일 작성

### 7. 환경변수 확인
```bash
# settings에서 사용하는 환경변수 확인
# - UPLOAD_BASE_PATH
# - UPLOAD_MAX_SIZE
# - UPLOAD_ALLOWED_TYPES
```

---

## 🎯 핵심 요약

### shared_core 통합이 필요한 이유

1. **doc-processor 제거 예정**
   - shared_core를 사용하는 다른 프로젝트 없음
   - chat-api가 유일한 사용자

2. **의존성 단순화**
   - 외부 패키지 의존성 제거
   - 배포 시 shared_core 함께 배포할 필요 없음

3. **디버깅 편의성**
   - 모든 코드가 한 프로젝트 내부에 있음
   - IDE에서 바로 코드 추적 가능

4. **구조 일관성**
   - 기존 PLC, Program, User 등과 동일한 패턴
   - models → crud → service → router 구조 통일

### 가장 중요한 작업: Phase 3 (Services 통합)

**이유:**
- chat-api의 DocumentService가 shared_core의 DocumentService를 **상속**받고 있음
- 상속 구조를 제거하고 **평탄화(flatten)**해야 함
- BaseDocumentService의 12개 메서드를 모두 복사해야 함
- 가장 시간이 오래 걸림 (60분 예상)

### database.py는 통합 불필요

**이유:**
- chat-api는 MySQL 사용, shared_core는 PostgreSQL 용도
- chat-api는 자체 Database 클래스 있음 (base.py)
- **실제로 사용하지 않음**

---

## 📚 참조 문서

통합 작업 중 참고할 문서:

1. **PROJECT_REFERENCE_GUIDE.md**
   - 프로젝트 전체 구조
   - 기존 파일 위치 확인

2. **DATABASE_SCHEMA_REFERENCE.md**
   - 테이블 구조 확인
   - Document 관련 테이블 스키마

3. **이 문서 (SHARED_CORE_INTEGRATION_PLAN.md)**
   - 작업 순서 및 체크리스트
   - 주의사항

---

## ✅ 완료 체크리스트 요약

- [ ] Phase 1: Models 통합 (3개 파일)
- [ ] Phase 2: CRUD 통합 (3개 파일)
- [ ] Phase 3: Services 통합 (1개 병합 + 2개 신규) ⭐
- [ ] Phase 4: base.py 수정
- [ ] Phase 5: Import 경로 전체 수정
- [ ] Phase 6: 의존성 제거
- [ ] Phase 7: 테스트 및 검증

**총 작업량: 약 3시간**

---

## 🚀 시작하기

```bash
# 1. 백업
cd D:\project-template
cp -r chat-api chat-api_backup_$(date +%Y%m%d)

# 2. 브랜치 생성 (권장)
cd chat-api
git checkout -b feature/integrate-shared-core

# 3. 작업 시작
# Phase 1부터 순서대로 진행

# 4. 각 Phase마다 커밋
git add .
git commit -m "feat: Phase X 완료"

# 5. 최종 테스트 후 머지
git checkout main
git merge feature/integrate-shared-core
```

---

**작성일:** 2025-10-21  
**작성자:** Claude  
**문서 버전:** 1.0

**다음 업데이트 예정:**
- 작업 완료 후 실제 소요 시간 기록
- 발생한 이슈 및 해결 방법 추가
- 성능 변화 측정 결과
