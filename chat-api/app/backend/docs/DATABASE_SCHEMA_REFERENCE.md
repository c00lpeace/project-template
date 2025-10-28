# 🗄️ Database Schema Reference

> **최종 업데이트:** 2025-10-28  
> **목적:** 모든 테이블 구조와 관계를 한눈에 파악

---

## 📊 테이블 목록

| 테이블명 | 설명 | 모델 파일 | 주요 용도 |
|---------|------|-----------|-----------|
| PLC_MASTER | PLC 마스터 정보 | plc_models.py | PLC 기본 정보 + 현재 매핑 상태 |
| PROGRAMS | 프로그램 마스터 | program_models.py | 프로그램 기본 정보 |
| PGM_MAPPING_HISTORY | 매핑 변경 이력 | pgm_mapping_models.py | 모든 매핑 변경 감사 추적 |
| PGM_TEMPLATE | 프로그램 템플릿 | template_models.py | 프로그램 구조 템플릿 (Excel 파싱) |
| DOCUMENTS | 문서 정보 | document_models.py | 업로드된 파일 메타데이터 (S3/로컬) ⭐ |
| USERS | 사용자 정보 | user_models.py | 사용자 계정 |
| GROUPS | 그룹 정보 | group_models.py | 사용자 그룹 |
| GROUP_USERS | 그룹-사용자 매핑 | group_models.py | N:M 관계 |
| CHAT_HISTORY | 채팅 이력 | chat_models.py | LLM 대화 기록 |

---

## 1️⃣ PLC_MASTER

### 테이블 정의
```sql
CREATE TABLE PLC_MASTER (
    PLC_ID VARCHAR(50) PRIMARY KEY,
    PLANT VARCHAR(100) NOT NULL,
    PROCESS VARCHAR(100) NOT NULL,
    LINE VARCHAR(100) NOT NULL,
    EQUIPMENT_GROUP VARCHAR(100) NOT NULL,
    UNIT VARCHAR(100) NOT NULL,
    PLC_NAME VARCHAR(200) NOT NULL,
    
    -- 프로그램 매핑 (현재 상태)
    PGM_ID VARCHAR(50),
    PGM_MAPPING_DT DATETIME,
    PGM_MAPPING_USER VARCHAR(50),
    
    -- 메타데이터
    IS_ACTIVE BOOLEAN NOT NULL DEFAULT TRUE,
    CREATE_DT DATETIME NOT NULL DEFAULT NOW(),
    CREATE_USER VARCHAR(50),
    UPDATE_DT DATETIME,
    UPDATE_USER VARCHAR(50)
);
```

### SQLAlchemy 모델
```python
class PLCMaster(Base):
    __tablename__ = "PLC_MASTER"
    
    plc_id = Column('PLC_ID', String(50), primary_key=True)
    plant = Column('PLANT', String(100), nullable=False)
    process = Column('PROCESS', String(100), nullable=False)
    line = Column('LINE', String(100), nullable=False)
    equipment_group = Column('EQUIPMENT_GROUP', String(100), nullable=False)
    unit = Column('UNIT', String(100), nullable=False)
    plc_name = Column('PLC_NAME', String(200), nullable=False)
    
    # 프로그램 매핑
    pgm_id = Column('PGM_ID', String(50), nullable=True)
    pgm_mapping_dt = Column('PGM_MAPPING_DT', DateTime, nullable=True)
    pgm_mapping_user = Column('PGM_MAPPING_USER', String(50), nullable=True)
    
    # 메타데이터
    is_active = Column('IS_ACTIVE', Boolean, nullable=False, server_default=true())
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())
    create_user = Column('CREATE_USER', String(50), nullable=True)
    update_dt = Column('UPDATE_DT', DateTime, nullable=True)
    update_user = Column('UPDATE_USER', String(50), nullable=True)
```

