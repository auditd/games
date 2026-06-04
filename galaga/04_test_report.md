# 갤러그(Galaga) HTML5 게임 QA 및 2차 최종 재검증 테스트 보고서

본 보고서는 `/home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html` 최종 패치 소스코드와 기술 설계서 `/home/yjlee/dev/redstar/game/galaga/.workspace/02_design_spec.md`를 교차 검증 및 정적/런타임 분석하여, 1차 보고서에서 지적된 5가지 핵심 버그(베지에 속도 오차, 트랙터 빔 X축 충돌 감지 공식, BGM 사운드 중첩, 포획 아군 사망 시 댕글링 포인터 처리, 레벨클리어/게임오버 연출 타이밍 문제)의 디버깅 및 보정 상태를 2차 재검증한 종합 품질 보증(QA) 최종 결과 보고서입니다.

---

## 1. 종합 평가 요약

| 검수 항목 | 1차 판정 | 최종 판정 (2차) | 주요 발견 요약 및 재검증 결과 |
| :--- | :---: | :---: | :--- |
| **1. 정적 오류 및 실행성** | **PASS** | **PASS** | 문법 에러 및 미정의 변수 참조 없음. 모바일 터치 이벤트 바인딩 정상 작동. |
| **2. 조작 및 조작 바인딩** | **PASS** | **PASS** | 다중 키 제어(Input Masking) 및 터치 반응성 보장. 오디오 컨텍스트 락 완화 정상 연동. |
| **3. 베지에 진입 속도 오차** | **FIX** | **PASS** | 설계서 규격인 $dt_t \approx 0.375 \times \Delta t$ 증가율 반영 완료. 속도 정상화 확인. |
| **4. 트랙터 빔 X축 충돌 감지** | **FIX** | **PASS** | 빔 높이 $150px$ 및 역사다리꼴 충돌 영역 $wHalf$ 수식 수정 완료. 시각적 이펙트와 충돌 판정 완벽 일치. |
| **5. BGM 사운드 중첩 및 오디오** | **FIX** | **PASS** | `activeBGMNodes` 트래킹 및 `stopAllBGM()` 도입으로 BGM 중첩 연주에 따른 불협화음 및 오디오 자원 누수 완전 해결. |
| **6. 포획 아군 사망/댕글링 포인터**| **FIX** | **PASS** | `capturedFighterRef` 파괴 시 실시간 null 갱신 및 댕글링 포인터 차단. 결합용 `DockingFighter` 무한 복제 루프 차단 확인. |
| **7. 상태 흐름 및 연출 타이밍** | **FIX** | **PASS** | `LEVEL_CLEAR` 상태에서도 배경/파티클 갱신 유지. Lives가 0인 경우에도 폭발 연출 1.8초 완수 후 `GAME_OVER`로 정상 전이. |

---

## 2. 5대 핵심 버그 세부 재검증 결과

