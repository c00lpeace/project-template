# 🗂️ S3 Storage Integration Reference

> **작업일:** 2025-10-28  
> **작업자:** Claude AI Assistant  
> **목적:** Amazon S3 파일 스토리지 연동 구현 내역 및 사용 가이드

---

## 📋 작업 개요

### 목표
로컬 디스크 저장 방식에서 Amazon S3 클라우드 스토리지로 확장하여 확장성과 고가용성 확보

### 구현 방식
- 기존 로컬 저장 방식 유지 (하위 호환성)
- 환경 변수로 저장 방식 선택 (`STORAGE_TYPE=local` or `s3`)
- 투명한 통합 (기존 API 변경 없음)

### 주요 특징
- ✅ 환경 변수 기반 전환
- ✅ 자동 폴백 (S3 실패 시 로컬로 전환)
- ✅ 메타데이터 저장 (s3_key, s3_url)
- ✅ 완전한 CRUD 지원

---

## 📂 변경된 파일 목록

### 1. 신규 생성 파일 (1개)
```
ai_backend/utils/s3_client.py          # S3 클라이언트 (업로드/다운로드/삭제)
```

### 2. 수정된 파일 (4개)
```
requirements.txt                        # boto3, botocore 추가
.env                                   # S3 설정 추가
ai_backend/config/simple_settings.py   # S3 설정 필드 추가
shared_core/services.py                # DocumentService S3 지원
```

---

## 🔧 상세 변경 내역

### 1️⃣ requirements.txt
```diff
+ # AWS SDK for S3 Storage
+ boto3>=1.34.0
+ botocore>=1.34.0
```

### 2️⃣ .env
```bash
# Storage Configuration
STORAGE_TYPE=local                    # local 또는 s3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=ap-northeast-2            # 서울 리전
S3_BUCKET_NAME=plc-documents
S3_PREFIX=uploads/                   # 버킷 내 폴더
```

### 3️⃣ simple_settings.py
```python
# Storage Configuration (S3)
storage_type: str = Field(default="local", env="STORAGE_TYPE")
aws_access_key_id: str = Field(default="", env="AWS_ACCESS_KEY_ID")
aws_secret_access_key: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")
aws_region: str = Field(default="ap-northeast-2", env="AWS_REGION")
s3_bucket_name: str = Field(default="", env="S3_BUCKET_NAME")
s3_prefix: str = Field(default="uploads/", env="S3_PREFIX")
```

### 4️⃣ ai_backend/utils/s3_client.py (신규)
**주요 메서드:**
```python
class S3Client:
    def __init__(aws_access_key_id, aws_secret_access_key, region_name, bucket_name)
    def upload_file(file_content: bytes, key: str, content_type: str) -> str
    def download_file(key: str) -> bytes
    def delete_file(key: str) -> bool
    def file_exists(key: str) -> bool
    def get_file_metadata(key: str) -> dict
```

**사용 예시:**
```python
from ai_backend.utils.s3_client import S3Client

s3 = S3Client(
    aws_access_key_id="AKIAIOSFODNN7EXAMPLE",
    aws_secret_access_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    region_name="ap-northeast-2",
    bucket_name="plc-documents"
)

# 업로드
url = s3.upload_file(
    file_content=b"file data",
    key="uploads/user1/file.pdf",
    content_type="application/pdf"
)

# 다운로드
content = s3.download_file("uploads/user1/file.pdf")

# 삭제
success = s3.delete_file("uploads/user1/file.pdf")
```

### 5️⃣ shared_core/services.py
**수정된 메서드:**

#### `__init__()` - 스토리지 초기화
```python
def __init__(self, db: Session, upload_base_path: str = None):
    # Storage 타입 체크
    from ai_backend.config.simple_settings import settings
    self.storage_type = settings.storage_type
    
    # S3 또는 로컬 저장소 초기화
    if self.storage_type == "s3":
        from ai_backend.utils.s3_client import S3Client
        self.s3_client = S3Client(...)
        self.s3_prefix = settings.s3_prefix
        logger.info("✅ S3 스토리지 모드 활성화")
    else:
        self.upload_base_path = Path(upload_base_path or "uploads")
        logger.info("✅ 로컬 스토리지 모드 활성화")
```

#### `create_document_from_file()` - 파일 저장
```python
# 파일 저장 (S3 또는 로컬)
if self.storage_type == "s3":
    # S3 저장
    s3_key = f"{self.s3_prefix}{file_key}"
    s3_url = self.s3_client.upload_file(
        file_content=file_content,
        key=s3_key,
        content_type=file_type
    )
    upload_path = s3_url
    additional_metadata['s3_key'] = s3_key
    additional_metadata['s3_url'] = s3_url
    additional_metadata['storage_type'] = 's3'
else:
    # 로컬 저장 (기존 로직)
    upload_path = self._get_upload_path(file_key)
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    with open(upload_path, "wb") as f:
        f.write(file_content)
    upload_path = str(upload_path)
    additional_metadata['storage_type'] = 'local'
```