### 컬럼 설명
| 컬럼명 | 타입 | NULL | 설명 | 예시 |
|--------|------|------|------|------|
| PLC_ID | VARCHAR(50) | NOT NULL | PLC 고유 ID (PK) | "M1CFB01000" |
| PLANT | VARCHAR(100) | NOT NULL | Plant | "P1" |
| PROCESS | VARCHAR(100) | NOT NULL | 공정 | "조립" |
| LINE | VARCHAR(100) | NOT NULL | Line | "L1" |
| EQUIPMENT_GROUP | VARCHAR(100) | NOT NULL | 장비그룹 | "로봇" |
| UNIT | VARCHAR(100) | NOT NULL | 호기 | "1호기" |
| PLC_NAME | VARCHAR(200) | NOT NULL | PLC 명칭 | "조립라인1 PLC" |
| PGM_ID | VARCHAR(50) | NULL | 현재 매핑된 프로그램 ID | "PGM00001" |
| PGM_MAPPING_DT | DATETIME | NULL | 마지막 매핑 일시 | 2025-10-17 10:30:00 |
| PGM_MAPPING_USER | VARCHAR(50) | NULL | 마지막 매핑 사용자 | "admin" |
| IS_ACTIVE | BOOLEAN | NOT NULL | 활성 상태 (삭제=FALSE) | TRUE |
| CREATE_DT | DATETIME | NOT NULL | 생성일시 | 2025-10-17 09:00:00 |
| CREATE_USER | VARCHAR(50) | NULL | 생성자 | "admin" |
| UPDATE_DT | DATETIME | NULL | 수정일시 | 2025-10-17 10:30:00 |
| UPDATE_USER | VARCHAR(50) | NULL | 수정자 | "admin" |

### 인덱스
```sql
-- Primary Key
PRIMARY KEY (PLC_ID)

-- 검색용 인덱스 (추가 권장)
CREATE INDEX idx_plant ON PLC_MASTER(PLANT);
CREATE INDEX idx_process ON PLC_MASTER(PROCESS);
CREATE INDEX idx_is_active ON PLC_MASTER(IS_ACTIVE);
CREATE INDEX idx_pgm_id ON PLC_MASTER(PGM_ID);
```

### 샘플 데이터
```sql
INSERT INTO PLC_MASTER VALUES
('M1CFB01000', 'P1', '조립', 'L1', '로봇', '1호기', '조립라인1 PLC', 
 'PGM00001', '2025-10-17 10:30:00', 'admin', 
 TRUE, '2025-10-17 09:00:00', 'admin', '2025-10-17 10:30:00', 'admin');
```

---

## 2️⃣ PROGRAMS

### 테이블 정의
```sql
CREATE TABLE PROGRAMS (
    PGM_ID VARCHAR(50) PRIMARY KEY,
    PGM_NAME VARCHAR(200) NOT NULL,
    DOCUMENT_ID VARCHAR(100),
    PGM_VERSION VARCHAR(20),
    DESCRIPTION VARCHAR(1000),
    CREATE_DT DATETIME NOT NULL DEFAULT NOW(),
    CREATE_USER VARCHAR(50),
    UPDATE_DT DATETIME,
    UPDATE_USER VARCHAR(50),
    NOTES VARCHAR(1000)
);
```

### SQLAlchemy 모델
```python
class Program(Base):
    __tablename__ = "PROGRAMS"
    
    pgm_id = Column('PGM_ID', String(50), primary_key=True)
    pgm_name = Column('PGM_NAME', String(200), nullable=False)
    document_id = Column('DOCUMENT_ID', String(100), nullable=True)
    pgm_version = Column('PGM_VERSION', String(20), nullable=True)
    description = Column('DESCRIPTION', String(1000), nullable=True)
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())
    create_user = Column('CREATE_USER', String(50), nullable=True)
    update_dt = Column('UPDATE_DT', DateTime, nullable=True, onupdate=func.now())
    update_user = Column('UPDATE_USER', String(50), nullable=True)
    notes = Column('NOTES', String(1000), nullable=True)
```

