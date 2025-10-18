# 🏗️ PLC-Program Mapping System - 프로젝트 참조 가이드

> **최종 업데이트:** 2025-10-19 02:19:00 (일요일 오전 2시 19분)  
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
│   │   ├── plc_router.py         # PLC 관리 API ⭐ 업데이트
│   │   ├── program_router.py     # 프로그램 관리 API
│   │   └── user_router.py        # 사용자 관리 API
│   │
│   └── services/                 # Business Logic Layer
│       ├── document_service.py   # 문서 관리 비즈니스 로직
│       ├── group_service.py      # 그룹 관리 비즈니스 로직
│       ├── llm_chat_service.py   # LLM 채팅 비즈니스 로직
│       ├── llm_provider_factory.py # LLM Provider 팩토리
│       ├── pgm_history_service.py # 매핑 이력 비즈니스 로직
│       ├── plc_service.py        # PLC 관리 비즈니스 로직 ⭐ 업데이트
│       ├── program_service.py    # 프로그램 관리 비즈니스 로직
│       └── user_service.py       # 사용자 관리 비즈니스 로직
│
├── database/                     # Database Layer
│   ├── models/                   # SQLAlchemy Models
│   │   ├── plc_models.py         # PLCMaster 모델 ⭐
│   │   ├── program_models.py     # Program 모델
│   │   ├── mapping_models.py     # PgmMappingHistory 모델
│   │   └── ...
│   │
│   └── crud/                     # CRUD Operations
│       ├── plc_crud.py           # PLC CRUD
│       └── ...
│
└── types/                        # Type Definitions (Pydantic)
    └── response/                 # Response Models
        ├── plc_hierarchy_response.py # ⭐ NEW: 계층 구조 응답
        └── ...
```

---

## 🔗 API 엔드포인트 (총 52개)

### PLC API (plc_router.py) - 총 16개

**단일 PLC 리소스 (`/plc/{plc_id}`):**
```
GET    /v1/plc/{plc_id}             # PLC 조회
PUT    /v1/plc/{plc_id}             # PLC 수정
DELETE /v1/plc/{plc_id}             # PLC 삭제 (Soft Delete)
POST   /v1/plc/{plc_id}/restore     # PLC 복원
GET    /v1/plc/{plc_id}/exists      # PLC 존재 여부 확인
POST   /v1/plc/{plc_id}/mapping     # 프로그램 매핑 (UPSERT)
DELETE /v1/plc/{plc_id}/mapping     # 매핑 해제
GET    /v1/plc/{plc_id}/history     # PLC 매핑 이력
```

**PLC 컬렉션 리소스 (`/plcs`):**
```
POST   /v1/plcs                      # PLC 생성
GET    /v1/plcs                      # PLC 목록 (검색, 페이징, 필터링)
GET    /v1/plcs/search/keyword       # PLC 검색
GET    /v1/plcs/count/summary        # PLC 개수 조회
GET    /v1/plcs/hierarchy/values     # 계층별 고유 값 조회
GET    /v1/plcs/tree                 # PLC 계층 구조 트리 조회 ⭐ NEW
GET    /v1/plcs/unmapped/list        # 매핑되지 않은 PLC 목록
GET    /v1/programs/{pgm_id}/plcs    # 프로그램별 매핑된 PLC 목록
```

### Program API (program_router.py) - 5개
```
POST   /v1/programs                  # 프로그램 생성
GET    /v1/programs/{pgm_id}         # 프로그램 조회
GET    /v1/programs                  # 프로그램 목록 (검색, 페이징)
PUT    /v1/programs/{pgm_id}         # 프로그램 수정
DELETE /v1/programs/{pgm_id}         # 프로그램 삭제
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

---

## 🎯 핵심 기능 Flow

### ⭐ NEW: PLC 계층 구조 트리 조회 Flow (2025-10-17)
```
Client → GET /v1/plcs/tree?is_active=true
    ↓
plc_router.get_plc_tree(is_active)
    ↓
plc_service.get_plc_hierarchy(is_active)
    ├─ plc_service.get_plcs(is_active) 재사용
    │  └─ plc_crud.get_plcs() → PLC_MASTER 전체 조회
    ├─ _build_hierarchy() 계층 구조 변환
    │  └─ Plant → Process → Line → Equipment Group → Unit Data
    └─ _convert_to_response() Response 형식 변환

Response:
{
  "data": [
    {
      "plant": "PLT1",
      "processes": [
        {
          "process": "PLT1-PRC1",
          "lines": [
            {
              "line": "PLT1-PRC1-LN1",
              "equipment_groups": [
                {
                  "equipment_group": "PLT1-PRC1-LN1-EQ1",
                  "unit_data": [
                    {
                      "unit": "PLT1-PRC1-LN1-EQ1-U1",
                      "plc_id": "...",
                      "create_dt": "2023-10-01T10:00:00Z",
                      "user": "admin"  ← CREATE_USER 사용!
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

---

## 🗄️ 주요 테이블

### PLC_MASTER (⭐ 업데이트됨 - 2025-10-17)
```python
plc_id: str                    # PRIMARY KEY
plant: str                     # Plant (계층 1단계)
process: str                   # 공정 (계층 2단계)
line: str                      # Line (계층 3단계)
equipment_group: str           # 장비그룹 (계층 4단계)
unit: str                      # 호기 (계층 5단계)
plc_name: str                  # PLC 명칭

# 프로그램 매핑
pgm_id: str                    # 현재 매핑된 프로그램 ID
pgm_mapping_dt: datetime       # 마지막 매핑 일시
pgm_mapping_user: str          # 마지막 매핑 사용자

