# 🔧 S3 스토리지 파일 처리 로직 통합 수정 가이드

> **작성일:** 2025-10-29  
> **목적:** S3 업로드 후 파일 처리 로직(Excel 파싱, ZIP 처리 등) 완전 통합  
> **상태:** 수정 방안 확정 → 구현 대기

---

## 📌 현재 문제점 요약

### 전체 플로우 상태
```
✅ 1단계: 파일 업로드 → S3 저장 (완벽 작동)
✅ 2단계: DB 메타데이터 저장 (완벽 작동)
❌ 3단계: 파일 처리 (Excel, ZIP 등) (S3 파일 접근 불가)
```

### 발견된 문제 파일들

| 파일명 | 메서드 | 문제 | 영향도 |
|--------|--------|------|--------|
| **template_service.py** | parse_and_save() | Excel 파싱 시 로컬 경로 필요 | 🔥 높음 |
| **document_service.py** | upload_zip_document() | ZIP 업로드 시 로컬 경로 사용 | 🔥 높음 |
| **document_service.py** | _extract_and_store_zip() | ZIP 압축 해제 시 로컬 경로 필요 | 🔥 높음 |
| **document_service.py** | _analyze_zip_file() | ZIP 분석 시 로컬 경로 필요 | 🔥 높음 |
| **document_service.py** | get_zip_file_content() | ZIP 내부 파일 추출 시 로컬 경로 필요 | 🔥 높음 |

---

## 🎯 채택 방안: 하이브리드 (방안 2 기반)

### 선택 이유
```
✅ 안정성: 대용량 파일도 안전하게 처리
✅ 성능: 작은 파일은 메모리 기반으로 빠르게
✅ 확장성: 다른 파일 타입도 동일 패턴 적용 가능
✅ 기업용: 동시 사용자 많아도 메모리 부족 없음
```

### 하이브리드 전략
```python
if file_size < 10MB:
    # 작은 파일: 메모리 기반 (빠름)
    stream = StorageHelper.get_file_stream(document)
    df = pd.read_excel(stream)
else:
    # 큰 파일: 임시 파일 기반 (안정)
    with StorageHelper.download_to_temp(document) as path:
        df = pd.read_excel(path)
```

---

## 🏗️ 구현 계획

### Phase 1: StorageHelper 유틸리티 생성 ⭐

#### 파일 위치
```
D:\project-template\chat-api\app\backend\ai_backend\utils\storage_helper.py
```

