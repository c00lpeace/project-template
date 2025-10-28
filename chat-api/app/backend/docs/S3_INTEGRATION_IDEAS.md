# 🔄 S3 스토리지와 파일 처리 로직 통합 방안

> **작성일:** 2025-10-29  
> **목적:** S3 업로드 후 파일 처리(Excel 파싱 등) 로직 개선 방안  
> **상태:** 아이디어 단계 (구현 전)

---

## 📌 현재 상황

### 완료된 작업
- ✅ S3 클라이언트 구현 (`ai_backend/utils/s3_client.py`)
- ✅ 파일 업로드 S3 연동 완료
- ✅ metadata_json에 S3 정보 저장 (`s3_key`, `s3_url`, `storage_type`)

### 현재 문제
- ❌ **Excel 파싱 시 로컬 파일 경로 필요**
  - `template_service.py`의 `parse_and_save()` 메서드가 `file_path` 파라미터 사용
  - `pd.read_excel(file_path)` 형태로 로컬 파일 기대
  - S3에 업로드된 파일은 로컬 경로가 없어서 처리 불가

### 관련 코드 위치
```
D:\project-template\chat-api\app\backend\
├── ai_backend\api\services\
│   ├── template_service.py     # Excel 파싱 (47번 라인 문제)
│   └── document_service.py     # 업로드 후 parse_and_save() 호출
└── shared_core\
    └── services.py              # S3 업로드 처리
```

### 문제 코드
```python
# template_service.py (47번 라인)
df = pd.read_excel(file_path)  # ← file_path가 S3 URL이면 실패!
```

---

## 💡 해결 방안 (3가지)

### 방안 1: In-Memory 처리 (메모리 기반) ⭐ 추천

#### 개념
```
S3 파일 → bytes 다운로드 → io.BytesIO 버퍼 → pandas 직접 처리
(네트워크)  (메모리)         (메모리)         (디스크 I/O 없음)
```

#### 작동 방식
```python
# StorageHelper 유틸리티 사용
from ai_backend.utils.storage_helper import StorageHelper

# S3에서 메모리 기반으로 가져오기
file_stream = StorageHelper.get_file_stream(document)

# pandas가 메모리에서 직접 읽음
df = pd.read_excel(file_stream)
```

#### 장점
- ✅ **디스크 I/O 없음** - 완전히 메모리에서 처리
- ✅ **빠름** - 네트워크 → 메모리 → 처리
- ✅ **간단함** - 임시 파일 관리 불필요
- ✅ **안정적** - 파일 시스템 의존성 제거
- ✅ **S3 전용 최적화** - 웹앱 환경에 완벽

#### 단점
- ⚠️ **메모리 사용량** - 큰 파일(>100MB)은 메모리 부담
- ⚠️ **네트워크 오버헤드** - S3 다운로드 시간 발생

#### 필요 작업
1. **StorageHelper 유틸리티 생성**
   - 위치: `ai_backend/utils/storage_helper.py`
   - 기능:
     - `get_file_bytes(document)` - bytes 반환
     - `get_file_stream(document)` - BytesIO 반환
     - `get_file_text(document)` - 텍스트 반환
     - S3 클라이언트 싱글톤 관리

2. **template_service.py 수정**
   - `parse_and_save()` 메서드 시그니처 변경:
     ```python
     # Before
     def parse_and_save(self, document_id: str, file_path: str, ...)
     
     # After
     def parse_and_save(self, document_id: str, document: dict, ...)
     ```
   - Excel 읽기 로직 변경:
     ```python
     # Before
     df = pd.read_excel(file_path)
     
     # After
     file_stream = StorageHelper.get_file_stream(document)
     df = pd.read_excel(file_stream)
     ```

3. **document_service.py 수정**
   - `parse_and_save()` 호출 시 document 객체 전달:
     ```python
     # Before
     parse_result = template_service.parse_and_save(
         document_id=result['document_id'],
         file_path=file_path,
         ...
     )
     
     # After
     parse_result = template_service.parse_and_save(
         document_id=result['document_id'],
         document=result,  # metadata_json 포함
         ...
     )
     ```

#### 적용 가능한 다른 파일 타입
```python
# PDF
file_stream = StorageHelper.get_file_stream(document)
pdf = PyPDF2.PdfReader(file_stream)

# Word
file_stream = StorageHelper.get_file_stream(document)
doc = DocxDocument(file_stream)

# 이미지
file_stream = StorageHelper.get_file_stream(document)
img = Image.open(file_stream)

# CSV
file_stream = StorageHelper.get_file_stream(document)
df = pd.read_csv(file_stream)
```