### 컬럼 설명
| 컬럼명 | 타입 | NULL | 설명 | 예시 |
|--------|------|------|------|------|
| PGM_ID | VARCHAR(50) | NOT NULL | 프로그램 ID (PK) | "PGM00001" |
| PGM_NAME | VARCHAR(200) | NOT NULL | 프로그램 명칭 | "조립 로봇 제어 프로그램" |
| DOCUMENT_ID | VARCHAR(100) | NULL | 연결된 문서 ID (FK) | "doc-uuid-123" |
| PGM_VERSION | VARCHAR(20) | NULL | 프로그램 버전 | "1.2.3" |
| DESCRIPTION | VARCHAR(1000) | NULL | 프로그램 설명 | "조립라인 로봇 제어용" |
| CREATE_DT | DATETIME | NOT NULL | 생성일시 | 2025-10-17 09:00:00 |
| CREATE_USER | VARCHAR(50) | NULL | 생성자 | "admin" |
| UPDATE_DT | DATETIME | NULL | 수정일시 | 2025-10-17 10:00:00 |
| UPDATE_USER | VARCHAR(50) | NULL | 수정자 | "admin" |
| NOTES | VARCHAR(1000) | NULL | 비고 | "테스트 완료" |

### 인덱스
```sql
PRIMARY KEY (PGM_ID)

-- 검색용 인덱스
CREATE INDEX idx_pgm_version ON PROGRAMS(PGM_VERSION);
CREATE INDEX idx_document_id ON PROGRAMS(DOCUMENT_ID);
```

### 샘플 데이터
```sql
INSERT INTO PROGRAMS VALUES
('PGM00001', '조립 로봇 제어 프로그램', 'doc-123', '1.0.0', 
 '조립라인 로봇 제어용', '2025-10-17 09:00:00', 'admin', 
 NULL, NULL, '초기 버전');
```

---

## 3️⃣ PGM_MAPPING_HISTORY

### 테이블 정의
```sql
CREATE TABLE PGM_MAPPING_HISTORY (
    HISTORY_ID INT PRIMARY KEY AUTO_INCREMENT,
    PLC_ID VARCHAR(50) NOT NULL,
    PGM_ID VARCHAR(50),
    
    -- 이력 메타데이터
    ACTION VARCHAR(20) NOT NULL,
    ACTION_DT DATETIME NOT NULL DEFAULT NOW(),
    ACTION_USER VARCHAR(50),
    
    -- 변경 전 정보
    PREV_PGM_ID VARCHAR(50),
    
    NOTES VARCHAR(500),
    
    INDEX idx_plc_id (PLC_ID),
    INDEX idx_action_dt (ACTION_DT)
);
```

### SQLAlchemy 모델
```python
class MappingAction(str, enum.Enum):
    CREATE = "CREATE"    # 최초 매핑
    UPDATE = "UPDATE"    # 프로그램 변경
    DELETE = "DELETE"    # 매핑 해제
    RESTORE = "RESTORE"  # 매핑 복원

class PgmMappingHistory(Base):
    __tablename__ = "PGM_MAPPING_HISTORY"
    
    history_id = Column('HISTORY_ID', Integer, primary_key=True, autoincrement=True)
    plc_id = Column('PLC_ID', String(50), nullable=False, index=True)
    pgm_id = Column('PGM_ID', String(50), nullable=True)
    
    action = Column('ACTION', String(20), nullable=False)
    action_dt = Column('ACTION_DT', DateTime, nullable=False, server_default=func.now(), index=True)
    action_user = Column('ACTION_USER', String(50), nullable=True)
    
    prev_pgm_id = Column('PREV_PGM_ID', String(50), nullable=True)
    notes = Column('NOTES', String(500), nullable=True)
```