#### 기능 명세
```python
class StorageHelper:
    """S3/로컬 스토리지 통합 헬퍼"""
    
    # 싱글톤 S3 클라이언트
    _s3_client = None
    
    @classmethod
    def _get_s3_client(cls) -> S3Client:
        """S3 클라이언트 싱글톤 인스턴스"""
        if cls._s3_client is None:
            from ai_backend.config.simple_settings import settings
            from ai_backend.utils.s3_client import S3Client
            
            cls._s3_client = S3Client(
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
                bucket_name=settings.s3_bucket_name
            )
        return cls._s3_client
    
    @classmethod
    def get_file_bytes(cls, document: dict) -> bytes:
        """파일을 bytes로 다운로드
        
        Args:
            document: 문서 딕셔너리 (metadata_json 포함)
        
        Returns:
            파일 내용 (bytes)
        """
        storage_type = document.get('metadata_json', {}).get('storage_type', 'local')
        
        if storage_type == 's3':
            # S3에서 다운로드
            s3_key = document['metadata_json']['s3_key']
            s3_client = cls._get_s3_client()
            file_bytes = s3_client.download_file(s3_key)
            logger.info(f"✅ S3 다운로드 완료: {s3_key} ({len(file_bytes)} bytes)")
            return file_bytes
        else:
            # 로컬에서 읽기
            file_path = document.get('upload_path') or document.get('file_path')
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            logger.info(f"✅ 로컬 파일 읽기 완료: {file_path} ({len(file_bytes)} bytes)")
            return file_bytes
    
    @classmethod
    def get_file_stream(cls, document: dict) -> BinaryIO:
        """파일을 BytesIO 스트림으로 반환
        
        Args:
            document: 문서 딕셔너리
        
        Returns:
            BytesIO 스트림
        """
        import io
        file_bytes = cls.get_file_bytes(document)
        stream = io.BytesIO(file_bytes)
        logger.info(f"✅ BytesIO 스트림 생성: {len(file_bytes)} bytes")
        return stream
    
    @classmethod
    @contextmanager
    def download_to_temp(cls, document: dict, suffix: str = None) -> str:
        """파일을 임시 디렉토리에 다운로드 (자동 정리)
        
        Args:
            document: 문서 딕셔너리
            suffix: 파일 확장자 (예: '.xlsx', '.zip')
        
        Yields:
            임시 파일 경로 (str)
        """
        import tempfile
        from pathlib import Path
        
        # 확장자 자동 추출
        if suffix is None:
            filename = document.get('original_filename', '')
            suffix = Path(filename).suffix or '.tmp'
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(
            suffix=suffix,
            delete=False  # with 블록 종료 시 수동 삭제
        ) as tmp:
            # 파일 다운로드
            file_bytes = cls.get_file_bytes(document)
            tmp.write(file_bytes)
            tmp.flush()
            tmp_path = tmp.name
            
            logger.info(f"✅ 임시 파일 생성: {tmp_path} ({len(file_bytes)} bytes)")
            
            try:
                yield tmp_path
            finally:
                # 자동 정리
                try:
                    Path(tmp_path).unlink()
                    logger.info(f"✅ 임시 파일 삭제: {tmp_path}")
                except Exception as e:
                    logger.warning(f"⚠️ 임시 파일 삭제 실패: {tmp_path}, {e}")
    
    @classmethod
    def get_file_text(cls, document: dict, encoding: str = 'utf-8') -> str:
        """텍스트 파일 내용 반환
        
        Args:
            document: 문서 딕셔너리
            encoding: 인코딩 (기본값: utf-8)
        
        Returns:
            텍스트 내용
        """
        file_bytes = cls.get_file_bytes(document)
        text = file_bytes.decode(encoding)
        logger.info(f"✅ 텍스트 파일 읽기 완료: {len(text)} chars")
        return text
```

#### 주요 특징
- ✅ **S3/로컬 자동 판단** - metadata_json.storage_type 확인
- ✅ **싱글톤 패턴** - S3Client 재사용
- ✅ **Context Manager** - 임시 파일 자동 정리
- ✅ **하이브리드 지원** - 메모리/디스크 모두 가능
- ✅ **로깅 완비** - 모든 작업 로깅

---

### Phase 2: template_service.py 수정

#### 2-1. 메서드 시그니처 변경

**Before:**
```python
def parse_and_save(
    self,
    document_id: str,
    file_path: str,  # ❌ 로컬 경로
    pgm_id: str,
    user_id: str
) -> Dict:
```

**After:**
```python
def parse_and_save(
    self,
    document_id: str,
    document: dict,  # ✅ 전체 문서 객체
    pgm_id: str,
    user_id: str
) -> Dict:
```

#### 2-2. Excel 읽기 로직 수정

**Before (47번 라인):**
```python
try:
    df = pd.read_excel(file_path)  # ❌ S3 URL 사용 불가
    logger.info(f"Excel 파일 읽기 완료: {len(df)}행")
except Exception as e:
    logger.error(f"Excel 파일 읽기 실패: {e}")
    raise HandledException(...)
```

