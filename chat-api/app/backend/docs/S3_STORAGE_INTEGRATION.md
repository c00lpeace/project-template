# 📦 S3 Storage Integration - 작업 컨텍스트

> **작업 일시:** 2025-10-28 11:00  
> **작업자:** Claude AI Assistant  
> **목적:** 파일 업로드를 로컬 디스크에서 Amazon S3로 전환 가능하도록 구현

---

## 🎯 작업 목표

기존 로컬 디스크 기반 파일 저장 시스템을 Amazon S3와 통합하여:
1. **환경 변수로 저장소 타입 선택 가능** (local ↔ s3)
2. **기존 API 변경 없이 투명하게 통합**
3. **업로드/다운로드/삭제 모두 지원**
4. **메타데이터를 DB에 저장**

---

## ✅ 구현 완료 항목

### 1. **패키지 추가**
- ✅ boto3 (AWS SDK)
- ✅ botocore (boto3 의존성)

### 2. **설정 파일 수정**
- ✅ `.env` - S3 환경 변수 추가
- ✅ `simple_settings.py` - S3 설정 필드 추가

### 3. **신규 파일 생성**
- ✅ `ai_backend/utils/s3_client.py` - S3 클라이언트 래퍼

### 4. **기존 파일 수정**
- ✅ `shared_core/services.py` - DocumentService에 S3 지원 추가

---

## 📂 변경된 파일 상세

### 1. requirements.txt
```diff
+ # AWS SDK for S3 Storage
+ boto3>=1.34.0
+ botocore>=1.34.0
```

### 2. .env
```bash
# Storage Configuration
STORAGE_TYPE=local              # local or s3
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=ap-northeast-2       # 서울 리전
S3_BUCKET_NAME=plc-documents
S3_PREFIX=uploads/
```

### 3. ai_backend/config/simple_settings.py
```python
# Storage Configuration (S3)
storage_type: str = Field(default="local", env="STORAGE_TYPE")
aws_access_key_id: str = Field(default="", env="AWS_ACCESS_KEY_ID")
aws_secret_access_key: str = Field(default="", env="AWS_SECRET_ACCESS_KEY")
aws_region: str = Field(default="ap-northeast-2", env="AWS_REGION")
s3_bucket_name: str = Field(default="", env="S3_BUCKET_NAME")
s3_prefix: str = Field(default="uploads/", env="S3_PREFIX")
```

### 4. ai_backend/utils/s3_client.py (신규)
**주요 메서드:**
- `upload_file(file_content, key, content_type)` → S3 URL
- `download_file(key)` → bytes
- `delete_file(key)` → bool
- `file_exists(key)` → bool
- `get_file_metadata(key)` → dict

**구현 방식:**
- `boto3.client('s3')` 사용
- `put_object()` - 메모리 기반 업로드
- `get_object()` - 다운로드
- `delete_object()` - 삭제
- `head_object()` - 존재 확인

### 5. shared_core/services.py
**DocumentService 수정:**

#### `__init__()` 메서드
```python
# Storage 타입 체크
self.storage_type = settings.storage_type  # 'local' or 's3'

if self.storage_type == "s3":
    self.s3_client = S3Client(...)  # S3 클라이언트 초기화
else:
    self.upload_base_path = Path(...)  # 로컬 경로 설정
```

#### `create_document_from_file()` 메서드
```python
if self.storage_type == "s3":
    # S3 저장
    s3_url = self.s3_client.upload_file(...)
    additional_metadata['s3_key'] = s3_key
    additional_metadata['s3_url'] = s3_url
    additional_metadata['storage_type'] = 's3'
else:
    # 로컬 저장 (기존 로직)
    with open(upload_path, "wb") as f:
        f.write(file_content)
```

#### `download_document()` 메서드
```python
storage_type = metadata.get('storage_type', 'local')

if storage_type == 's3':
    file_content = self.s3_client.download_file(s3_key)
else:
    with open(upload_path, "rb") as f:
        file_content = f.read()
```

#### `delete_document()` 메서드
```python
if storage_type == 's3':
    self.s3_client.delete_file(s3_key)
else:
    upload_path.unlink()
```

---

## 🗄️ 데이터베이스 변경