### 컬럼 설명
| 컬럼명 | 타입 | NULL | 설명 | 예시 |
|--------|------|------|------|------|
| HISTORY_ID | INT | NOT NULL | 이력 ID (PK, AUTO_INCREMENT) | 1, 2, 3... |
| PLC_ID | VARCHAR(50) | NOT NULL | PLC ID | "M1CFB01000" |
| PGM_ID | VARCHAR(50) | NULL | 변경 후 프로그램 ID | "PGM00002" |
| ACTION | VARCHAR(20) | NOT NULL | 액션 타입 | "CREATE", "UPDATE", "DELETE" |
| ACTION_DT | DATETIME | NOT NULL | 액션 일시 | 2025-10-17 10:30:00 |
| ACTION_USER | VARCHAR(50) | NULL | 액션 사용자 | "admin" |
| PREV_PGM_ID | VARCHAR(50) | NULL | 변경 전 프로그램 ID | "PGM00001" |
| NOTES | VARCHAR(500) | NULL | 비고 | "버전 업그레이드" |

### 액션 타입
| ACTION | 설명 | 시나리오 |
|--------|------|----------|
| CREATE | 최초 매핑 | PLC에 처음으로 프로그램 매핑 |
| UPDATE | 프로그램 변경 | 기존 프로그램을 다른 프로그램으로 변경 |
| DELETE | 매핑 해제 | PLC에서 프로그램 매핑 제거 |
| RESTORE | 매핑 복원 | 이전에 삭제된 매핑을 다시 복원 |

### 인덱스
```sql
PRIMARY KEY (HISTORY_ID)
INDEX idx_plc_id (PLC_ID)
INDEX idx_action_dt (ACTION_DT)

-- 추가 권장 인덱스
CREATE INDEX idx_pgm_id ON PGM_MAPPING_HISTORY(PGM_ID);
CREATE INDEX idx_action ON PGM_MAPPING_HISTORY(ACTION);
```

### 샘플 데이터
```sql
-- 최초 매핑
INSERT INTO PGM_MAPPING_HISTORY 
(PLC_ID, PGM_ID, ACTION, ACTION_DT, ACTION_USER, PREV_PGM_ID, NOTES)
VALUES
('M1CFB01000', 'PGM00001', 'CREATE', '2025-10-17 10:00:00', 'admin', NULL, '최초 등록');

-- 프로그램 변경
INSERT INTO PGM_MAPPING_HISTORY 
(PLC_ID, PGM_ID, ACTION, ACTION_DT, ACTION_USER, PREV_PGM_ID, NOTES)
VALUES
('M1CFB01000', 'PGM00002', 'UPDATE', '2025-10-17 11:00:00', 'admin', 'PGM00001', '버전 업그레이드');

-- 매핑 해제
INSERT INTO PGM_MAPPING_HISTORY 
(PLC_ID, PGM_ID, ACTION, ACTION_DT, ACTION_USER, PREV_PGM_ID, NOTES)
VALUES
('M1CFB01000', NULL, 'DELETE', '2025-10-17 12:00:00', 'admin', 'PGM00002', '점검을 위한 해제');
```

---

## 4️⃣ PGM_TEMPLATE

### 테이블 정의
```sql
CREATE TABLE PGM_TEMPLATE (
    TEMPLATE_ID INT PRIMARY KEY AUTO_INCREMENT,
    PGM_ID VARCHAR(50) NOT NULL,
    DOCUMENT_ID VARCHAR(100),
    
    -- 계층 구조
    FOLDER_ID VARCHAR(50) NOT NULL,
    FOLDER_NAME VARCHAR(200) NOT NULL,
    SUB_FOLDER_ID VARCHAR(50),
    SUB_FOLDER_NAME VARCHAR(200),
    LOGIC_ID VARCHAR(50) NOT NULL,
    LOGIC_NAME VARCHAR(200) NOT NULL,
    
    DESCRIPTION VARCHAR(1000),
    CREATE_DT DATETIME NOT NULL DEFAULT NOW(),
    
    INDEX idx_pgm_id (PGM_ID),
    INDEX idx_document_id (DOCUMENT_ID)
);
```