**After:**
```python
try:
    from ai_backend.utils.storage_helper import StorageHelper
    
    # 하이브리드 전략
    file_size = document.get('file_size', 0)
    THRESHOLD_SIZE = 10 * 1024 * 1024  # 10MB
    
    if file_size < THRESHOLD_SIZE:
        # 작은 파일: 메모리 기반 (빠름)
        logger.info(f"📥 Excel 파일 메모리 기반 로드 시작: {file_size} bytes")
        file_stream = StorageHelper.get_file_stream(document)
        df = pd.read_excel(file_stream)
        logger.info(f"✅ Excel 파일 읽기 완료 (메모리): {len(df)}행")
    else:
        # 큰 파일: 임시 파일 기반 (안정)
        logger.info(f"📥 Excel 파일 임시 다운로드 시작: {file_size} bytes")
        with StorageHelper.download_to_temp(document, suffix='.xlsx') as tmp_path:
            df = pd.read_excel(tmp_path)
            logger.info(f"✅ Excel 파일 읽기 완료 (임시 파일): {len(df)}행")
    
except Exception as e:
    logger.error(f"❌ Excel 파일 읽기 실패: {e}")
    raise HandledException(
        ResponseCode.INVALID_DATA_FORMAT,
        msg=f"Excel 파일을 읽을 수 없습니다: {str(e)}"
    )
```

#### 2-3. 예상 로그 출력
```
✅ S3 클라이언트 초기화 (StorageHelper)
📥 Excel 파일 메모리 기반 로드 시작: 524288 bytes
✅ S3 다운로드 완료: uploads/user/file.xlsx (524288 bytes)
✅ BytesIO 스트림 생성: 524288 bytes
✅ Excel 파일 읽기 완료 (메모리): 150행
```

---

### Phase 3: document_service.py 수정

#### 3-1. upload_document() 수정

**Before (Line ~95):**
```python
# Excel 파싱 및 PGM_TEMPLATE 테이블 저장
file_path = result.get('upload_path') or result.get('file_path')
if not file_path:
    logger.error(f"file_path를 찾을 수 없음")
    raise ValueError("file_path를 result에서 찾을 수 없습니다")

parse_result = template_service.parse_and_save(
    document_id=result['document_id'],
    file_path=file_path,  # ❌ S3 URL 전달
    pgm_id=pgm_id,
    user_id=user_id
)
```

**After:**
```python
# Excel 파싱 및 PGM_TEMPLATE 테이블 저장
parse_result = template_service.parse_and_save(
    document_id=result['document_id'],
    document=result,  # ✅ 전체 문서 객체 전달
    pgm_id=pgm_id,
    user_id=user_id
)
```

#### 3-2. upload_zip_document() 수정

**Before:**
```python
# 1. 기존 upload_document로 파일 저장
result = self.upload_document(...)

document_id = result['document_id']
upload_path = result['upload_path']  # ❌ S3 URL

# 2. 압축 해제 여부에 따라 분기
if extract_files:
    extraction_result = self._extract_and_store_zip(upload_path, ...)  # ❌
    zip_contents = extraction_result['zip_contents']
else:
    zip_contents = self._analyze_zip_file(upload_path)  # ❌
```

**After:**
```python
# 1. 기존 upload_document로 파일 저장
result = self.upload_document(...)

document_id = result['document_id']

# 2. 압축 해제 여부에 따라 분기
if extract_files:
    extraction_result = self._extract_and_store_zip(result, document_id, user_id)  # ✅
    zip_contents = extraction_result['zip_contents']
else:
    zip_contents = self._analyze_zip_file(result)  # ✅
```

#### 3-3. _extract_and_store_zip() 수정

**Before:**
```python
def _extract_and_store_zip(self, zip_path: str, document_id: str, user_id: str) -> Dict:
    """압축 해제 및 저장
    
    Args:
        zip_path: 원본 ZIP 파일 경로  # ❌ 로컬 경로
    """
    try:
        zip_path_obj = Path(zip_path)
        extracted_base = zip_path_obj.parent / f"{zip_path_obj.stem}_extracted"
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:  # ❌ 로컬 파일
            ...
```