#### `download_document()` - 파일 다운로드
```python
# S3 또는 로컬에서 파일 가져오기
metadata = document.metadata_json or {}
storage_type = metadata.get('storage_type', 'local')

if storage_type == 's3':
    # S3에서 다운로드
    s3_key = metadata.get('s3_key')
    file_content = self.s3_client.download_file(s3_key)
else:
    # 로컬 파일 읽기
    upload_path = Path(document.upload_path)
    with open(upload_path, "rb") as f:
        file_content = f.read()
```

#### `delete_document()` - 파일 삭제
```python
# 실제 파일도 삭제
metadata = document.metadata_json or {}
storage_type = metadata.get('storage_type', 'local')

if storage_type == 's3':
    # S3에서 삭제
    s3_key = metadata.get('s3_key')
    self.s3_client.delete_file(s3_key)
else:
    # 로컬 파일 삭제
    upload_path = Path(document.upload_path)
    upload_path.unlink()
```

---

## 📊 데이터베이스 스키마

### DOCUMENTS 테이블의 metadata_json
S3 사용 시 저장되는 메타데이터:
```json
{
  "storage_type": "s3",
  "s3_key": "uploads/user123/document.pdf",
  "s3_url": "https://plc-documents.s3.ap-northeast-2.amazonaws.com/uploads/user123/document.pdf"
}
```

로컬 사용 시:
```json
{
  "storage_type": "local"
}
```

---

## 🚀 사용 방법

### 1단계: 패키지 설치
```bash
cd D:\project-template\chat-api\app\backend
pip install boto3
```

### 2단계: 환경 설정

**로컬 모드 (기본)**
```bash
# .env
STORAGE_TYPE=local
UPLOAD_BASE_PATH=./uploads
```

**S3 모드**
```bash
# .env
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=your-access-key-here
AWS_SECRET_ACCESS_KEY=your-secret-key-here
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=plc-documents
S3_PREFIX=uploads/
```

### 3단계: 서버 재시작
```bash
python -m uvicorn ai_backend.main:app --reload --port 8000
```

### 4단계: 확인
서버 로그에서 스토리지 모드 확인:
```
✅ S3 스토리지 모드 활성화
```
또는
```
✅ 로컬 스토리지 모드 활성화
```

---

## 🧪 테스트

### 로컬 모드 테스트
```bash
# 1. .env 설정
STORAGE_TYPE=local

# 2. 파일 업로드
curl -X POST http://localhost:8000/v1/upload \
  -F "file=@test.pdf" \
  -F "user_id=test_user"

# 3. 확인
# - ./uploads/test_user/test.pdf 생성됨
# - DB에 storage_type='local' 저장
```

### S3 모드 테스트
```bash
# 1. .env 설정
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=plc-documents

# 2. 파일 업로드
curl -X POST http://localhost:8000/v1/upload \
  -F "file=@test.pdf" \
  -F "user_id=test_user"

# 3. 확인
# - S3 버킷에 uploads/test_user/test.pdf 생성
# - DB에 s3_key, s3_url, storage_type='s3' 저장
```

### API 테스트 (Swagger UI)
```
http://localhost:8000/docs

1. POST /v1/upload - 파일 업로드
2. GET /v1/documents - 문서 목록 조회
3. GET /v1/documents/{document_id}/download - 다운로드
4. DELETE /v1/documents/{document_id} - 삭제
```

---

## 🔍 로그 확인

### 초기화 로그
```
✅ S3 클라이언트 초기화 성공: bucket=plc-documents, region=ap-northeast-2
✅ S3 스토리지 모드 활성화
```

### 업로드 로그
```
✅ S3 업로드 성공: https://plc-documents.s3.ap-northeast-2.amazonaws.com/uploads/user/file.pdf
✅ S3 저장 완료: https://...
```

### 다운로드 로그
```
✅ S3 다운로드 성공: uploads/user/file.pdf (1048576 bytes)
✅ S3에서 다운로드: uploads/user/file.pdf
```

### 삭제 로그
```
✅ S3 삭제 성공: uploads/user/file.pdf
✅ S3 파일 삭제: uploads/user/file.pdf
```

### 에러 로그
```
❌ S3 업로드 실패 (ClientError): code=AccessDenied, msg=Access Denied
❌ S3 파일 없음: uploads/user/notfound.pdf
❌ S3 초기화 실패, 로컬 모드로 전환: Invalid credentials
```

---

## 🛠️ AWS S3 설정 가이드

### 1. S3 버킷 생성
```
1. AWS Console > S3
2. "버킷 만들기" 클릭
3. 버킷 이름: plc-documents
4. 리전: 아시아 태평양(서울) ap-northeast-2
5. 기본 설정으로 생성
```