### SQLAlchemy 모델
```python
class PgmTemplate(Base):
    __tablename__ = "PGM_TEMPLATE"
    
    template_id = Column('TEMPLATE_ID', Integer, primary_key=True, autoincrement=True)
    pgm_id = Column('PGM_ID', String(50), nullable=False, index=True)
    document_id = Column('DOCUMENT_ID', String(100), nullable=True, index=True)
    
    # 계층 구조
    folder_id = Column('FOLDER_ID', String(50), nullable=False)
    folder_name = Column('FOLDER_NAME', String(200), nullable=False)
    sub_folder_id = Column('SUB_FOLDER_ID', String(50), nullable=True)
    sub_folder_name = Column('SUB_FOLDER_NAME', String(200), nullable=True)
    logic_id = Column('LOGIC_ID', String(50), nullable=False)
    logic_name = Column('LOGIC_NAME', String(200), nullable=False)
    
    description = Column('DESCRIPTION', String(1000), nullable=True)
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())
```

### 컬럼 설명
| 컬럼명 | 타입 | NULL | 설명 | 예시 |
|--------|------|------|------|------|
| TEMPLATE_ID | INT | NOT NULL | 템플릿 ID (PK) | 1, 2, 3... |
| PGM_ID | VARCHAR(50) | NOT NULL | 프로그램 ID | "PGM00001" |
| DOCUMENT_ID | VARCHAR(100) | NULL | 원본 Excel 문서 ID | "doc-uuid-123" |
| FOLDER_ID | VARCHAR(50) | NOT NULL | Folder ID | "F001" |
| FOLDER_NAME | VARCHAR(200) | NOT NULL | Folder 명칭 | "초기화" |
| SUB_FOLDER_ID | VARCHAR(50) | NULL | Sub Folder ID | "SF001" |
| SUB_FOLDER_NAME | VARCHAR(200) | NULL | Sub Folder 명칭 | "설정" |
| LOGIC_ID | VARCHAR(50) | NOT NULL | Logic ID | "L001" |
| LOGIC_NAME | VARCHAR(200) | NOT NULL | Logic 명칭 | "시스템 초기화" |
| DESCRIPTION | VARCHAR(1000) | NULL | 설명 | "시스템 시작 시 초기화" |
| CREATE_DT | DATETIME | NOT NULL | 생성일시 | 2025-10-19 15:23:00 |

### 샘플 데이터
```sql
INSERT INTO PGM_TEMPLATE VALUES
(1, 'PGM00001', 'doc-123', 
 'F001', '초기화', 'SF001', '설정', 
 'L001', '시스템 초기화', 
 '시스템 시작 시 초기화', '2025-10-19 15:23:00');
```

---

## 5️⃣ DOCUMENTS ⭐ 업데이트

### 테이블 정의
```sql
CREATE TABLE DOCUMENTS (
    DOCUMENT_ID VARCHAR(100) PRIMARY KEY,
    FILENAME VARCHAR(255) NOT NULL,
    FILE_PATH VARCHAR(500) NOT NULL,
    FILE_SIZE BIGINT NOT NULL,
    DOCUMENT_TYPE VARCHAR(50) NOT NULL,
    UPLOAD_DT DATETIME NOT NULL DEFAULT NOW(),
    USER_ID VARCHAR(50) NOT NULL,
    IS_PUBLIC BOOLEAN NOT NULL DEFAULT FALSE,
    METADATA_JSON JSON  -- ⭐ S3 정보 포함
);
```

