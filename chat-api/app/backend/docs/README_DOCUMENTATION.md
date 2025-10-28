# 📚 프로젝트 참조 문서 인덱스

> **프로젝트:** PLC-Program Mapping System  
> **경로:** `D:\project-template\chat-api\app\backend\`  
> **최종 업데이트:** 2025-10-28

---

## 🎯 문서 활용 방법

Claude에게 새로운 질문을 할 때, 아래 문서들을 먼저 참조하면 **파일 검색 시간을 절약**할 수 있습니다!

---

## 📑 참조 문서 목록

### 1. **PROJECT_REFERENCE_GUIDE.md** ⭐
**용도:** 프로젝트 전체 구조 파악

**포함 내용:**
- ✅ 디렉토리 구조 (전체)
- ✅ 모든 파일 위치
- ✅ API 엔드포인트 목록 (62개+)
- ✅ 아키텍처 패턴
- ✅ 의존성 주입 구조
- ✅ 설정 파일 (.env, settings.py)
- ✅ Naming Convention
- ✅ 개발 가이드
- ✅ **S3 스토리지 설정** ⭐ NEW

**언제 보면 좋을까?**
- 새로운 기능 추가할 때
- 파일 위치를 모를 때
- API 엔드포인트 확인할 때
- 프로젝트 구조를 처음 파악할 때
- S3 스토리지 설정 확인할 때 ⭐

---

### 2. **DATABASE_SCHEMA_REFERENCE.md** ⭐
**용도:** 데이터베이스 테이블 구조 파악

**포함 내용:**
- ✅ 모든 테이블 스키마 (9개)
- ✅ 컬럼별 상세 설명
- ✅ 인덱스 정보
- ✅ 샘플 데이터
- ✅ 테이블 관계도
- ✅ 데이터 흐름 예시
- ✅ SQLAlchemy 모델 코드
- ✅ **DOCUMENTS 테이블 S3 메타데이터** ⭐ NEW

**언제 보면 좋을까?**
- DB 관련 작업할 때
- 테이블 구조 확인할 때
- 관계 파악할 때
- 쿼리 작성할 때
- S3 메타데이터 구조 확인할 때 ⭐

---

### 3. **PROJECT_COMPLETION_REPORT.md**
**용도:** 최근 작업 내역 확인

**포함 내용:**
- ✅ 구현 완료 항목 (2025-10-28까지)
- ✅ 생성된 파일 목록
- ✅ API 엔드포인트 상세
- ✅ 코드 구조 분석
- ✅ 실행 방법
- ✅ 테스트 예시
- ✅ **S3 스토리지 통합 작업 내역** ⭐ NEW

**언제 보면 좋을까?**
- 최근 작업 내용 확인할 때
- 새로 추가된 기능 파악할 때
- 완료 체크리스트 확인할 때
- S3 작업 이력 확인할 때 ⭐

---

### 4. **S3_STORAGE_IMPLEMENTATION.md** ⭐ NEW
**용도:** S3 스토리지 상세 구현 가이드

**포함 내용:**
- ✅ S3 통합 개요
- ✅ 변경된 파일 목록
- ✅ 상세 변경 내역
- ✅ 사용 방법 (로컬/S3)
- ✅ 로그 확인 방법
- ✅ 문제 해결 (Troubleshooting)
- ✅ AWS S3 설정 가이드
- ✅ 주의사항 (보안, 비용, 성능)

**언제 보면 좋을까?**
- S3 스토리지 설정할 때
- S3 관련 에러 해결할 때
- AWS 설정 방법 확인할 때
- S3 비용/성능 정보 확인할 때

---

### 5. **S3_STORAGE_INTEGRATION.md** ⭐ NEW
**용도:** S3 작업 컨텍스트 및 빠른 참조

**포함 내용:**
- ✅ 작업 목표 및 배경
- ✅ 구현 완료 항목 요약
- ✅ 변경된 파일 간략 설명
- ✅ 사용 방법 (간단)
- ✅ 핵심 설계 원칙
- ✅ 테스트 체크리스트
- ✅ 다음 작업 제안

**언제 보면 좋을까?**
- S3 작업 컨텍스트 빠르게 파악할 때
- 새 대화에서 이어서 작업할 때
- S3 관련 빠른 참조가 필요할 때

---

## 🔍 빠른 검색 가이드

### 질문 유형별 추천 문서

| 질문 유형 | 추천 문서 | 예시 질문 |
|----------|----------|----------|
| **파일 위치** | PROJECT_REFERENCE_GUIDE.md | "PLC Service는 어디에?" |
| **API 엔드포인트** | PROJECT_REFERENCE_GUIDE.md | "프로그램 생성 API는?" |
| **테이블 구조** | DATABASE_SCHEMA_REFERENCE.md | "PLC_MASTER 테이블 구조는?" |
| **컬럼 설명** | DATABASE_SCHEMA_REFERENCE.md | "PGM_ID가 뭐야?" |
| **관계 파악** | DATABASE_SCHEMA_REFERENCE.md | "PLC와 프로그램 관계는?" |
| **최근 작업** | PROJECT_COMPLETION_REPORT.md | "어떤 API가 추가됐어?" |
| **아키텍처** | PROJECT_REFERENCE_GUIDE.md | "계층 구조는?" |
| **설정** | PROJECT_REFERENCE_GUIDE.md | ".env 파일은?" |
| **S3 설정** | S3_STORAGE_IMPLEMENTATION.md ⭐ | "S3 어떻게 설정해?" |
| **S3 에러** | S3_STORAGE_IMPLEMENTATION.md ⭐ | "S3 업로드 실패 해결법?" |
| **S3 작업 이력** | S3_STORAGE_INTEGRATION.md ⭐ | "S3 작업 뭐했어?" |

---

## 📂 문서 경로

```
D:\project-template\chat-api\app\backend\docs\
├── PROJECT_REFERENCE_GUIDE.md          # 프로젝트 구조 ⭐ 업데이트
├── DATABASE_SCHEMA_REFERENCE.md        # DB 스키마 ⭐ 업데이트
├── PROJECT_COMPLETION_REPORT.md        # 작업 내역 ⭐ 업데이트
├── S3_STORAGE_IMPLEMENTATION.md        # S3 상세 가이드 ⭐ NEW
├── S3_STORAGE_INTEGRATION.md           # S3 작업 컨텍스트 ⭐ NEW
├── README_DOCUMENTATION.md             # 이 문서 ⭐ 업데이트
└── ...
```

---

## 💡 활용 팁

### Claude에게 질문할 때

**❌ 비효율적인 방법:**
```
"S3 설정 어떻게 해?"
→ Claude가 프로젝트 전체를 검색 (시간 소요)
```

**✅ 효율적인 방법:**
```
"S3_STORAGE_IMPLEMENTATION.md를 참조해서, 
S3 설정 방법을 알려줘"
→ Claude가 문서만 보고 빠르게 답변
```

### 문서 우선순위

```
1순위: 해당 주제의 전문 문서
   - S3 관련 → S3_STORAGE_*.md
   - DB 관련 → DATABASE_SCHEMA_REFERENCE.md
   