### 2. IAM 사용자 생성
```
1. AWS Console > IAM > 사용자
2. "사용자 추가" 클릭
3. 사용자 이름: plc-s3-uploader
4. 액세스 유형: 프로그래밍 방식 액세스
5. 권한: 기존 정책 직접 연결
   - AmazonS3FullAccess (또는 커스텀 정책)
6. Access Key / Secret Key 저장
```

### 3. 커스텀 IAM 정책 (최소 권한)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:HeadObject"
      ],
      "Resource": "arn:aws:s3:::plc-documents/*"
    }
  ]
}
```

### 4. CORS 설정 (필요시)
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": []
  }
]
```

---

## ⚠️ 주의사항

### 보안
- ✅ `.env` 파일을 `.gitignore`에 추가
- ✅ AWS 자격증명 절대 코드에 하드코딩 금지
- ✅ 프로덕션에서는 IAM Role 사용 권장
- ✅ S3 버킷 공개 액세스 차단 설정

### 비용
- 📊 S3 스토리지 요금: 월 $0.025/GB (서울 리전)
- 📊 요청 요금: PUT/POST $0.005/1,000건, GET $0.0004/1,000건
- 📊 데이터 전송: 인터넷으로 나가는 데이터 $0.09/GB

### 성능
- ⚡ S3 업로드/다운로드 시 네트워크 지연 발생
- ⚡ 로컬보다 약간 느림 (네트워크 오버헤드)
- ⚡ 대용량 파일 업로드 시 멀티파트 업로드 고려

### 마이그레이션
- 🔄 기존 로컬 파일을 S3로 이전하려면 별도 스크립트 필요
- 🔄 storage_type이 'local'인 문서는 로컬에서 읽음
- 🔄 storage_type이 's3'인 문서는 S3에서 읽음

---

## 🐛 문제 해결

### 문제 1: S3 업로드 실패 (AccessDenied)
**증상:**
```
❌ S3 업로드 실패: Access Denied
```

**해결:**
1. IAM 사용자 권한 확인
2. S3 버킷 정책 확인
3. Access Key/Secret Key 재확인

### 문제 2: 파일이 S3에 없음 (NoSuchKey)
**증상:**
```
❌ S3에 파일이 존재하지 않습니다: uploads/user/file.pdf
```

**해결:**
1. DB의 s3_key 확인
2. S3 Console에서 파일 존재 여부 확인
3. 버킷명/리전 설정 확인

### 문제 3: S3 초기화 실패
**증상:**
```
❌ S3 초기화 실패, 로컬 모드로 전환: Invalid credentials
```

**해결:**
1. .env 파일의 AWS 자격증명 확인
2. simple_settings.py가 .env를 제대로 읽는지 확인
3. boto3 설치 확인: `pip install boto3`

### 문제 4: 로컬 파일이 남아있음
**증상:**
S3 모드로 전환했는데 기존 로컬 파일 그대로

**해결:**
- 정상 동작 (기존 파일은 그대로 유지)
- 새로 업로드하는 파일만 S3에 저장됨
- 필요시 마이그레이션 스크립트 작성

---

## 📈 향후 개선 사항

### 단기 (1-2주)
- [ ] 대용량 파일 멀티파트 업로드 지원
- [ ] S3 Presigned URL을 통한 직접 업로드
- [ ] 파일 업로드 진행률 표시

### 중기 (1-2개월)
- [ ] 로컬→S3 마이그레이션 스크립트
- [ ] S3 CloudFront CDN 연동
- [ ] 파일 버전 관리 (S3 Versioning)

### 장기 (3개월+)
- [ ] 다중 스토리지 지원 (S3 + Azure Blob + GCS)
- [ ] 스토리지 사용량 모니터링
- [ ] 자동 백업 및 복구 시스템

---

## 📚 참고 자료

### 공식 문서
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS S3 API Reference](https://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html)
- [FastAPI File Upload](https://fastapi.tiangolo.com/tutorial/request-files/)

### 관련 프로젝트 문서
- `docs/PROJECT_REFERENCE_GUIDE.md` - 프로젝트 전체 구조
- `docs/DATABASE_SCHEMA_REFERENCE.md` - DB 스키마
- `ai_backend/utils/s3_client.py` - S3 클라이언트 구현
- `shared_core/services.py` - DocumentService 구현

---

## 🎯 체크리스트

### 개발 환경 설정
- [ ] boto3 설치 (`pip install boto3`)
- [ ] .env에 `STORAGE_TYPE=local` 설정
- [ ] 로컬 모드로 테스트

### 프로덕션 배포
- [ ] AWS S3 버킷 생성
- [ ] IAM 사용자 생성 및 권한 부여
- [ ] .env에 AWS 자격증명 설정
- [ ] `STORAGE_TYPE=s3`로 변경
- [ ] S3 모드로 테스트
- [ ] 모니터링 및 로그 확인

---

**작성일:** 2025-10-28  
**최종 수정:** 2025-10-28 11:09

이 문서는 S3 스토리지 연동 작업의 완전한 참조 가이드입니다. 🚀