**After:**
```python
def _extract_and_store_zip(self, document: dict, document_id: str, user_id: str) -> Dict:
    """압축 해제 및 저장 (S3/로컬 통합)
    
    Args:
        document: 문서 딕셔너리  # ✅ 전체 객체
    """
    import os
    import zipfile
    from collections import defaultdict
    from datetime import datetime
    from pathlib import Path
    from ai_backend.utils.storage_helper import StorageHelper
    
    try:
        # 하이브리드 전략
        file_size = document.get('file_size', 0)
        THRESHOLD_SIZE = 50 * 1024 * 1024  # 50MB (ZIP은 더 큰 임계값)
        
        if file_size < THRESHOLD_SIZE:
            # 작은 ZIP: 메모리 기반
            logger.info(f"📦 ZIP 파일 메모리 기반 처리 시작: {file_size} bytes")
            zip_bytes = StorageHelper.get_file_bytes(document)
            zip_stream = io.BytesIO(zip_bytes)
            
            # 압축 해제 대상 디렉토리 생성
            from ai_backend.config.simple_settings import settings
            extracted_base = Path(settings.upload_base_path) / document_id / "extracted"
            extracted_base.mkdir(parents=True, exist_ok=True)
            
            files = []
            file_type_stats = defaultdict(int)
            extracted_count = 0
            
            with zipfile.ZipFile(zip_stream, 'r') as zip_ref:
                for info in zip_ref.infolist():
                    try:
                        path_obj = Path(info.filename)
                        extension = path_obj.suffix.lower() if not info.is_dir() else ''
                        
                        extracted_file_path = extracted_base / info.filename
                        
                        file_info = {
                            'path': info.filename,
                            'name': path_obj.name,
                            'extension': extension,
                            'size': info.compress_size,
                            'uncompressed_size': info.file_size,
                            'is_directory': info.is_dir(),
                            'modified_date': datetime(*info.date_time).isoformat() if info.date_time else None,
                            'extracted_path': str(extracted_file_path)
                        }
                        
                        files.append(file_info)
                        
                        if not info.is_dir():
                            if extension:
                                file_type_stats[extension] += 1
                            else:
                                file_type_stats['[no extension]'] += 1
                            
                            # 파일 해제
                            extracted_file_path.parent.mkdir(parents=True, exist_ok=True)
                            with zip_ref.open(info.filename) as source:
                                with open(extracted_file_path, 'wb') as target:
                                    target.write(source.read())
                            extracted_count += 1
                        else:
                            extracted_file_path.mkdir(parents=True, exist_ok=True)
                    
                    except Exception as e:
                        logger.warning(f"⚠️ 파일 해제 실패: {info.filename}, {e}")
                        continue
        else:
            # 큰 ZIP: 임시 파일 기반
            logger.info(f"📦 ZIP 파일 임시 다운로드 시작: {file_size} bytes")
            with StorageHelper.download_to_temp(document, suffix='.zip') as tmp_zip_path:
                zip_path_obj = Path(tmp_zip_path)
                
                # 압축 해제 대상 디렉토리
                from ai_backend.config.simple_settings import settings
                extracted_base = Path(settings.upload_base_path) / document_id / "extracted"
                extracted_base.mkdir(parents=True, exist_ok=True)
                
                files = []
                file_type_stats = defaultdict(int)
                extracted_count = 0
                
                with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
                    for info in zip_ref.infolist():
                        try:
                            path_obj = Path(info.filename)
                            extension = path_obj.suffix.lower() if not info.is_dir() else ''
                            
                            extracted_file_path = extracted_base / info.filename
                            
                            file_info = {
                                'path': info.filename,
                                'name': path_obj.name,
                                'extension': extension,
                                'size': info.compress_size,
                                'uncompressed_size': info.file_size,
                                'is_directory': info.is_dir(),
                                'modified_date': datetime(*info.date_time).isoformat() if info.date_time else None,
                                'extracted_path': str(extracted_file_path)
                            }
                            
                            files.append(file_info)
                            
                            if not info.is_dir():
                                if extension:
                                    file_type_stats[extension] += 1
                                else:
                                    file_type_stats['[no extension]'] += 1
                                
                                extracted_file_path.parent.mkdir(parents=True, exist_ok=True)
                                with zip_ref.open(info.filename) as source:
                                    with open(extracted_file_path, 'wb') as target:
                                        target.write(source.read())
                                extracted_count += 1
                            else:
                                extracted_file_path.mkdir(parents=True, exist_ok=True)
                        
                        except Exception as e:
                            logger.warning(f"⚠️ 파일 해제 실패: {info.filename}, {e}")
                            continue
        
        logger.info(f"✅ ZIP 압축 해제 완료: {extracted_count}개 파일")
        
        return {
            'zip_contents': {
                'files': files,
                'file_type_stats': dict(file_type_stats)
            },
            'extracted_path': str(extracted_base),
            'extracted_count': extracted_count,
            'failed_count': len(files) - extracted_count
        }
        
    except zipfile.BadZipFile:
        raise HandledException(
            ResponseCode.DOCUMENT_INVALID_FILE_TYPE,
            msg="손상된 zip 파일입니다"
        )
    except Exception as e:
        logger.error(f"❌ zip 파일 해제 실패: {e}")
        raise
```