### SQLAlchemy 모델
```python
class Document(Base):
    __tablename__ = "DOCUMENTS"
    
    document_id = Column('DOCUMENT_ID', String(100), primary_key=True)
    filename = Column('FILENAME', String(255), nullable=False)
    file_path = Column('FILE_PATH', String(500), nullable=False)
    file_size = Column('FILE_SIZE', BigInteger, nullable=False)
    document_type = Column('DOCUMENT_TYPE', String(50), nullable=False)
    upload_dt = Column('UPLOAD_DT', DateTime, nullable=False, server_default=func.now())
    user_id = Column('USER_ID', String(50), nullable=False)
    is_public = Column('IS_PUBLIC', Boolean, nullable=False, server_default=false())
    metadata_json = Column('METADATA_JSON', JSON, nullable=True)  # ⭐
```

### 컬럼 설명
| 컬럼명 | 타입 | NULL | 설명 | 예시 |
|--------|------|------|------|------|
| DOCUMENT_ID | VARCHAR(100) | NOT NULL | 문서 ID (PK) | "doc-uuid-123" |
| FILENAME | VARCHAR(255) | NOT NULL | 원본 파일명 | "manual.pdf" |
| FILE_PATH | VARCHAR(500) | NOT NULL | 저장 경로 | "uploads/2025/10/uuid.pdf" |
| FILE_SIZE | BIGINT | NOT NULL | 파일 크기 (bytes) | 1048576 |
| DOCUMENT_TYPE | VARCHAR(50) | NOT NULL | 문서 타입 | "pdf", "zip", "pgm_template" |
| UPLOAD_DT | DATETIME | NOT NULL | 업로드 일시 | 2025-10-17 10:00:00 |
| USER_ID | VARCHAR(50) | NOT NULL | 업로드 사용자 | "admin" |
| IS_PUBLIC | BOOLEAN | NOT NULL | 공개 여부 | TRUE |
| METADATA_JSON | JSON | NULL | 메타데이터 (S3 정보 포함) ⭐ | {"storage_type": "s3", "s3_key": "..."} |

### ⭐ METADATA_JSON 구조

#### S3 스토리지 사용 시
```json
{
  "storage_type": "s3",
  "s3_key": "uploads/user123/document.pdf",
  "s3_url": "https://plc-documents.s3.ap-northeast-2.amazonaws.com/uploads/user123/document.pdf"
}
```

#### 로컬 스토리지 사용 시
```json
{
  "storage_type": "local"
}
```

#### 템플릿 파일 (pgm_template) 사용 시
```json
{
  "storage_type": "s3",
  "s3_key": "uploads/user123/template.xlsx",
  "s3_url": "https://...",
  "pgm_id": "PGM00001",
  "template_parse_result": {
    "total_count": 150,
    "folder_count": 10,
    "sub_folder_count": 25,
    "logic_count": 150
  }
}
```

### 샘플 데이터
```sql
-- 로컬 스토리지
INSERT INTO DOCUMENTS VALUES
('doc-local-123', 'manual.pdf', 'uploads/2025/10/local.pdf', 
 1048576, 'pdf', '2025-10-28 10:00:00', 'admin', 
 TRUE, '{"storage_type": "local"}');

-- S3 스토리지
INSERT INTO DOCUMENTS VALUES
('doc-s3-456', 'manual.pdf', 'https://plc-documents.s3.ap-northeast-2.amazonaws.com/uploads/user/manual.pdf', 
 1048576, 'pdf', '2025-10-28 11:00:00', 'admin', 
 TRUE, '{"storage_type": "s3", "s3_key": "uploads/user/manual.pdf", "s3_url": "https://..."}');
```

---

## 6️⃣ USERS

### 테이블 정의
```sql
CREATE TABLE USERS (
    USER_ID VARCHAR(50) PRIMARY KEY,
    USERNAME VARCHAR(50) UNIQUE NOT NULL,
    EMAIL VARCHAR(100) UNIQUE NOT NULL,
    FULL_NAME VARCHAR(100),
    IS_ACTIVE BOOLEAN NOT NULL DEFAULT TRUE,
    CREATE_DT DATETIME NOT NULL DEFAULT NOW(),
    UPDATE_DT DATETIME
);
```