### DOCUMENTS 테이블의 metadata_json 필드
S3 사용 시 추가되는 메타데이터:
```json
{
  "storage_type": "s3",
  "s3_key": "uploads/user_id/filename.pdf",
  "s3_url": "https://bucket.s3.region.amazonaws.com/uploads/user_id/filename.pdf"
}
```

---

## 🚀 사용 방법

### 로컬 모드 (기본)
```bash
# .env
STORAGE_TYPE=local
UPLOAD_BASE_PATH=./uploads
```

### S3 모드
```bash
# .env
STORAGE_TYPE=s3
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=ap-northeast-2
S3_BUCKET_NAME=plc-documents
S3_PREFIX=uploads/
```

### API 호출 (변경 없음)
```bash
# 파일 업로드 (로컬/S3 자동 선택)
curl -X POST http://localhost:8000/v1/upload \
  -F "file=@document.pdf" \
  -F "user_id=user123"

# 파일 다운로드
curl http://localhost:8000/v1/documents/{document_id}/download

# 파일 삭제
curl -X DELETE http://localhost:8000/v1/documents/{document_id}
```

---

## 🔍 로그 확인

### 서버 시작 시
```
✅ S3 스토리지 모드 활성화
✅ S3 클라이언트 초기화 성공: bucket=plc-documents, region=ap-northeast-2
```
또는
```
✅ 로컬 스토리지 모드 활성화
```

### 파일 업로드 시
```
✅ S3 업로드 성공: https://plc-documents.s3.ap-northeast-2.amazonaws.com/uploads/user/file.pdf
✅ S3 저장 완료: https://...
```

### 에러 발생 시
```
❌ S3 초기화 실패, 로컬 모드로 전환: [error message]
❌ S3 업로드 실패 (ClientError): code=AccessDenied, msg=...
```

---

## 🎯 핵심 설계 원칙

### 1. **전략 패턴 (Strategy Pattern)**
```
DocumentService
    ↓
if storage_type == "s3":
    S3Client (AWS S3)
else:
    Local File System
```

### 2. **투명성 (Transparency)**
- API 엔드포인트 변경 없음
- 클라이언트 코드 수정 불필요
- 환경 변수로만 제어

### 3. **자동 폴백 (Auto Fallback)**
- S3 초기화 실패 → 로컬 모드로 자동 전환
- 에러 로그 남기고 서비스 계속 운영

### 4. **메타데이터 추적**
- storage_type, s3_key, s3_url을 DB에 저장
- 파일 위치 추적 가능

---

## ⚠️ 주의사항

### AWS S3 준비사항
1. **AWS 계정 생성**
2. **S3 버킷 생성**
   - 버킷명: `plc-documents` (또는 원하는 이름)
   - 리전: `ap-northeast-2` (서울)
3. **IAM 사용자 생성 및 권한 부여**
   - `s3:PutObject` (업로드)
   - `s3:GetObject` (다운로드)
   - `s3:DeleteObject` (삭제)
   - `s3:HeadObject` (존재 확인)
4. **Access Key/Secret Key 발급**

### 보안
- ✅ `.env` 파일을 `.gitignore`에 추가
- ✅ AWS 자격증명 노출 주의
- ✅ 프로덕션에서는 IAM Role 사용 권장
- ✅ S3 버킷 정책 설정 (퍼블릭 액세스 차단)

### 비용
- S3 스토리지 비용 발생 (GB당 과금)
- 데이터 전송 비용 발생 (다운로드 시)
- 프리티어: 5GB 저장소, 20,000 GET 요청, 2,000 PUT 요청

---

## 🧪 테스트 체크리스트

### 로컬 모드
- [ ] 파일 업로드 → `./uploads/user_id/filename` 생성 확인
- [ ] 파일 다운로드 → 정상 다운로드 확인
- [ ] 파일 삭제 → 로컬 파일 삭제 확인

### S3 모드
- [ ] 파일 업로드 → S3 버킷에 파일 확인
- [ ] DB에 s3_key, s3_url 저장 확인
- [ ] 파일 다운로드 → S3에서 다운로드 확인
- [ ] 파일 삭제 → S3에서 삭제 확인

### 폴백 테스트
- [ ] 잘못된 AWS 자격증명 → 로컬 모드로 전환 확인
- [ ] S3 버킷 없음 → 에러 로그 확인

---

## 📊 성능 비교