#### 3-4. _analyze_zip_file() 수정

**Before:**
```python
def _analyze_zip_file(self, file_path: str) -> Dict:
    """zip 파일 분석하여 내부 파일 목록 추출"""
    import zipfile
    
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:  # ❌ 로컬 파일
            ...
```

**After:**
```python
def _analyze_zip_file(self, document: dict) -> Dict:
    """zip 파일 분석하여 내부 파일 목록 추출 (S3/로컬 통합)"""
    import zipfile
    import io
    from collections import defaultdict
    from datetime import datetime
    from pathlib import Path
    from ai_backend.utils.storage_helper import StorageHelper
    
    files = []
    file_type_stats = defaultdict(int)
    
    try:
        # 하이브리드 전략
        file_size = document.get('file_size', 0)
        THRESHOLD_SIZE = 50 * 1024 * 1024  # 50MB
        
        if file_size < THRESHOLD_SIZE:
            # 작은 ZIP: 메모리 기반
            logger.info(f"📋 ZIP 분석 메모리 기반 시작: {file_size} bytes")
            zip_bytes = StorageHelper.get_file_bytes(document)
            zip_stream = io.BytesIO(zip_bytes)
            
            with zipfile.ZipFile(zip_stream, 'r') as zip_ref:
                for info in zip_ref.infolist():
                    path_obj = Path(info.filename)
                    extension = path_obj.suffix.lower() if not info.is_dir() else ''
                    
                    file_info = {
                        'path': info.filename,
                        'name': path_obj.name,
                        'extension': extension,
                        'size': info.compress_size,
                        'uncompressed_size': info.file_size,
                        'is_directory': info.is_dir(),
                        'modified_date': datetime(*info.date_time).isoformat() if info.date_time else None
                    }
                    
                    files.append(file_info)
                    
                    if not info.is_dir():
                        if extension:
                            file_type_stats[extension] += 1
                        else:
                            file_type_stats['[no extension]'] += 1
        else:
            # 큰 ZIP: 임시 파일 기반
            logger.info(f"📋 ZIP 분석 임시 다운로드 시작: {file_size} bytes")
            with StorageHelper.download_to_temp(document, suffix='.zip') as tmp_path:
                with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                    for info in zip_ref.infolist():
                        path_obj = Path(info.filename)
                        extension = path_obj.suffix.lower() if not info.is_dir() else ''
                        
                        file_info = {
                            'path': info.filename,
                            'name': path_obj.name,
                            'extension': extension,
                            'size': info.compress_size,
                            'uncompressed_size': info.file_size,
                            'is_directory': info.is_dir(),
                            'modified_date': datetime(*info.date_time).isoformat() if info.date_time else None
                        }
                        
                        files.append(file_info)
                        
                        if not info.is_dir():
                            if extension:
                                file_type_stats[extension] += 1
                            else:
                                file_type_stats['[no extension]'] += 1
        
        logger.info(f"✅ ZIP 분석 완료: {len(files)}개 항목")
        
        return {
            'files': files,
            'file_type_stats': dict(file_type_stats)
        }
        
    except zipfile.BadZipFile:
        raise HandledException(
            ResponseCode.DOCUMENT_INVALID_FILE_TYPE,
            msg="손상된 zip 파일입니다"
        )
    except Exception as e:
        logger.error(f"❌ zip 파일 분석 실패: {e}")
        raise
```