#### 예상 로그
```
✅ S3 클라이언트 초기화 (StorageHelper)
📥 S3에서 파일 다운로드 시작: uploads/user/file.xlsx
✅ S3 다운로드 완료: uploads/user/file.xlsx (52,428 bytes)
✅ BytesIO 스트림 생성 완료
✅ Excel 파일 읽기 완료 (S3 메모리 기반): 150행
```

---

### 방안 2: 임시 다운로드 + 자동 정리

#### 개념
```
S3 파일 → 임시 디렉토리 다운로드 → 처리 → 자동 삭제
```

#### 작동 방식
```python
import tempfile

# 1. 임시 파일 생성
with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=True) as tmp:
    # 2. S3에서 다운로드
    file_bytes = s3_client.download_file(s3_key)
    tmp.write(file_bytes)
    tmp.flush()
    
    # 3. 기존 코드 그대로 사용
    df = pd.read_excel(tmp.name)
    
# 4. with 블록 종료 시 자동 삭제
```

#### 장점
- ✅ **기존 코드 최소 변경** - file_path 방식 유지
- ✅ **안정적** - 큰 파일도 안전하게 처리
- ✅ **자동 정리** - with 블록 사용 시

#### 단점
- ⚠️ **디스크 I/O 발생** - 쓰기/읽기 오버헤드
- ⚠️ **느림** - 네트워크 + 디스크 I/O
- ⚠️ **복잡도** - 임시 파일 관리 필요

#### 필요 작업
1. **StorageManager 헬퍼 클래스 생성**
   - Context manager 지원
   - 자동 정리 기능

2. **template_service.py 수정**
   - with 블록으로 임시 파일 관리:
     ```python
     with StorageManager.get_local_path(document) as local_path:
         df = pd.read_excel(local_path)
     # 자동 삭제됨
     ```

---

### 방안 3: Storage Type 제거 (S3 Only)

#### 개념
- 로컬 스토리지 코드 완전 제거
- S3 전용으로 단순화
- `storage_type` 설정 제거

#### 장점
- ✅ **코드 복잡도 최소화** - 분기 로직 제거
- ✅ **유지보수 쉬움** - 한 가지 방식만 지원
- ✅ **명확함** - 웹앱 = S3만 사용

#### 단점
- ⚠️ **개발 환경** - 로컬 개발 시에도 S3 필요
- ⚠️ **비용** - 개발/테스트도 S3 사용
- ⚠️ **복잡도** - LocalStack 같은 S3 모킹 필요

#### 필요 작업
1. **shared_core/services.py 수정**
   - storage_type 체크 로직 제거
   - 항상 S3만 사용

2. **.env 수정**
   - STORAGE_TYPE 제거
   - S3 설정만 유지

3. **개발 환경 구성**
   - LocalStack 설치 및 설정
   - 또는 개발용 S3 버킷 생성

---

## 📊 방안 비교표

| 항목 | 방안1: In-Memory | 방안2: 임시 다운로드 | 방안3: S3 Only |
|------|-----------------|-------------------|----------------|
| **디스크 I/O** | ❌ 없음 | ⚠️ 있음 | ❌ 없음 |
| **메모리 사용** | ⚠️ 높음 | ✅ 낮음 | ⚠️ 높음 |
| **처리 속도** | ✅ 빠름 | ⚠️ 느림 | ✅ 빠름 |
| **코드 복잡도** | ⚠️ 중간 | ⚠️ 중간 | ✅ 낮음 |
| **기존 코드 변경** | ⚠️ 중간 | ✅ 최소 | ⚠️ 많음 |
| **대용량 파일** | ⚠️ 주의 | ✅ 안정 | ⚠️ 주의 |
| **개발 편의성** | ✅ 좋음 | ✅ 좋음 | ⚠️ S3 필요 |
| **유지보수** | ✅ 쉬움 | ⚠️ 보통 | ✅ 매우 쉬움 |

---

## 🎯 권장 방안

### 단기 (지금 당장): **방안 1 (In-Memory)** ⭐

**이유:**
- 웹앱 환경에 최적화
- 대부분의 파일 크기 적절 (Excel, PDF 등 < 50MB)
- 구현 간단, 유지보수 쉬움
- 다른 파일 타입도 동일하게 적용 가능