---

## 7️⃣ GROUPS & GROUP_USERS

### GROUPS 테이블
```sql
CREATE TABLE GROUPS (
    GROUP_ID VARCHAR(50) PRIMARY KEY,
    GROUP_NAME VARCHAR(100) NOT NULL,
    DESCRIPTION VARCHAR(500),
    CREATE_DT DATETIME NOT NULL DEFAULT NOW(),
    CREATE_USER VARCHAR(50)
);
```

### GROUP_USERS 테이블 (N:M 관계)
```sql
CREATE TABLE GROUP_USERS (
    GROUP_ID VARCHAR(50) NOT NULL,
    USER_ID VARCHAR(50) NOT NULL,
    JOIN_DT DATETIME NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (GROUP_ID, USER_ID),
    FOREIGN KEY (GROUP_ID) REFERENCES GROUPS(GROUP_ID),
    FOREIGN KEY (USER_ID) REFERENCES USERS(USER_ID)
);
```

---

## 8️⃣ CHAT_HISTORY

### 테이블 정의
```sql
CREATE TABLE CHAT_HISTORY (
    CHAT_ID VARCHAR(100) PRIMARY KEY,
    USER_ID VARCHAR(50) NOT NULL,
    MESSAGE TEXT NOT NULL,
    RESPONSE TEXT NOT NULL,
    MODEL_NAME VARCHAR(50),
    CREATE_DT DATETIME NOT NULL DEFAULT NOW(),
    TOKENS_USED INT
);
```

---

## 🔗 테이블 관계도

```
USERS ────┐
          │
          ├─── GROUP_USERS ──── GROUPS
          │
          └─── DOCUMENTS (S3/로컬) ⭐
                    │
                    ├─── PROGRAMS ──── PGM_MAPPING_HISTORY ──── PLC_MASTER
                    │         │                                       │
                    │         └───────────────────────────────────────┘
                    │                  (현재 매핑 상태)
                    │
                    └─── PGM_TEMPLATE
                              └─── (Excel 파싱 결과)

USERS ──── CHAT_HISTORY
```

### 관계 설명
1. **PLC_MASTER ↔ PROGRAMS** (N:1 현재 상태)
   - PLC_MASTER.PGM_ID → PROGRAMS.PGM_ID
   - 한 PLC는 현재 1개의 프로그램만 매핑

2. **PLC_MASTER ↔ PGM_MAPPING_HISTORY** (1:N 이력)
   - PLC_MASTER.PLC_ID → PGM_MAPPING_HISTORY.PLC_ID
   - 모든 매핑 변경 이력 저장

3. **PROGRAMS ↔ DOCUMENTS** (N:1)
   - PROGRAMS.DOCUMENT_ID → DOCUMENTS.DOCUMENT_ID
   - 프로그램 매뉴얼 연결

4. **PGM_TEMPLATE ↔ DOCUMENTS** (N:1)
   - PGM_TEMPLATE.DOCUMENT_ID → DOCUMENTS.DOCUMENT_ID
   - 원본 Excel 파일 연결

5. **DOCUMENTS ⭐ 스토리지 위치** (S3/로컬)
   - metadata_json.storage_type으로 스토리지 유형 구분
   - S3: s3_key, s3_url 포함
   - Local: storage_type="local"만 포함

6. **USERS ↔ GROUP_USERS ↔ GROUPS** (N:M)
   - 사용자-그룹 다대다 관계

7. **USERS ↔ CHAT_HISTORY** (1:N)
   - 사용자별 채팅 기록

---

## 🎯 데이터 흐름 예시