# 메타데이터
is_active: bool                # 활성 상태
create_dt: datetime            # 생성일시
create_user: str               # 생성자 ⭐ 확인됨 (실제 존재)
update_dt: datetime            # 수정일시
update_user: str               # 수정자 ⭐ 확인됨 (실제 존재)
```

---

## ✨ 최근 변경사항

### 2025-10-19 02:19:00 - PLC 트리 조회 API 구현 완료 (일요일 오전 2시 19분)

**구현 완료된 컴포넌트:**
```
1. ✅ plc_router.py - get_plc_tree() 엔드포인트
   - GET /v1/plcs/tree?is_active=true
   - PlcTreeResponse 반환
   - 계층 구조 트리 조회

2. ✅ plc_service.py - get_plc_tree() 메서드
   - PLC 목록 조회 후 계층 구조 변환
   - 통계 정보 포함 (total_count, filtered_count)
   - timestamp 추가

3. ✅ plc_response.py - PlcTreeResponse 타입
   - data: List[PlcHierarchy]
   - total_count: int
   - filtered_count: int
   - timestamp: datetime

4. ✅ plc-tree.html - 트리 시각화 페이지
   - 심플하고 미니멀한 디자인
   - 펼치기/접기 기능
   - JSON 원본 보기
   - 실시간 트리 렌더링
```

**API 비교:**
```
기존: GET /v1/plc/hierarchy  (PlcHierarchyResponse)
새로: GET /v1/plcs/tree      (PlcTreeResponse) ⭐

차이점:
- /plcs/tree는 통계 정보 포함 (total_count, filtered_count)
- /plcs/tree는 timestamp 포함
- 더 구조화된 응답 형식
```

---

### 2025-10-18 - PLC API 엔드포인트 단수/복수 구분

### ⭐ PLC API 엔드포인트 단수/복수 구분 (Singular/Plural)
```
1. ✅ plc_router.py 라우트 경로 변경
   - 단일 PLC: /plcs/{plc_id} → /plc/{plc_id}
   - 컬렉션: /plcs (유지)
   - 라우팅 충돌 해결 및 RESTful 설계 개선

2. ✅ 변경된 엔드포인트 (단일 리소스)
   - GET    /v1/plc/{plc_id}              # PLC 조회
   - PUT    /v1/plc/{plc_id}              # PLC 수정
   - DELETE /v1/plc/{plc_id}              # PLC 삭제
   - POST   /v1/plc/{plc_id}/restore      # PLC 복원
   - GET    /v1/plc/{plc_id}/exists       # 존재 여부
   - POST   /v1/plc/{plc_id}/mapping      # 프로그램 매핑
   - DELETE /v1/plc/{plc_id}/mapping      # 매핑 해제
   - GET    /v1/plc/{plc_id}/history      # 매핑 이력

3. ✅ 유지된 엔드포인트 (컬렉션)
   - POST   /v1/plcs                      # PLC 생성
   - GET    /v1/plcs                      # PLC 목록
   - GET    /v1/plcs/search/keyword       # 검색
   - GET    /v1/plcs/count/summary        # 개수
   - GET    /v1/plcs/hierarchy/values     # 계층 값
   - GET    /v1/plcs/tree                 # 트리 구조 ⭐
   - GET    /v1/plcs/unmapped/list        # 미매핑 목록

4. ✅ HTML 테스트 페이지 추가
   - plc-tree.html 생성 (심플 디자인)
   - main.py에 /plc-tree 경로 추가
   - 트리 구조 시각화, 펼치기/접기, JSON 보기 기능
   - Console 디버그 로그 추가

5. ✅ PostgreSQL 대소문자 구분 이슈 해결
   - 테이블명에 큰따옴표 사용 ("PLC_MASTER")
   - check_db.py 스크립트 생성
```

### ⭐ PLC 계층 구조 트리 조회 API 추가 (2025-10-17)
```
1. ✅ plc_hierarchy_response.py 생성
   - UnitData, EquipmentGroup, Line, Process, Plant, PlcTreeResponse 모델

2. ✅ plc_service.py 메서드 추가
   - get_plc_hierarchy(is_active) - 계층 구조 조회
   - _build_hierarchy(plcs) - 딕셔너리 변환
   - _convert_to_response(hierarchy) - Response 형식 변환

3. ✅ plc_router.py 엔드포인트 추가
   - GET /v1/plcs/tree?is_active=true
   - 파라미터: is_active만 사용 (plant, process 제거)

4. ✅ PLC_MASTER 테이블 구조 확인
   - CREATE_USER, UPDATE_USER 컬럼 실제 존재 확인
   - 기존 문서와 실제 코드 일치 확인
```

---

## 🔍 빠른 검색 키워드

- **PLC 관련**: plc_models.py, plc_crud.py, plc_service.py, plc_router.py
- **프로그램 관련**: program_models.py, program_crud.py, program_service.py, program_router.py
- **매핑 이력**: mapping_models.py, mapping_crud.py, pgm_history_service.py, pgm_history_router.py
- **계층 구조**: plc_hierarchy_response.py, get_plc_hierarchy(), /v1/plcs/tree ⭐ NEW
- **문서 관리**: document_models.py, document_service.py, document_router.py

---

## 🚀 서버 실행

```bash
cd D:\project-template\chat-api\app\backend
python -m uvicorn ai_backend.main:app --reload --port 8000
```

**Swagger UI:** http://localhost:8000/docs

---

**이 문서를 활용하면 Claude가 매번 파일을 검색하지 않고도 프로젝트 구조를 빠르게 파악할 수 있습니다!** 🚀