2순위: 프로젝트 전체 참조
   - PROJECT_REFERENCE_GUIDE.md
   
3순위: 최근 작업 확인
   - PROJECT_COMPLETION_REPORT.md
```

### 문서 업데이트

새로운 기능을 추가하면 문서도 함께 업데이트하세요:

```
1. 파일 생성/수정
2. PROJECT_REFERENCE_GUIDE.md 업데이트
   - 파일 목록에 추가
   - API 엔드포인트 추가
   - 최근 변경사항 섹션 업데이트
3. DATABASE_SCHEMA_REFERENCE.md 업데이트 (필요시)
   - 새 테이블 추가
   - 컬럼 변경사항 반영
4. PROJECT_COMPLETION_REPORT.md 업데이트
   - 작업 내역 추가
5. 주제별 전문 문서 생성 (필요시)
   - 예: S3_STORAGE_*.md
```

---

## 🎯 주요 섹션 빠른 링크

### PROJECT_REFERENCE_GUIDE.md에서

- **디렉토리 구조** → 모든 폴더와 파일 위치
- **API 엔드포인트** → 62개+ REST API 목록
- **아키텍처 패턴** → Layered Architecture
- **의존성 주입** → dependencies.py 구조
- **개발 가이드** → 새 기능 추가 순서
- **S3 설정** → .env, simple_settings.py ⭐

### DATABASE_SCHEMA_REFERENCE.md에서

- **PLC_MASTER** → PLC 마스터 정보 + 현재 매핑
- **PROGRAMS** → 프로그램 마스터
- **PGM_MAPPING_HISTORY** → 모든 매핑 변경 이력
- **PGM_TEMPLATE** → 프로그램 구조 템플릿
- **DOCUMENTS** → 파일 메타데이터 (S3/로컬) ⭐
- **테이블 관계도** → 테이블 간 관계 시각화
- **데이터 흐름** → 매핑 시나리오별 흐름

### S3_STORAGE_IMPLEMENTATION.md에서 ⭐

- **작업 개요** → S3 통합 목표 및 방식
- **변경된 파일** → 신규/수정 파일 목록
- **상세 변경 내역** → 코드 레벨 변경사항
- **사용 방법** → 로컬/S3 모드 전환
- **AWS S3 설정** → 버킷 생성, IAM 설정
- **문제 해결** → 일반적인 에러 해결법

---

## ✨ 장점

### 문서 활용 시
- ⚡ **빠른 응답** - 파일 검색 시간 절약
- 🎯 **정확한 답변** - 전체 구조 파악 가능
- 📚 **일관성** - 표준화된 정보
- 🔄 **재사용** - 반복 질문 감소

### 문서 미활용 시
- 🐌 파일 검색으로 시간 소요
- 🤔 부분적인 정보만 제공
- 🔁 같은 질문 반복

---

## 🚀 시작하기

### 1단계: 프로젝트 구조 파악
```
PROJECT_REFERENCE_GUIDE.md 파일을 열어서
프로젝트 전체 구조를 먼저 파악하세요!
```

### 2단계: 필요한 정보 찾기
```
- 파일 위치? → "디렉토리 구조" 섹션
- API? → "API 엔드포인트" 섹션
- DB? → DATABASE_SCHEMA_REFERENCE.md
- S3? → S3_STORAGE_*.md ⭐
```

### 3단계: Claude에게 질문
```
"PROJECT_REFERENCE_GUIDE.md를 참조해서 답변해줘"
또는
"DATABASE_SCHEMA_REFERENCE.md의 PLC_MASTER 테이블을..."
또는
"S3_STORAGE_IMPLEMENTATION.md를 보고 S3 설정 방법을..." ⭐
```

---

## 📝 문서 업데이트 히스토리

| 날짜 | 변경 내용 | 문서 |
|------|-----------|------|
| 2025-10-28 | S3 스토리지 통합 작업 반영 ⭐ | PROJECT_REFERENCE_GUIDE.md |
| 2025-10-28 | DOCUMENTS 테이블 S3 메타데이터 추가 ⭐ | DATABASE_SCHEMA_REFERENCE.md |
| 2025-10-28 | S3 작업 내역 추가 ⭐ | PROJECT_COMPLETION_REPORT.md |
| 2025-10-28 | S3 상세 가이드 생성 ⭐ | S3_STORAGE_IMPLEMENTATION.md |
| 2025-10-28 | S3 작업 컨텍스트 생성 ⭐ | S3_STORAGE_INTEGRATION.md |
| 2025-10-28 | 문서 인덱스 업데이트 ⭐ | README_DOCUMENTATION.md |
| 2025-10-21 | PLC 트리 API 응답 구조 개선 | PROJECT_REFERENCE_GUIDE.md |
| 2025-10-20 | Excel 업로드 에러 처리 개선 | PROJECT_COMPLETION_REPORT.md |
| 2025-10-19 | 템플릿 관리 기능 추가 | PROJECT_REFERENCE_GUIDE.md |
| 2025-10-19 | PLC 트리 조회 API 추가 | DATABASE_SCHEMA_REFERENCE.md |
| 2025-10-17 | 초기 생성 | 전체 |

---

## 🎉 결론

이제 Claude에게 질문할 때 **이 문서들을 먼저 참조**하면:
- ✅ 더 빠른 답변
- ✅ 더 정확한 정보
- ✅ 더 나은 개발 경험

**특히 S3 관련 작업 시:**
- ✅ S3_STORAGE_IMPLEMENTATION.md - 상세 가이드
- ✅ S3_STORAGE_INTEGRATION.md - 빠른 컨텍스트

**Happy Coding with Documentation!** 🚀

---

## 📖 다음 질문 예시

### 프로젝트 구조
```
"PROJECT_REFERENCE_GUIDE.md를 참조해서,
PLC에 프로그램을 매핑하는 전체 플로우를 설명해줘"
```

### 데이터베이스
```
"DATABASE_SCHEMA_REFERENCE.md를 보고,
PGM_MAPPING_HISTORY 테이블의 모든 컬럼을 설명해줘"
```

### ⭐ S3 스토리지
```
"S3_STORAGE_IMPLEMENTATION.md를 참조해서,
S3 스토리지를 어떻게 설정하고 사용하는지 알려줘"

"S3_STORAGE_INTEGRATION.md를 보고,
S3 작업에서 어떤 파일들이 변경됐는지 알려줘"

"S3 업로드 실패 에러가 나는데,
S3_STORAGE_IMPLEMENTATION.md의 문제 해결 섹션을 참조해서 해결 방법 알려줘"
```

### 최근 작업
```
"PROJECT_COMPLETION_REPORT.md를 보고,
최근 추가된 S3 기능에 대해 설명해줘"
```

---

**문서 경로:** `D:\project-template\chat-api\app\backend\docs\`  
**마지막 업데이트:** 2025-10-28  
**작성자:** Claude (Anthropic AI Assistant)
