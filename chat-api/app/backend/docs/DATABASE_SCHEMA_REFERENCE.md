# 🗄️ Database Schema Reference

> **최종 업데이트:** 2025-10-20 01:31:00 (일요일 오전 1시 31분)  
> **목적:** 모든 테이블 구조와 관계를 한눈에 파악  
> **⭐ 중요:** 실제 코드 기준으로 작성됨

---

## 📊 테이블 목록

| 테이블명 | 설명 | 모델 파일 | 주요 용도 |
|---------|------|-----------|-----------|
| PLC_MASTER | PLC 마스터 정보 | plc_models.py | PLC 기본 정보 + 현재 매핑 상태 |
| PROGRAMS | 프로그램 마스터 | program_models.py | 프로그램 기본 정보 |
| PGM_MAPPING_HISTORY | 매핑 변경 이력 | mapping_models.py | 모든 매핑 변경 감사 추적 |
| DOCUMENTS | 문서 정보 | document_models.py | 업로드된 파일 메타데이터 |
| USERS | 사용자 정보 | user_models.py | 사용자 계정 |
| GROUPS | 그룹 정보 | group_models.py | 사용자 그룹 |
| GROUP_USERS | 그룹-사용자 매핑 | group_models.py | N:M 관계 |
| CHAT_HISTORY | 채팅 이력 | chat_models.py | LLM 대화 기록 |

---

## 1️⃣ PLC_MASTER ⭐ (업데이트됨 - 2025-10-17)

### SQLAlchemy 모델 (실제 코드 확인)
```python
# D:\project-template\chat-api\app\backend\ai_backend\database\models\plc_models.py

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
    
    # 메타데이터 ⭐ 실제 코드 확인됨
    is_active = Column('IS_ACTIVE', Boolean, nullable=False, server_default=true())
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())
    create_user = Column('CREATE_USER', String(50), nullable=True)  # ⭐ 존재!
    update_dt = Column('UPDATE_DT', DateTime, nullable=True)
    update_user = Column('UPDATE_USER', String(50), nullable=True)  # ⭐ 존재!
```

### 컬럼 설명
| 컬럼명 | 타입 | NULL | 설명 | 예시 |
|--------|------|------|------|------|
| PLC_ID | VARCHAR(50) | NOT NULL | PLC 고유 ID (PK) | "M1CFB01000" |
| PLANT | VARCHAR(100) | NOT NULL | Plant (계층 1단계) | "PLT1" |
| PROCESS | VARCHAR(100) | NOT NULL | 공정 (계층 2단계) | "PLT1-PRC1" |
| LINE | VARCHAR(100) | NOT NULL | Line (계층 3단계) | "PLT1-PRC1-LN1" |
| EQUIPMENT_GROUP | VARCHAR(100) | NOT NULL | 장비그룹 (계층 4단계) | "PLT1-PRC1-LN1-EQ1" |
| UNIT | VARCHAR(100) | NOT NULL | 호기 (계층 5단계) | "PLT1-PRC1-LN1-EQ1-U1" |
| PLC_NAME | VARCHAR(200) | NOT NULL | PLC 명칭 | "조립라인1 PLC" |
| PGM_ID | VARCHAR(50) | NULL | 현재 매핑된 프로그램 ID | "PGM00001" |
| PGM_MAPPING_DT | DATETIME | NULL | 마지막 매핑 일시 | 2025-10-17 10:30:00 |
| PGM_MAPPING_USER | VARCHAR(50) | NULL | 마지막 매핑 사용자 | "admin" |
| IS_ACTIVE | BOOLEAN | NOT NULL | 활성 상태 (삭제=FALSE) | TRUE |
| CREATE_DT | DATETIME | NOT NULL | 생성일시 | 2025-10-17 09:00:00 |
| **CREATE_USER** ⭐ | VARCHAR(50) | NULL | **생성자** | **"admin"** |
| UPDATE_DT | DATETIME | NULL | 수정일시 | 2025-10-17 10:30:00 |
| **UPDATE_USER** ⭐ | VARCHAR(50) | NULL | **수정자** | **"admin"** |

### 계층 구조 (Hierarchy) ⭐
```
PLC_MASTER의 5단계 계층:

1. PLANT          (예: "PLT1")
   ↓
2. PROCESS        (예: "PLT1-PRC1")
   ↓
3. LINE           (예: "PLT1-PRC1-LN1")
   ↓
4. EQUIPMENT_GROUP (예: "PLT1-PRC1-LN1-EQ1")
   ↓
5. UNIT           (예: "PLT1-PRC1-LN1-EQ1-U1")
   + PLC_ID       (예: "PLT1-PRC1-LN1-EQ1-U1-PLC01")
   + CREATE_USER  (예: "admin") ← /v1/plcs/tree에서 사용
```

