---
name: galaga-orchestrator
description: "고전 아케이드 슈팅 게임(갤러그/스페이스 인베이더 등)을 개발하고 배포하기 위해 요건분석/설계/코딩/테스트/배포 서브에이전트 팀을 조율할 때 사용한다. 후속 작업: 게임 플레이 수정, 기능 추가, 난이도 밸런싱 수정, 버그 디버깅, 재실행, 부분 다시 실행, 업데이트, 보완 요청 시에도 반드시 이 스킬을 호출할 것."
---

# Galaga Game Development Orchestrator

고전 아케이드 슈팅 게임(갤러그/스페이스 인베이더 스타일) 개발 프로젝트를 총괄 조율하고, 서브에이전트 팀의 순차 파이프라인 및 피드백 디버깅 루프를 제어하는 통합 오케스트레이터 스킬.

## 실행 모드: 순차 서브에이전트 (루프형 피드백 파이프라인)

## 작업 공간 경로 및 자산 구조
모든 작업물은 `/home/yjlee/dev/redstar/game/galaga` 디렉토리에 저장된다.
*   임시 작업 공간: `/home/yjlee/dev/redstar/game/galaga/.workspace/`
*   최종 산출물 경로: `/home/yjlee/dev/redstar/game/galaga/` (코드는 `index.html`, 배포용 서버 스크립트는 `start_server.py`)

## 서브에이전트 팀 구성 및 스킬 매핑

| 에이전트 TypeName | 역할 | 관련 스킬 | 출력물 경로 |
| :--- | :--- | :--- | :--- |
| `game-analyst` | 기획 및 요구사항 분석 | `game-analyst-skill` | `/home/yjlee/dev/redstar/game/galaga/.workspace/01_requirements.md` |
| `game-designer` | 객체 구조, FSM, 2D 물리 설계 | `game-designer-skill` | `/home/yjlee/dev/redstar/game/galaga/.workspace/02_design_spec.md` |
| `game-developer` | Canvas/Vanilla JS 게임 코딩 | `game-developer-skill` | `/home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html` |
| `game-tester` | 자바스크립트 버그 및 물리 QA | `game-tester-skill` | `/home/yjlee/dev/redstar/game/galaga/.workspace/04_test_report.md` |
| `game-deployer` | 패키징, PWA 및 호스팅 서버 구축 | `game-deployer-skill` | `/home/yjlee/dev/redstar/game/galaga/` (배포 루트) |

---

## 워크플로우 (Pipeline & Feedback Loop)

### Phase 0: 컨텍스트 확인 (후속 및 부분 재실행 제어)
기존 작업 상태를 분석하여 실행 모드를 동적으로 결정한다.
1. `/home/yjlee/dev/redstar/game/galaga/.workspace/` 디렉토리와 내부 산출물 파일 유무를 분석한다.
2. 실행 상태에 따라 흐름 분기:
   - **디렉토리 미존재**: 초기 실행. Phase 1(준비)부터 전체 파이프라인 순서대로 실행한다.
   - **기존 결과물 존재 + 사용자의 부분 피드백**: 부분 재실행. 이전 산출물 경로를 인자로 넘겨 해당 서브에이전트만 재호출(예: 개발자에게 디버깅 위임)하고, 변경된 파일만 갱신한 뒤 테스트 및 배포 단계를 밟는다.
   - **기존 결과물 존재 + 완전히 새로운 게임 컨셉 요청**: 신규 실행. 기존 디렉토리를 `/home/yjlee/dev/redstar/game/galaga/.workspace_backup_{YYYYMMDD_HHMMSS}/`로 안전하게 백업 및 이동한 후 Phase 1을 시작한다.

### Phase 1: 준비 및 기획 분석
1. 사용자가 제시한 아케이드 게임 플레이 요건을 분석한다.
2. 작업 디렉토리 하위에 `/home/yjlee/dev/redstar/game/galaga/.workspace/` 폴더를 새로 개설하고, 원본 인풋 요구사항을 `00_input/` 하위에 저장한다.
3. `invoke_subagent` 도구를 호출하여 요건 분석가인 `game-analyst`를 기동한다.
   - **Prompt**: "사용자 요구사항을 토대로 고전 슈팅 게임 플레이 사양 및 점수 테이블, 레벨 구조를 작성하고 `/home/yjlee/dev/redstar/game/galaga/.workspace/01_requirements.md` 파일에 기록하세요."