### 2.1 베지에 편대 진입 속도 오차 보정
* **원인 (1차 지적)**: 진입 속도 증가율이 `0.45 * dt * speedMultiplier`로 적용되어 설계서 규격 대비 약 20% 빠르게 포메이션 대열에 도달하는 오차가 있었습니다.
* **재검증 결과**: **PASS**
  - `03_game_code.html` [L861](file:///home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html#L861)에서 베지에 매개변수 $t$의 증가 공식이 다음과 같이 정상 수정되었습니다:
    ```javascript
    this.t += dt * this.speedMultiplier * 0.375;
    ```
  - 매 프레임당 증가율이 프레임 독립성을 띠면서 설계 스펙($dt_t \approx 0.375 \times \Delta t$)과 정밀하게 일치함을 확인했습니다.

### 2.2 트랙터 빔 X축 충돌 감지 공식 및 범위 정합성
* **원인 (1차 지적)**: 빔 높이가 `160`으로 상이했으며, 충돌 범위 반폭 $wHalf$ 계산 시 `48 * progress`가 사용되어 최대 $64px$(총 128px)의 이격을 형성, 비주얼 빔 이펙트 영역 밖에서도 플레이어가 납치되는 물리 판정 버그가 존재했습니다.
* **재검증 결과**: **PASS**
  - `03_game_code.html` [L1013](file:///home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html#L1013) 및 [L1470](file:///home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html#L1470)에서 빔의 기준 높이가 `150`으로 정밀 조정되었습니다.
  - [L1472-L1476](file:///home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html#L1472-L1476)에서 역사다리꼴 영역 캡처 X축 반폭 공식이 설계 사양과 일치하도록 다음과 같이 수정되었습니다:
    ```javascript
    const beamHeight = 150;
    if (py >= yb && py <= yb + beamHeight) {
        const progress = (py - yb) / beamHeight;
        const wHalf = 16 + (32 * progress); // (16px에서 48px까지 선형 확장)
        if (Math.abs(px - xb) <= wHalf) {
            // ... 포획 트리거
        }
    }
    ```
  - 이로써 비주얼 렌더링에 사용되는 역사다리꼴 영역 스케일과 물리 충돌 감지 경계선이 좌우 오차 없이 정합함을 검증하였습니다.

### 2.3 BGM 사운드 중첩 및 오디오 자원 누수 방지
* **원인 (1차 지적)**: 멜로디 시퀀스 작동 중 새로운 멜로디를 재생할 때 이전 오실레이터 노드를 정지 및 청소하지 않아 사운드가 겹치고 브라우저 자원 낭비가 발생했습니다.
* **재검증 결과**: **PASS**
  - `AudioManager` 내에 `activeBGMNodes` 트래킹 배열과 `stopAllBGM()` 메서드가 추가되었습니다 ([L356](file:///home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html#L356), [L476-L487](file:///home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html#L476)).
  - 새로운 BGM 연주 시, [L493](file:///home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html#L493)에서 `this.stopAllBGM()`을 먼저 실행하도록 하였고, [L536](file:///home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html#L536)에서 신규 오실레이터 노드를 `this.activeBGMNodes`에 적절히 푸시하여 추적할 수 있도록 보완되었습니다.
  - 이로 인해 신규 스테이지 진입, 보너스 라이프 획득, 게임 오버 시 BGM 노드가 겹치지 않고 오디오 자원이 깔끔하게 수거됩니다.

### 2.4 포획 아군 사망 시 댕글링 포인터 및 자가 복제 버그 차단
* **원인 (1차 지적)**: 포획된 전투기가 플레이어 공격에 맞아 사망할 때, 보스의 `capturedFighterRef` 참조가 해제되지 않아 가비지 컬렉션(GC) 누수가 생겼고, 보스가 파괴되는 시점에 소멸한 아군 객체를 바탕으로 `DockingFighter`를 다시 소환하는 자가 복제(복사 버그) 결함이 발생했습니다.
* **재검증 결과**: **PASS**
  - 보스 기체의 `update` 프레임 핸들러 내 [L950-L958](file:///home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html#L950-L958) 영역에서 참조 대상 아군의 사망 여부를 즉각 감지하여 관계성을 릴리즈하도록 수정되었습니다:
    ```javascript
    if (this.hasCapturedFighter && this.capturedFighterRef) {
        if (this.capturedFighterRef.isDead) {
            this.hasCapturedFighter = false;
            this.capturedFighterRef = null;
        } else {
            this.capturedFighterRef.x = this.x;
            this.capturedFighterRef.y = this.y - 24;
        }
    }
    ```
  - [L1641-L1650](file:///home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html#L1641-L1650)에서 보스가 사망하는 시점에도 `enemy.hasCapturedFighter && enemy.capturedFighterRef`가 온전히 살아있을 때에만 아군이 릴리즈 및 `DockingFighter`로 변형되도록 물리 로직을 정교화함으로써, 좀비 객체 누수와 복제 취약점을 동시에 완벽 방어하고 있습니다.

### 2.5 레벨 클리어/게임 오버 연출 타이밍 제어 및 동결 개선
* **원인 (1차 지적)**:
  1. `LEVEL_CLEAR` 진입 시 `update(dt)`의 즉시 반환(return) 처리에 의해 3.5초 동안 배경 우주 및 이펙트 파티클이 동결되는 부자연스러운 현상이 일어났습니다.
  2. 플레이어의 라이프가 0인 상태에서 격격당했을 때, 피격 연출이 끝나기 전에 화면 전체가 바로 `GAME_OVER`로 전이되는 맥락 단절 현상이 확인되었습니다.
* **재검증 결과**: **PASS**
  - **화면 동결 개선**: `update(dt)` 초반부에 별무리(`starfield.update`)와 파티클(`particles.update`) 연산 물리 루프를 리턴 분기 상단([L1381-L1393](file:///home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html#L1381-L1393))으로 하향 및 재조정하여, LEVEL_CLEAR 상태에서도 파편 효과와 배경 스크롤이 매끄럽게 흐릅니다.
  - **게임 오버 연출 타이밍 보정**: 플레이어가 파괴되는 순간 즉시 게임 오버로 분기되던 기존 로직을 삭제하고, [L1419-L1431](file:///home/yjlee/dev/redstar/game/galaga/.workspace/03_game_code.html#L1419-L1431) 리스폰 딜레이 타이머 내에 해당 논리를 포함시켰습니다. 이에 따라 1.8초 동안 플레이어 폭발 연출을 충분히 노출한 뒤, 잔기가 0이면 비로소 게임 오버 화면으로 매끄럽게 장면이 전환됩니다.

---

## 3. 종합 최종 품질 결론

- **2차 재검증 결과**: **전원 PASS (통과)**
- **결론 요약**: 개발사에 의해 5대 핵심 버그(베지에 곡선 증가율, 역사다리꼴 빔 좌표계, 오디오 노드 중첩, GC 댕글링 포인터, FSM 타임아웃)가 설계서에 지정된 아케이드 정합 사양에 맞춰 모두 완벽하게 수정되었음을 확인하였습니다. 
- 본 소스코드는 런타임 상의 메모리 누수와 물리 바운딩 박스 이격을 배제하고 60FPS 및 주사율 보정 환경에서 안정적으로 플레이 가능하므로 QA 프로세스를 **최종 통과** 처리합니다.