#### 3-5. get_zip_file_content() 수정

**Before:**
```python
def get_zip_file_content(
    self,
    document_id: str,
    user_id: str,
    file_path: str
) -> tuple[bytes, str]:
    """zip 내부 특정 파일 추출"""
    import zipfile
    from pathlib import Path
    
    try:
        doc_info = self.get_document(document_id, user_id)
        
        # ...
        
        # 압축 파일에서 추출 (기존 로직)
        zip_file_path = doc_info['file_path']  # ❌ 로컬 경로
        
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:  # ❌
            ...
```

**After:**
```python
def get_zip_file_content(
    self,
    document_id: str,
    user_id: str,
    file_path: str
) -> tuple[bytes, str]:
    """zip 내부 특정 파일 추출 (S3/로컬 통합)"""
    import zipfile
    import io
    from pathlib import Path
    from ai_backend.utils.storage_helper import StorageHelper
    
    try:
        doc_info = self.get_document(document_id, user_id)
        
        if doc_info.get('document_type') != 'zip':
            raise HandledException(
                ResponseCode.DOCUMENT_INVALID_FILE_TYPE,
                msg="zip 파일이 아닙니다"
            )
        
        from shared_core.crud import DocumentCRUD
        doc_crud = DocumentCRUD(self.db)
        document = doc_crud.get_document(document_id)
        
        storage_type = 'compressed'
        if document.metadata_json:
            storage_type = document.metadata_json.get('storage_type', 'compressed')
        
        if storage_type == 'extracted':
            # 압축 해제된 파일에서 직접 읽기 (기존 로직 유지)
            extracted_path = document.metadata_json.get('extracted_path')
            if not extracted_path:
                raise HandledException(
                    ResponseCode.DOCUMENT_NOT_FOUND,
                    msg="압축 해제 경로를 찾을 수 없습니다"
                )
            
            extracted_file_path = Path(extracted_path) / file_path
            if not extracted_file_path.exists():
                raise HandledException(
                    ResponseCode.DOCUMENT_NOT_FOUND,
                    msg=f"파일이 존재하지 않습니다: {file_path}"
                )
            
            with open(extracted_file_path, 'rb') as f:
                file_content = f.read()
            filename = Path(file_path).name
            return file_content, filename
        else:
            # 압축 파일에서 추출 (S3/로컬 통합)
            document_dict = self._document_to_dict(document)
            
            # 하이브리드 전략
            file_size = document_dict.get('file_size', 0)
            THRESHOLD_SIZE = 50 * 1024 * 1024  # 50MB
            
            if file_size < THRESHOLD_SIZE:
                # 메모리 기반
                logger.info(f"📤 ZIP 내부 파일 추출 (메모리): {file_path}")
                zip_bytes = StorageHelper.get_file_bytes(document_dict)
                zip_stream = io.BytesIO(zip_bytes)
                
                with zipfile.ZipFile(zip_stream, 'r') as zip_ref:
                    try:
                        file_content = zip_ref.read(file_path)
                        filename = Path(file_path).name
                        logger.info(f"✅ ZIP 내부 파일 추출 완료: {len(file_content)} bytes")
                        return file_content, filename
                    except KeyError:
                        raise HandledException(
                            ResponseCode.DOCUMENT_NOT_FOUND,
                            msg=f"zip 내부에 '{file_path}' 파일이 존재하지 않습니다"
                        )
            else:
                # 임시 파일 기반
                logger.info(f"📤 ZIP 내부 파일 추출 (임시 파일): {file_path}")
                with StorageHelper.download_to_temp(document_dict, suffix='.zip') as tmp_path:
                    with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                        try:
                            file_content = zip_ref.read(file_path)
                            filename = Path(file_path).name
                            logger.info(f"✅ ZIP 내부 파일 추출 완료: {len(file_content)} bytes")
                            return file_content, filename
                        except KeyError:
                            raise HandledException(
                                ResponseCode.DOCUMENT_NOT_FOUND,
                                msg=f"zip 내부에 '{file_path}' 파일이 존재하지 않습니다"
                            )
        
    except HandledException:
        raise
    except Exception as e:
        logger.error(f"❌ zip 파일 추출 실패: {e}")
        raise HandledException(ResponseCode.DOCUMENT_DOWNLOAD_ERROR, e=e)
```