### Phase 2: 기술 아키텍처 설계
1. `invoke_subagent` 도구를 호출하여 게임 디자이너인 `game-designer`를 기동한다.
   - **Prompt**: "요구사항 정의서 `/home/yjlee/dev/redstar/game/galaga/.workspace/01_requirements.md`를 로드하여 클래스 구조, 게임 상태 FSM, 2D AABB 충돌 수학식 및 베지에 비행 궤적 공식을 설계하고 `/home/yjlee/dev/redstar/game/galaga/.workspace/02_design_spec.md` 파일에 기록하세요."

### Phase 3: 게임 코딩 및 구현
1. `invoke_subagent` 도구를 호출하여 게임 개발자인 `game-developer`를 기동한다.
   - **Prompt**: "기술 설계서 `/home/yjlee/dev/redstar/game/galaga/.workspace/02_design_spec.md`를 바탕으로, HTML5 Canvas와 Web Audio API 사운드 합성 코드가 포함되어 단독 구동이 가능한 단일 자바스크립트 게임 코드를 작성하고 `/home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html` 파일에 기록하세요."

### Phase 4: 품질 보증 및 디버깅 루프 (Incremental QA Loop)
1. `invoke_subagent` 도구를 호출하여 게임 QA 테스터인 `game-tester`를 기동한다.
   - **Prompt**: "구현된 소스코드 `/home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html`와 설계서 `/home/yjlee/dev/redstar/game/galaga/.workspace/02_design_spec.md`를 교차 검증하여, 문법 오류, 조작 반응성, 충돌 바운더리를 테스트하고 PASS/FIX/REDO 평가 결과서를 `/home/yjlee/dev/redstar/game/galaga/.workspace/04_test_report.md`에 작성하세요."
2. **피드백 제어 루프**:
   - `/home/yjlee/dev/redstar/game/galaga/.workspace/04_test_report.md` 파일 내용을 판독한다.
   - **REDO 또는 FIX 판정**이 존재하는 경우:
     - 개발자 `game-developer`를 재소집(invoke_subagent)한다.
     - **Prompt**: "테스트 결과 보고서 `/home/yjlee/dev/redstar/game/galaga/.workspace/04_test_report.md`에 지적된 자바스크립트 버그 및 정합성 실패 내용을 핀포인트로 디버깅하여 `/home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html`를 수정 및 업데이트하세요."
     - 수정이 완료되면 다시 1단계(테스터 호출)로 복귀한다. (이 루프는 최대 2회 반복하며, 계속 버그 발생 시 메인 오케스트레이터가 개입한다.)
   - **전원 PASS 판정**: Phase 5로 전이한다.

### Phase 5: 번들링 및 정적 호스팅 배포
1. `invoke_subagent` 도구를 호출하여 배포 엔지니어인 `game-deployer`를 기동한다.
   - **Prompt**: "최종 검증 통과한 `/home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html` 코드를 가져와, PWA 설정, 반응형 모바일 뷰포트 처리, 파이썬3 포트 스위칭 웹 서버 자동 기동 스크립트(`start_server.py`) 및 사용 가이드 `README.md`를 포함한 배포 디렉토리 `/home/yjlee/dev/redstar/game/galaga/`를 구축하세요."
2. 최종 빌드 결과물이 위치한 배포 경로를 확인하고 최종 사용자에게 완료 브리핑을 보고한다.

---

## 에러 핸들링 프로토콜

| 발생 상황 | 처리 및 폴백 전략 |
| :--- | :--- |
| 서브에이전트 구동 에러/실패 | 1회 즉각 재호출(Retry)을 시도한다. 지속 실패 시 에러 로그를 기록하고 파이프라인을 일시 정지하여 사용자에게 수동 검토를 요청한다. |
| 루프 한도 초과 (2회 이상 불합격) | 테스터와 개발자 간의 핑퐁 루프가 2회를 초과하여 실패할 경우, 메인 에이전트(오케스트레이터)가 직접 디버깅 도구를 사용해 코드를 열고 수동으로 디버깅을 마친 뒤 PASS 처리한다. |
| 산출물 파일 누락 | 이전 Phase의 아티팩트 파일이 발견되지 않으면, 해당 단계를 복원하기 위해 직전 단계 에이전트를 재구동한다. |

---

## 테스트 시나리오

### 1. 정상 작동 시나리오 (Happy Path)
- **입력**: 사용자가 "스페이스 인베이더 스타일의 아케이드 클래식 갤러그 게임 구현" 요청.
- **최종 결과**: `/home/yjlee/dev/redstar/game/galaga/index.html` 및 `start_server.py`가 정상 구동 가능하도록 빌드 완료.

### 2. 예외 및 오류 시나리오 (Error Path)
- **입력**: 개발자가 코딩 중 미사일 충돌 박스 처리의 문법 오타 발생.
- **예상 흐름**: 테스터가 버그 감지 후 REDO 판정 → 개발자가 수정 후 재테스트 통과 → 배포 완료.