### ⭐ S3 파일 업로드 시나리오
```
1. 파일 업로드
   → POST /v1/upload (STORAGE_TYPE=s3)
   → S3Client.upload_file()
   → S3 버킷에 파일 저장

2. DOCUMENTS 레코드 생성
   DOCUMENT_ID: "doc-s3-456"
   FILE_PATH: "https://plc-documents.s3.ap-northeast-2.amazonaws.com/..."
   METADATA_JSON: {
     "storage_type": "s3",
     "s3_key": "uploads/user/file.pdf",
     "s3_url": "https://..."
   }

3. 파일 다운로드
   → GET /v1/documents/{document_id}/download
   → metadata_json에서 storage_type 확인
   → S3Client.download_file(s3_key)
   → StreamingResponse 반환

4. 파일 삭제
   → DELETE /v1/documents/{document_id}
   → metadata_json에서 s3_key 추출
   → S3Client.delete_file(s3_key)
   → DOCUMENTS 레코드 삭제
```

### 프로그램 매핑 시나리오
```
1. PLC 생성
   → PLC_MASTER에 INSERT
   → PGM_ID = NULL (매핑 없음)

2. 프로그램 생성
   → PROGRAMS에 INSERT
   → PGM_ID = 'PGM00001'

3. 매핑 생성
   → PLC_MASTER.PGM_ID = 'PGM00001' UPDATE
   → PGM_MAPPING_HISTORY에 ACTION='CREATE' INSERT

4. 프로그램 변경
   → PLC_MASTER.PGM_ID = 'PGM00002' UPDATE
   → PGM_MAPPING_HISTORY에 ACTION='UPDATE' INSERT
   → PREV_PGM_ID = 'PGM00001'

5. 매핑 해제
   → PLC_MASTER.PGM_ID = NULL UPDATE
   → PGM_MAPPING_HISTORY에 ACTION='DELETE' INSERT
   → PREV_PGM_ID = 'PGM00002'
```

### Excel 템플릿 업로드 시나리오
```
1. Excel 파일 업로드
   → POST /v1/upload
   → document_type="pgm_template"
   → metadata='{"pgm_id": "PGM00001"}'

2. DOCUMENTS 저장 (S3 또는 로컬)
   → DOCUMENT_ID: "doc-template-789"
   → METADATA_JSON: {"pgm_id": "PGM00001", "storage_type": "s3", ...}

3. Excel 파싱
   → template_service.parse_and_save()
   → pd.read_excel()
   → 데이터 변환

4. PGM_TEMPLATE Bulk Insert
   → 기존 템플릿 삭제 (PGM_ID='PGM00001')
   → 새 템플릿 Bulk Insert
   → 각 행마다 DOCUMENT_ID='doc-template-789' 연결

5. DOCUMENTS metadata 업데이트
   → template_parse_result 추가
   → 파싱 통계 정보 저장
```

---

## 📊 예상 데이터 규모

| 테이블 | 예상 레코드 수 | 증가율 | 비고 |
|--------|----------------|--------|------|
| PLC_MASTER | 1,000 | 낮음 | PLC 장비 수 |
| PROGRAMS | 500 | 중간 | 프로그램 버전 관리 |
| PGM_MAPPING_HISTORY | 10,000+ | 높음 | 매핑 변경할 때마다 증가 |
| PGM_TEMPLATE | 50,000+ | 높음 | 프로그램당 평균 100개 템플릿 |
| DOCUMENTS | 1,000 | 중간 | 매뉴얼, Excel 등 (S3/로컬) ⭐ |
| USERS | 100 | 낮음 | 시스템 사용자 |
| CHAT_HISTORY | 50,000+ | 높음 | 채팅 사용량에 비례 |

---

## ✨ 최근 변경사항

### 2025-10-28 - S3 스토리지 통합
```
✅ DOCUMENTS.metadata_json에 S3 정보 추가
   - storage_type: "s3" or "local"
   - s3_key: S3 객체 키
   - s3_url: S3 접근 URL

✅ FILE_PATH 필드 사용 방식 변경
   - S3: S3 URL 저장
   - 로컬: 로컬 파일 경로 저장
```

---

**이 문서를 참조하면 모든 테이블 구조를 빠르게 확인할 수 있습니다!** 📚