---

## 📋 수정 대상 정리표

| 파일 | 메서드 | 변경 유형 | 우선순위 |
|------|--------|----------|----------|
| **storage_helper.py** | 전체 | 🆕 신규 생성 | 1️⃣ 최우선 |
| **template_service.py** | parse_and_save() | 🔧 시그니처 + 로직 변경 | 2️⃣ 높음 |
| **document_service.py** | upload_document() | 🔧 호출 부분 수정 | 2️⃣ 높음 |
| **document_service.py** | upload_zip_document() | 🔧 호출 부분 수정 | 3️⃣ 중간 |
| **document_service.py** | _extract_and_store_zip() | 🔧 시그니처 + 로직 변경 | 3️⃣ 중간 |
| **document_service.py** | _analyze_zip_file() | 🔧 시그니처 + 로직 변경 | 3️⃣ 중간 |
| **document_service.py** | get_zip_file_content() | 🔧 로직 변경 | 3️⃣ 중간 |

---

## 🧪 테스트 계획

### 테스트 케이스

#### 1. Excel 파일 처리
```bash
# 작은 Excel (< 10MB)
curl -X POST http://localhost:8000/v1/upload \
  -F "file=@small_template.xlsx" \
  -F "document_type=pgm_template" \
  -F "metadata={\"pgm_id\": \"PGM001\"}"

# 큰 Excel (> 10MB)
curl -X POST http://localhost:8000/v1/upload \
  -F "file=@large_template.xlsx" \
  -F "document_type=pgm_template" \
  -F "metadata={\"pgm_id\": \"PGM002\"}"
```

#### 2. ZIP 파일 처리
```bash
# ZIP 업로드 (압축 유지)
curl -X POST http://localhost:8000/v1/upload-zip \
  -F "file=@test.zip" \
  -F "extract_files=false"

# ZIP 업로드 (압축 해제)
curl -X POST http://localhost:8000/v1/upload-zip \
  -F "file=@test.zip" \
  -F "extract_files=true"

# ZIP 내부 파일 추출
curl "http://localhost:8000/v1/zip/{document_id}/extract/file.txt"
```

#### 3. S3 스토리지 전환 테스트
```bash
# .env 변경
STORAGE_TYPE=s3

# 서버 재시작 후 동일 테스트 반복
```

### 예상 로그 확인

#### Excel 파싱 (메모리 기반)
```
✅ S3 클라이언트 초기화 (StorageHelper)
📥 Excel 파일 메모리 기반 로드 시작: 524288 bytes
✅ S3 다운로드 완료: uploads/user/file.xlsx (524288 bytes)
✅ BytesIO 스트림 생성: 524288 bytes
✅ Excel 파일 읽기 완료 (메모리): 150행
```

#### Excel 파싱 (임시 파일)
```
✅ S3 클라이언트 초기화 (StorageHelper)
📥 Excel 파일 임시 다운로드 시작: 15728640 bytes
✅ S3 다운로드 완료: uploads/user/large.xlsx (15728640 bytes)
✅ 임시 파일 생성: /tmp/tmpxyz.xlsx (15728640 bytes)
✅ Excel 파일 읽기 완료 (임시 파일): 5000행
✅ 임시 파일 삭제: /tmp/tmpxyz.xlsx
```

#### ZIP 압축 해제
```
📦 ZIP 파일 메모리 기반 처리 시작: 2097152 bytes
✅ S3 다운로드 완료: uploads/user/test.zip (2097152 bytes)
✅ ZIP 압축 해제 완료: 150개 파일
```

---

## ⏱️ 예상 작업 시간

