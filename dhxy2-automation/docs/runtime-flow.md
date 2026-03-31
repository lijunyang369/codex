# ?????2?????????

## ????

???????

1. ?????
2. ???????
3. ??????????

---

## 1. ?????

```mermaid
flowchart LR
    subgraph Entry[???]
        A["scripts/run_battle_app.py"]
    end

    subgraph App[?????? app]
        B["bootstrap.build_app_from_configs()"]
        C["BattleAutomationApp.run_once()"]
        D["DefaultObservationProvider.observe()"]
    end

    subgraph Platform[??? platform]
        E["WindowFinder"]
        F["WindowSession"]
        G["PyWin32WindowGateway"]
    end

    subgraph Perception[??? perception]
        H["TemplateCatalog"]
        I["OpenCvTemplateMatcher"]
        J["OCRReader"]
        K["ObservationBuilder"]
    end

    subgraph Domain[??? domain]
        L["BattleObservation"]
        M["ActionPlan / AutomationAction"]
        N["AutomationContext"]
    end

    subgraph StateMachine[???? state_machine]
        O["BattleStateMachine"]
    end

    subgraph Policy[??? policy]
        P["FixedRulePolicy"]
    end

    subgraph Executor[??? executor]
        Q["ActionExecutor"]
        R["InputGateway"]
    end

    subgraph Runtime[????? runtime]
        S["RuntimeSession"]
        T["Artifacts / Logs"]
    end

    A --> B --> E --> F --> C
    E --> G
    C --> D --> F
    D --> I
    D --> J
    I --> H
    D --> K --> L
    C --> O
    O --> N
    C --> P --> M
    C --> Q --> R
    C --> S --> T
```

---

## 2. ???????

```mermaid
sequenceDiagram
    participant Entry as ????
    participant Bootstrap as bootstrap
    participant Finder as WindowFinder
    participant Session as WindowSession
    participant Provider as ObservationProvider
    participant Matcher as TemplateMatcher
    participant OCR as OCRReader
    participant Builder as ObservationBuilder
    participant Runtime as RuntimeSession
    participant SM as StateMachine
    participant Policy as Policy
    participant Executor as Executor
    participant Input as InputGateway

    Entry->>Bootstrap: build_app_from_configs(paths)
    Bootstrap->>Bootstrap: ?? env/account/scenario ??
    Bootstrap->>Finder: ????
    Finder->>Session: ?? WindowSession(handle)
    Bootstrap-->>Entry: ?? BattleAutomationApp

    Entry->>Runtime: ???????? RuntimeSession
    Entry->>Bootstrap: app.run_once()

    Bootstrap->>Provider: observe(window_session)
    Provider->>Session: snapshot()
    Provider->>Session: capture_client()
    Provider->>Matcher: match(frame, region_name, rect)
    Provider->>OCR: read_lines(frame, region_name, rect)
    Provider->>Builder: build(frame, window_info, matches, ocr)
    Builder-->>Provider: BattleObservation
    Provider-->>Bootstrap: BattleObservation

    Bootstrap->>Runtime: record_observation(observation)
    Bootstrap->>SM: tick(observation, context)
    SM-->>Bootstrap: TransitionResult
    Bootstrap->>Runtime: record_transition(transition)

    Bootstrap->>Policy: build_plan(observation, context)
    Policy-->>Bootstrap: ActionPlan

    alt ????
        Bootstrap-->>Entry: AppTickResult(???)
    else ????
        Bootstrap->>SM: begin_action(plan, context)
        SM-->>Bootstrap: TransitionResult
        Bootstrap->>Runtime: record_transition(begin)

        loop ?? AutomationAction
            Bootstrap->>Runtime: record_action(action, reason)
            Bootstrap->>Executor: execute(action, window_session, input_gateway)
            Executor->>Session: focus()
            Executor->>Input: click / key / wait
            Executor-->>Bootstrap: ExecutionResult
        end

        Bootstrap->>SM: complete_action(context, accepted_by_ui=True)
        SM-->>Bootstrap: TransitionResult
        Bootstrap->>Runtime: record_transition(finish)
        Bootstrap-->>Entry: AppTickResult
    end
```

---

## 2.5 ??????

??????????????????

???

- ???????? `window_focused`
- ???????????????????
- ?????????????????

?????

- `configs/env/local.json` ? `require_foreground=true`

???????

- ??????????????????????
- ????????? `run_once()` ????????

---

## 3. run_once ????

```mermaid
flowchart TD
    A["run_once ??"] --> B["observe(window)"]
    B --> C["record_observation"]
    C --> D["state_machine.tick"]
    D --> E["record_transition"]
    E --> F["policy.build_plan"]
    F --> G{"plan ?????"}

    G -- ? --> H["?? AppTickResult
???????"]

    G -- ? --> I["state_machine.begin_action"]
    I --> J["record_transition"]
    J --> K["?? plan.actions"]
    K --> L["record_action"]
    L --> M["executor.execute"]
    M --> N["state_machine.complete_action"]
    N --> O["record_transition"]
    O --> P["?? AppTickResult"]
```

---

## 4. ???????

```mermaid
flowchart LR
    A["resources/templates/*.png"] --> B["catalog.json"]
    B --> C["TemplateCatalog"]
    C --> D["OpenCvTemplateMatcher"]
    D --> E["MatchResult"]
    E --> F["ObservationBuilder"]
    F --> G["BattleObservation"]
    G --> H["BattleStateMachine"]
```

????

- ????? `resources`
- ??????? `perception`
- ???????? `BattleObservation`
- ????? `BattleObservation` ??

---

## 5. ?????

?????

- `D:\Codex\dhxy2-automation\scriptsun_battle_app.py`

?????????

- `D:\Codex\dhxy2-automation\srcpp\service.py`
- `BattleAutomationApp.run_once()`

?????

```powershell
$env:PYTHONPATH='D:\Codex\dhxy2-automation'
D:\Codex\dhxy2-automation\.venv\Scripts\python.exe D:\Codex\dhxy2-automation\scriptsun_battle_app.py
```

---

## 6. ????????????

????????

- `D:\Codex\dhxy2-automation\scriptsun_battle_app.py`
- `D:\Codex\dhxy2-automation\srcppootstrap.py`

????????????????

- `D:\Codex\dhxy2-automation\srcpp\observation_provider.py`
- `D:\Codex\dhxy2-automation\src\perception\services.py`
- `D:\Codex\dhxy2-automation\src\perception\observation.py`
- `D:\Codex\dhxy2-automation\src\state_machine\machine.py`

??????????????

- `D:\Codex\dhxy2-automation\src\policy\planner.py`
- `D:\Codex\dhxy2-automation\src\executor	ranslator.py`
- `D:\Codex\dhxy2-automation\src\executor\executor.py`

---

## 7. ??????????

```mermaid
flowchart TD
    A["????? dry-run"] --> B["????????"]
    B --> C["???????"]
    C --> D["??? OCR"]
    D --> E["????????"]
    E --> F["?????"]
```