**단계:**
1. StorageHelper 유틸리티 생성
2. template_service.py 수정
3. document_service.py 수정
4. 테스트

### 장기 (추후 고려): **방안 1 + 방안 2 하이브리드**

**컨셉:**
```python
# 파일 크기에 따라 자동 선택
if file_size < 50MB:
    # 메모리 기반
    stream = StorageHelper.get_file_stream(document)
    df = pd.read_excel(stream)
else:
    # 임시 다운로드
    with StorageManager.get_local_path(document) as path:
        df = pd.read_excel(path)
```

---

## 🔧 구현 단계 (방안 1 선택 시)

### Phase 1: StorageHelper 생성
```python
# ai_backend/utils/storage_helper.py
class StorageHelper:
    @classmethod
    def get_file_bytes(cls, document: dict) -> bytes:
        """S3에서 bytes로 다운로드"""
        
    @classmethod
    def get_file_stream(cls, document: dict) -> BinaryIO:
        """S3에서 BytesIO 스트림 반환"""
        
    @classmethod
    def get_file_text(cls, document: dict, encoding='utf-8') -> str:
        """S3에서 텍스트 파일 반환"""
```

### Phase 2: template_service.py 수정
```python
def parse_and_save(
    self,
    document_id: str,
    document: dict,  # ← 변경
    pgm_id: str,
    user_id: str
) -> Dict:
    # S3에서 메모리 기반으로 읽기
    file_stream = StorageHelper.get_file_stream(document)
    df = pd.read_excel(file_stream)
```

### Phase 3: document_service.py 수정
```python
parse_result = template_service.parse_and_save(
    document_id=result['document_id'],
    document=result,  # ← 변경
    pgm_id=pgm_id,
    user_id=user_id
)
```

### Phase 4: 테스트
```bash
# 서버 재시작
python -m uvicorn ai_backend.main:app --reload --port 8000

# Excel 업로드 테스트
curl -X POST http://localhost:8000/v1/upload \
  -F "file=@test.xlsx" \
  -F "document_type=pgm_template" \
  -F "metadata={\"pgm_id\": \"PGM001\"}"
```

---

## 📝 체크리스트

### 구현 전 확인사항
- [ ] 현재 Excel 파일 평균 크기 확인 (메모리 적절성)
- [ ] S3 다운로드 속도 테스트 (네트워크 오버헤드)
- [ ] 다른 파일 처리 로직 확인 (PDF, 이미지 등)
- [ ] 방안 선택 및 팀 합의

### 구현 후 확인사항
- [ ] 기능 테스트 (Excel 파싱 성공)
- [ ] 성능 테스트 (처리 속도 확인)
- [ ] 에러 핸들링 (S3 다운로드 실패 시)
- [ ] 로그 확인 (정상 동작 여부)
- [ ] 문서 업데이트

---

## 🚀 다음 단계

1. **방안 선택** - 위 3가지 중 선택
2. **상세 설계** - 선택한 방안의 구현 계획 수립
3. **코드 리뷰** - 변경사항 검토
4. **구현** - 단계별 작업
5. **테스트** - 기능 및 성능 검증
6. **배포** - 프로덕션 적용

---

## 💬 질문 사항

### 기술적 질문
- Excel 파일의 평균/최대 크기는?
- 동시 처리 예상 건수는?
- S3 리전과 서버 리전은 동일한가?

### 비즈니스 질문
- 처리 속도 요구사항은?
- 메모리 제약사항은?
- 개발 환경 구성 방식은?

---

## 📚 참고 자료

### 내부 문서
- `docs/PROJECT_REFERENCE_GUIDE.md` - 프로젝트 구조
- `docs/S3_STORAGE_INTEGRATION.md` - S3 통합 가이드
- `docs/DATABASE_SCHEMA_REFERENCE.md` - DB 스키마

### 관련 코드
- `ai_backend/utils/s3_client.py` - S3 클라이언트
- `ai_backend/api/services/template_service.py` - Excel 파싱
- `shared_core/services.py` - 파일 업로드

### 외부 참고
- [pandas read_excel with BytesIO](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html)
- [boto3 S3 best practices](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3.html)
- [Python tempfile module](https://docs.python.org/3/library/tempfile.html)

---

**이 문서를 새로운 대화에서 참조하여 작업을 이어갈 수 있습니다!** 🚀