| 단계 | 작업 내용 | 예상 시간 |
|------|----------|-----------|
| 1️⃣ | StorageHelper 생성 | 30분 |
| 2️⃣ | template_service.py 수정 | 20분 |
| 3️⃣ | document_service.py (Excel) 수정 | 10분 |
| 4️⃣ | document_service.py (ZIP) 수정 | 30분 |
| 5️⃣ | 테스트 및 검증 | 30분 |
| 6️⃣ | 문서 업데이트 | 20분 |
| **합계** | | **약 2-3시간** |

---

## ✅ 완료 체크리스트

### 구현 전
- [ ] 이 문서 검토 완료
- [ ] 팀 리뷰 및 승인
- [ ] 백업 계획 수립

### Phase 1
- [ ] storage_helper.py 생성
- [ ] 기본 메서드 구현
  - [ ] get_file_bytes()
  - [ ] get_file_stream()
  - [ ] download_to_temp()
  - [ ] get_file_text()
- [ ] 단위 테스트

### Phase 2
- [ ] template_service.py 수정
  - [ ] 시그니처 변경
  - [ ] 하이브리드 로직 구현
  - [ ] 로깅 추가
- [ ] Excel 파싱 테스트

### Phase 3
- [ ] document_service.py 수정
  - [ ] upload_document() 수정
  - [ ] upload_zip_document() 수정
  - [ ] _extract_and_store_zip() 수정
  - [ ] _analyze_zip_file() 수정
  - [ ] get_zip_file_content() 수정
- [ ] ZIP 처리 테스트

### 통합 테스트
- [ ] 작은 파일 테스트 (메모리 기반)
- [ ] 큰 파일 테스트 (임시 파일)
- [ ] S3 모드 테스트
- [ ] 로컬 모드 테스트
- [ ] 에러 케이스 테스트

### 문서화
- [ ] PROJECT_REFERENCE_GUIDE.md 업데이트
- [ ] 변경 이력 기록
- [ ] API 문서 확인

---

## 🚨 주의사항

### 임계값 설정
```python
# Excel 파일
EXCEL_THRESHOLD = 10 * 1024 * 1024  # 10MB

# ZIP 파일  
ZIP_THRESHOLD = 50 * 1024 * 1024    # 50MB
```
→ 프로젝트 특성에 맞게 조정 필요

### 메모리 사용량 모니터링
- 동시 사용자 수 × 평균 파일 크기 < 서버 메모리
- 예: 20명 × 5MB = 100MB (여유 있음)
- 예: 50명 × 20MB = 1GB (주의 필요)

### S3 다운로드 속도
- 파일 크기가 클수록 다운로드 시간 증가
- 리전 간 거리 고려 (한국 서버 ↔ 한국 S3 = 빠름)

### 임시 파일 정리
- Context Manager 사용으로 자동 정리됨
- 만약 예외 발생 시에도 finally 블록에서 정리

---

## 🔗 관련 문서

- `S3_STORAGE_INTEGRATION.md` - S3 통합 가이드
- `S3_INTEGRATION_IDEAS.md` - 초기 아이디어 문서
- `PROJECT_REFERENCE_GUIDE.md` - 프로젝트 구조
- `DATABASE_SCHEMA_REFERENCE.md` - DB 스키마

---

## 🎯 최종 목표

```
현재:
├─ S3 업로드: ✅ 작동
├─ Excel 파싱: ❌ S3 파일 접근 불가
└─ ZIP 처리: ❌ S3 파일 접근 불가

목표:
├─ S3 업로드: ✅ 작동
├─ Excel 파싱: ✅ S3/로컬 통합
└─ ZIP 처리: ✅ S3/로컬 통합

결과:
✅ 완전한 S3 스토리지 통합
✅ 모든 파일 타입 처리 가능
✅ 하이브리드 전략으로 최적화
```

---

**이 문서를 새로운 대화에서 참조하여 단계별로 구현을 진행할 수 있습니다!** 🚀

**다음 단계:** 구현 시작 (StorageHelper부터)