---

## 2️⃣ PROGRAMS

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

---

## 3️⃣ PGM_MAPPING_HISTORY

### SQLAlchemy 모델
```python
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

### 액션 타입
| ACTION | 설명 | 시나리오 |
|--------|------|----------|
| CREATE | 최초 매핑 | PLC에 처음으로 프로그램 매핑 |
| UPDATE | 프로그램 변경 | 기존 프로그램을 다른 프로그램으로 변경 |
| DELETE | 매핑 해제 | PLC에서 프로그램 매핑 제거 |
| RESTORE | 매핑 복원 | 이전에 삭제된 매핑을 다시 복원 |

---

## 4️⃣ PGM_TEMPLATE ⭐ NEW (2025-10-19)

### 테이블 정의
```sql
CREATE TABLE PGM_TEMPLATE (
    TEMPLATE_ID INT PRIMARY KEY AUTO_INCREMENT,
    
    -- 문서 연결 (원본 Excel 파일)
    DOCUMENT_ID VARCHAR(100),
    
    -- 프로그램 참조
    PGM_ID VARCHAR(50) NOT NULL,
    
    -- 폴더 구조 (3단계 계층)
    FOLDER_ID VARCHAR(20) NOT NULL,
    FOLDER_NAME VARCHAR(200) NOT NULL,
    SUB_FOLDER_NAME VARCHAR(200),
    
    -- 로직 정보
    LOGIC_ID VARCHAR(20) NOT NULL,
    LOGIC_NAME VARCHAR(200) NOT NULL,
    
    -- 메타데이터
    CREATE_DT DATETIME NOT NULL DEFAULT NOW(),
    CREATE_USER VARCHAR(50),
    
    -- 인덱스
    INDEX idx_document_id (DOCUMENT_ID),
    INDEX idx_pgm_id (PGM_ID),
    INDEX idx_folder_id (FOLDER_ID),
    INDEX idx_logic_id (LOGIC_ID),
    INDEX idx_pgm_folder_logic (PGM_ID, FOLDER_ID, LOGIC_ID)
);
```

### SQLAlchemy 모델
```python
class PgmTemplate(Base):
    __tablename__ = "PGM_TEMPLATE"
    
    template_id = Column('TEMPLATE_ID', Integer, primary_key=True, autoincrement=True)
    document_id = Column('DOCUMENT_ID', String(100), nullable=True)
    pgm_id = Column('PGM_ID', String(50), nullable=False)
    folder_id = Column('FOLDER_ID', String(20), nullable=False)
    folder_name = Column('FOLDER_NAME', String(200), nullable=False)
    sub_folder_name = Column('SUB_FOLDER_NAME', String(200), nullable=True)
    logic_id = Column('LOGIC_ID', String(20), nullable=False)
    logic_name = Column('LOGIC_NAME', String(200), nullable=False)
    create_dt = Column('CREATE_DT', DateTime, nullable=False, server_default=func.now())
    create_user = Column('CREATE_USER', String(50), nullable=True)
```

### 컬럼 설명
| 컬럼명 | 타입 | NULL | 설명 | 예시 |
|--------|------|------|------|------|
| TEMPLATE_ID | INT | NOT NULL | 템플릿 ID (PK, AUTO_INCREMENT) | 1, 2, 3... |
| DOCUMENT_ID | VARCHAR(100) | NULL | 원본 Excel 문서 ID | "doc-uuid-123" |
| PGM_ID | VARCHAR(50) | NOT NULL | 프로그램 ID (FK → PROGRAMS.PGM_ID) | "PGM001" |
| FOLDER_ID | VARCHAR(20) | NOT NULL | 폴더 ID | "0", "20", "40" |
| FOLDER_NAME | VARCHAR(200) | NOT NULL | 폴더 명칭 | "Unit01_Endplate Box Loader" |
| SUB_FOLDER_NAME | VARCHAR(200) | NULL | 서브 폴더 명칭 | "Assy11_Endplate Box Loader" |
| LOGIC_ID | VARCHAR(20) | NOT NULL | 로직 ID | "0000_11", "0001_11" |
| LOGIC_NAME | VARCHAR(200) | NOT NULL | 로직 명칭 | "Mode", "Input", "Interlock" |
| CREATE_DT | DATETIME | NOT NULL | 생성일시 | 2025-10-19 15:00:00 |
| CREATE_USER | VARCHAR(50) | NULL | 생성자 | "admin" |

### 샘플 데이터
```sql
INSERT INTO PGM_TEMPLATE VALUES
(1, 'doc-123', 'PGM001', '0', 'Unit01_Endplate Box Loader', 'Assy11_Endplate Box Loader', 
 '0000_11', 'Mode', '2025-10-19 15:00:00', 'admin'),
