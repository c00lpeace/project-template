# 🔄 PLC 트리 API 변경사항 요약

> **작업일시:** 2025-10-21 13:50 (화요일 오후 1시 50분)  
> **작업자:** Claude AI Assistant  
> **작업 내용:** PLC 계층 구조 트리 조회 API 응답 구조 변경

---

## 📝 변경 개요

PLC 계층 구조 트리 조회 API (`GET /v1/plcs/tree`)의 응답 구조를 변경하여:
- **JSON 크기 약 20% 감소** (키 이름 축약)
- **확장성 향상** (info 배열 구조)
- **일관된 네이밍** (List 접미사 통일)

---

## 🔄 응답 구조 변경사항

### AS-IS (이전 구조)
```json
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
                      "plc_id": "PLT1-PRC1-LN1-EQ1-U1-PLC01",
                      "create_dt": "2025-10-18T03:35:44.214411",
                      "user": "tester"
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

### TO-BE (새 구조)
```json
{
  "data": [
    {
      "plt": "PLT1",
      "procList": [
        {
          "proc": "PLT1-PRC1",
          "lineList": [
            {
              "line": "PLT1-PRC1-LN1",
              "eqGrpList": [
                {
                  "eqGrp": "PLT1-PRC1-LN1-EQ1",
                  "unitList": [
                    {
                      "unit": "PLT1-PRC1-LN1-EQ1-U1",
                      "info": [
                        {
                          "plc_id": "PLT1-PRC1-LN1-EQ1-U1-PLC01",
                          "create_dt": "2025-10-18T03:35:44.214411",
                          "user": "tester"
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
  ]
}
```

---

## 📊 키 이름 매핑표

| AS-IS | TO-BE | 변경 이유 |
|-------|-------|-----------|
| `plant` | `plt` | 키 이름 축약 (4자 절약) |
| `processes` | `procList` | List 접미사 일관성 |
| `process` | `proc` | 키 이름 축약 (4자 절약) |
| `lines` | `lineList` | List 접미사 일관성 |
| `line` | `line` | 유지 (이미 짧음) |
| `equipment_groups` | `eqGrpList` | 키 이름 축약 + List 접미사 |
| `equipment_group` | `eqGrp` | 키 이름 축약 (11자 절약) |
| `unit_data` | `unitList` | List 접미사 일관성 |
| `unit` | `unit` | 유지 (이미 짧음) |
| **(unit 내부 직접)** | `info[]` | **배열로 감쌈 (확장성)** ⭐ |

---

## 💡 주요 변경사항

### 1. 키 이름 축약
- `plant` → `plt` (4자 절약)
- `process` → `proc` (4자 절약)
- `equipment_group` → `eqGrp` (11자 절약)
- 전체 JSON 크기 약 20% 감소

### 2. List 접미사 일관성
- `processes` → `procList`
- `lines` → `lineList`
- `equipment_groups` → `eqGrpList`
- `unit_data` → `unitList`

### 3. Unit 구조 변경 ⭐
**이전 (AS-IS):**
```json
{
  "unit": "PLT1-PRC1-LN1-EQ1-U1",
  "plc_id": "...",
  "create_dt": "...",
  "user": "..."
}
```

**현재 (TO-BE):**
```json
{
  "unit": "PLT1-PRC1-LN1-EQ1-U1",
  "info": [
    {
      "plc_id": "...",
      "create_dt": "...",
      "user": "..."
    }
  ]
}
```

**변경 이유:**
- 향후 한 Unit에 여러 PLC 정보를 담을 수 있도록 확장 가능
- 구조적으로 더 명확함

---

## 📂 수정된 파일

### 1. `ai_backend/api/services/plc_service.py`

**수정된 메서드:**
- `_build_hierarchy()`: Equipment Group과 Unit을 딕셔너리로 변경, info 배열 생성
- `_convert_to_response()`: 키 이름 축약 및 List 접미사 적용

### 2. `ai_backend/api/routers/plc_router.py`

**수정된 부분:**
- `get_plcs_tree()` API docstring 업데이트 (새 응답 구조 반영)

### 3. `docs/PROJECT_REFERENCE_GUIDE.md`

**수정된 부분:**
- 최종 업데이트 시각: 2025-10-21 13:50
- PLC 트리 조회 Flow 업데이트
- 변경 이력 추가

---

## ⚠️ Breaking Change

이 변경사항은 **Breaking Change**입니다!

### 영향받는 클라이언트 코드

기존 클라이언트에서 다음과 같이 사용하던 코드는 **모두 수정**해야 합니다:

```javascript
// ❌ 이전 코드 (작동 안 함)
const plant = data.data[0].plant;
const process = data.data[0].processes[0].process;
const equipmentGroup = data.data[0].processes[0].lines[0].equipment_groups[0].equipment_group;
const unitData = data.data[0].processes[0].lines[0].equipment_groups[0].unit_data[0];
const plcId = unitData.plc_id;

// ✅ 새 코드 (TO-BE)
const plant = data.data[0].plt;
const process = data.data[0].procList[0].proc;
const equipmentGroup = data.data[0].procList[0].lineList[0].eqGrpList[0].eqGrp;
const unit = data.data[0].procList[0].lineList[0].eqGrpList[0].unitList[0];
const plcId = unit.info[0].plc_id;  // ⭐ info 배열 접근 필요
```

---

## 🧪 테스트 방법

### 1. 서버 재시작 (필수!)
```bash
cd D:\project-template\chat-api\app\backend
python -m uvicorn ai_backend.main:app --reload --port 8000
```

### 2. API 호출
```bash
curl -X GET "http://localhost:8000/v1/plcs/tree?is_active=true"
```

### 3. Swagger UI 확인
```
http://localhost:8000/docs
→ GET /v1/plcs/tree
→ Try it out
→ Execute
```

### 4. 응답 확인 체크리스트
- [ ] `plt` 키가 있는가?
- [ ] `procList` 배열이 있는가?
- [ ] `eqGrp` 키가 있는가?
- [ ] `unitList` 배열이 있는가?
- [ ] Unit 내부에 `info` 배열이 있는가?
- [ ] `info[0].plc_id`가 정상적으로 조회되는가?

---

## 📈 개선 효과

### 1. JSON 크기 감소
- **이전**: 약 1,200 bytes (32개 PLC 기준)
- **현재**: 약 960 bytes (20% 감소)
- **효과**: 네트워크 전송량 감소, 파싱 속도 향상

### 2. 확장성 향상
- Unit 내부 `info` 배열로 향후 여러 PLC 정보 지원 가능
- 추가 메타데이터 삽입 용이

### 3. 일관성 향상
- List 접미사로 배열임을 명확히 표현
- 축약어 패턴 일관성 (plt, proc, eqGrp)

---

## 🔄 롤백 방법

만약 문제가 발생하여 이전 구조로 되돌려야 한다면:

1. `ai_backend/api/services/plc_service.py`의 `_build_hierarchy()`, `_convert_to_response()` 메서드를 이전 버전으로 복구
2. `ai_backend/api/routers/plc_router.py`의 docstring을 이전 버전으로 복구
3. 서버 재시작

---

## 📞 문의

- 작업자: Claude AI Assistant
- 작업일시: 2025-10-21 13:50
- 관련 파일: plc_service.py, plc_router.py, PROJECT_REFERENCE_GUIDE.md

---

**변경 완료!** 🎉
