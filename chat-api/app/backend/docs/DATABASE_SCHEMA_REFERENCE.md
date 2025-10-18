# 🗄️ Database Schema Reference

> **최종 업데이트:** 2025-10-17  
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