(2, 'doc-123', 'PGM001', '0', 'Unit01_Endplate Box Loader', 'Assy11_Endplate Box Loader', 
 '0001_11', 'Input', '2025-10-19 15:00:00', 'admin'),
(3, 'doc-123', 'PGM001', '0', 'Unit01_Endplate Box Loader', 'Assy11_Endplate Box Loader', 
 '0002_11', 'Interlock', '2025-10-19 15:00:00', 'admin');
```

### 계층 구조 (Hierarchy) ⭐
```
PGM_TEMPLATE의 3단계 계층:

1. FOLDER (Folder ID + Folder Name)
   ↓
2. SUB_FOLDER (Sub Folder Name)
   ↓
3. LOGIC (Logic ID + Logic Name)

예시:
PGM001
  └─ Folder: 0 "Unit01_Endplate Box Loader"
      └─ Sub Folder: "Assy11_Endplate Box Loader"
          ├─ Logic: 0000_11 "Mode"
          ├─ Logic: 0001_11 "Input"
          └─ Logic: 0002_11 "Interlock"
```

### 인덱스
```sql
PRIMARY KEY (TEMPLATE_ID)
INDEX idx_document_id (DOCUMENT_ID)
INDEX idx_pgm_id (PGM_ID)
INDEX idx_folder_id (FOLDER_ID)
INDEX idx_logic_id (LOGIC_ID)
INDEX idx_pgm_folder_logic (PGM_ID, FOLDER_ID, LOGIC_ID)
```

---

## 🔗 테이블 관계도

```
USERS ────┐
          │
          ├─── PLC_MASTER (CREATE_USER, UPDATE_USER) ⭐
          │         │
          │         ├─── PROGRAMS (PGM_ID)
          │         │
          │         └─── PGM_MAPPING_HISTORY (PLC_ID)
          │
          └─── DOCUMENTS ──── PROGRAMS (DOCUMENT_ID)
```

---

## 🎯 데이터 흐름 예시

### ⭐ NEW: PLC 계층 구조 트리 조회 시나리오 (2025-10-17)
```
1. GET /v1/plcs/tree?is_active=true 요청

2. plc_service.get_plc_hierarchy(is_active=true) 호출
   → plc_service.get_plcs(is_active=true) 재사용
   
3. PLC_MASTER 조회
   SELECT * FROM PLC_MASTER
   WHERE IS_ACTIVE = TRUE
   ORDER BY PLANT, PROCESS, LINE, EQUIPMENT_GROUP, UNIT

4. 계층 구조 변환 (_build_hierarchy)
   {
     "PLT1": {
       "PLT1-PRC1": {
         "PLT1-PRC1-LN1": {
           "PLT1-PRC1-LN1-EQ1": [
             {
               "unit": "PLT1-PRC1-LN1-EQ1-U1",
               "plc_id": "...",
               "create_dt": "...",
               "user": "admin"  ← CREATE_USER 사용!
             }
           ]
         }
       }
     }
   }

5. Response 형식으로 변환 (_convert_to_response)
   → data: [Plant[Process[Line[EquipmentGroup[UnitData[]]]]]]
```

---

## 📝 중요 변경사항 (2025-10-17)

### ⭐ PLC_MASTER 테이블 구조 확인
```diff
✅ 실제 코드 확인 결과:
+ CREATE_USER VARCHAR(50)  # 실제 존재 (plc_models.py)
+ UPDATE_USER VARCHAR(50)  # 실제 존재 (plc_models.py)
```

**변경 사유:**
- 실제 코드(plc_models.py)를 확인하여 문서 현행화
- 다른 테이블(PROGRAMS, GROUPS)과의 일관성 확인
- PLC 계층 구조 트리 조회 API에서 user 필드로 활용

**영향:**
- ✅ PLC 생성 시 CREATE_USER 저장 가능
- ✅ PLC 수정 시 UPDATE_USER 저장 가능
- ✅ GET /v1/plcs/tree API의 unit_data.user 필드에 사용
- ✅ 감사 추적(Audit Trail) 기능 강화

---

**이 문서는 실제 코드를 기준으로 작성되었습니다!** 📚  
**파일 위치:** `D:\project-template\chat-api\app\backend\ai_backend\database\models\plc_models.py`