| 항목 | 로컬 스토리지 | S3 스토리지 |
|------|--------------|-------------|
| **업로드 속도** | 빠름 (~10ms) | 중간 (~100ms) |
| **다운로드 속도** | 빠름 | 네트워크 의존 |
| **확장성** | 제한적 (디스크 용량) | 무제한 |
| **고가용성** | 낮음 (단일 서버) | 높음 (99.99%) |
| **백업** | 수동 필요 | 자동 (S3) |
| **비용** | 저렴 (디스크만) | 종량제 과금 |
| **멀티 서버** | 어려움 | 쉬움 |

---

## 🔧 문제 해결 (Troubleshooting)

### 1. "S3 초기화 실패"
```python
❌ S3 초기화 실패, 로컬 모드로 전환: Unable to locate credentials
```
**해결:**
- `.env` 파일에 `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` 확인
- 환경 변수가 제대로 로드되는지 확인

### 2. "Access Denied"
```python
❌ S3 업로드 실패 (ClientError): code=AccessDenied
```
**해결:**
- IAM 사용자에 `s3:PutObject` 권한 추가
- S3 버킷 정책 확인

### 3. "NoSuchBucket"
```python
❌ S3 업로드 실패: The specified bucket does not exist
```
**해결:**
- S3 콘솔에서 버킷 생성
- `.env`의 `S3_BUCKET_NAME` 확인

### 4. "파일을 찾을 수 없습니다"
```python
❌ S3 다운로드 실패: code=NoSuchKey
```
**해결:**
- DB의 `s3_key` 값 확인
- S3 콘솔에서 파일 존재 확인

---

## 🚀 다음 작업 제안

### 우선순위 높음
1. **S3 Presigned URL 생성**
   - 직접 다운로드 링크 생성 (CDN 대체)
   - 만료 시간 설정 (보안 강화)

2. **멀티파트 업로드 지원**
   - 대용량 파일 (>5GB) 업로드
   - 업로드 진행률 표시

3. **S3 수명 주기 정책**
   - 90일 후 Glacier로 이동
   - 비용 최적화

### 우선순위 중간
4. **CloudFront CDN 연동**
   - 다운로드 속도 향상
   - 글로벌 배포

5. **S3 이벤트 알림**
   - 파일 업로드 시 Lambda 트리거
   - 자동 이미지 썸네일 생성

### 우선순위 낮음
6. **하이브리드 모드**
   - 로컬 + S3 동시 저장 (이중화)
   - 캐시 레이어 추가

---

## 📚 참고 문서

### 프로젝트 문서
- `docs/PROJECT_REFERENCE_GUIDE.md` - 프로젝트 전체 구조
- `docs/DATABASE_SCHEMA_REFERENCE.md` - DB 스키마
- `docs/PROJECT_COMPLETION_REPORT.md` - 이전 작업 내역

### AWS 문서
- [boto3 S3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html)
- [S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/best-practices.html)
- [IAM Policies for S3](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-iam-policies.html)

---

## 🎓 새 대화에서 이어서 작업하기

새로운 대화를 시작할 때 이렇게 요청하세요:

```markdown
안녕! PLC-Program Mapping System 프로젝트야.

📂 프로젝트 경로: D:\project-template\chat-api\app\backend\

📚 참조 문서 먼저 읽어줘:
1. docs/PROJECT_REFERENCE_GUIDE.md - 프로젝트 구조
2. docs/S3_STORAGE_INTEGRATION.md - 최근 S3 작업 컨텍스트

🎯 다음 작업:
S3 Presigned URL 생성 기능 추가하고 싶어.
사용자가 직접 S3에서 다운로드할 수 있도록.
```

---

## ✨ 작업 요약

| 항목 | 내용 |
|------|------|
| **작업 일자** | 2025-10-28 |
| **소요 시간** | ~2시간 |
| **생성 파일** | 1개 (s3_client.py) |
| **수정 파일** | 4개 (requirements.txt, .env, settings.py, services.py) |
| **LOC** | ~300줄 |
| **테스트** | 수동 테스트 필요 |
| **배포 상태** | 개발 완료, 프로덕션 대기 |

---

**다음 작업 시 이 문서를 참조하면 빠르게 컨텍스트를 파악할 수 있습니다!** 🚀
