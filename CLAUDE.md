# CLAUDE.md

## Project Overview

Fairmont Ecological Recovery Framework — a thermodynamically-grounded decision support system for ecological recovery in the southern Minnesota corridor (Fairmont/Martin County, USDA zones 4a-4b). Designed to be executable at the hyper-local level when industrial agriculture systems fail.

All data is based on field observations from March 2026 documenting ecological collapse across 170+ miles of corridor.

## Repository Structure

```
substrate.py          — Layer 0: Substrate (soil/water) assessment & scoring
insect_sequence.py    — Layer 1: Insect species sequencing engine
plant_succession.py   — Layer 2: Plant succession matching
water_recovery.py     — Layer 3: Water/stream recovery triage
knowledge_bridge.py   — Layer 4: Community knowledge & collapse protocol
corridor_report.py    — Integrated multi-layer corridor reporting
README.md             — Full framework documentation
```

## Tech Stack

- **Language**: Python 3 (standard library only — no external dependencies)
- **Key modules used**: `dataclasses`, `enum`, `typing`, `datetime`
- **No build system**: No package.json, requirements.txt, setup.py, or pyproject.toml
- **No web framework or frontend**
- **No database**: All data embedded as module-level constants

## Running the Code

Each module has a `if __name__ == "__main__"` block with example usage:

```bash
python substrate.py         # Layer 0 — soil/water field assessment
python insect_sequence.py   # Layer 1 — insect sequencing
python water_recovery.py    # Layer 3 — stream triage
python knowledge_bridge.py  # Layer 4 — community inventory
python corridor_report.py   # Full integrated corridor report
```

The primary entry point is `corridor_report.py` which imports and orchestrates all layers.

## Architecture & Key Patterns

### Layered Design with Hard Dependencies

The framework enforces thermodynamic ordering — you cannot skip layers:

- **Layer 0 (Substrate)** must be assessed first → determines soil/water state
- **Layer 1 (Insects)** is gated by substrate state → only viable species are recommended
- **Layer 2 (Plants)** depends on both soil state and insect phase
- **Layer 3 (Water)** operates semi-independently for stream triage
- **Layer 4 (Knowledge)** tracks community capacity and collapse response

### Data Models

All models use `@dataclass`. Key types:

| Type | Module | Purpose |
|------|--------|---------|
| `FieldAssessment` | substrate.py | No-lab soil/water observation |
| `InsectSpec` | insect_sequence.py | Species with phase/tolerance/habitat |
| `PlantSpec` | plant_succession.py | Plants with succession phase/soil tolerance |
| `StreamAssessment` | water_recovery.py | Stream observation tracking |
| `KnowledgeHolder` | knowledge_bridge.py | Community skill inventory |
| `CommunityResource` | knowledge_bridge.py | Land/water/seed/tool resources |
| `CollapseAction` | knowledge_bridge.py | Emergency response protocol |

### Enums

| Enum | Values | Used For |
|------|--------|----------|
| `SoilState` | DEAD, DEGRADED, RECOVERABLE, REFUGIA | Soil classification |
| `WaterState` | TOXIC, CONTAMINATED, STRESSED, FUNCTIONAL | Water classification |
| `Phase` (IntEnum) | 0-4 | Insect recovery phases |
| `ChemTolerance` | HIGH → LOW | Chemical tolerance ordering |
| `SuccessionPhase` (IntEnum) | 0-3 | Plant succession stages |
| `SkillCategory` | 8 categories | Community skill types |
| `Urgency` | IMMEDIATE → LONG_TERM | Action priority |

### Scoring System

Composite soil score (0-100) from four subscores:
- Microbial activity (0-25)
- Soil structure (0-25)
- Chemical persistence (0-25)
- Biodiversity indicators (0-25)

Score thresholds determine `SoilState` classification.

### Consistent Function Patterns

- `get_viable_*()` — filter species/plants by current conditions
- `*_report()` — generate formatted text reports per layer
- `full_corridor_report()` — integrated multi-layer output

### Embedded Databases

Module-level constants serve as lookup tables:
- `CHEMICAL_PROFILES` — compound classes with half-lives
- `SPECIES_DB` — 16 insect species across 4 phases
- `PLANT_DB` — 20+ plant species across 4 succession phases
- `RECOVERY_SIGNALS` — ordered recovery milestones
- `TRADITIONAL_PRACTICES` — indigenous land management practices

## Code Conventions

- **Naming**: `snake_case` for functions/variables, `UPPER_CASE` for constants and enum members
- **Type hints**: Used throughout all function signatures and dataclass fields
- **Docstrings**: Module-level docstrings with purpose and license
- **Section dividers**: ASCII art comments (`# ── label ──────────────────`)
- **String formatting**: f-strings exclusively
- **Indentation**: 4 spaces (Python standard)
- **No formal linter/formatter configured** — code follows consistent manual style

## Testing

- No formal test framework (no pytest/unittest)
- Each module's `__main__` block serves as a runnable example/smoke test
- To verify the system works: `python corridor_report.py` should produce a formatted multi-layer report

## Extending the Framework

- **Add species**: Append `InsectSpec` entries to `SPECIES_DB` in `insect_sequence.py`
- **Add plants**: Append `PlantSpec` entries to `PLANT_DB` in `plant_succession.py`
- **Add chemicals**: Add entries to `CHEMICAL_PROFILES` in `substrate.py`
- **Add skills**: Extend `SkillCategory` enum and create `KnowledgeHolder` entries in `knowledge_bridge.py`
- **New layers**: Follow the existing pattern — dataclass models, enum states, filtering functions, report generator

## Environment Assumptions

- Climate: Continental (southern Minnesota)
- Hardiness zones: USDA 4a-4b
- Soil type: Clay-loam baseline
- No network connectivity required (fully offline)
- No environment variables or config files

## License

CC0 1.0 Universal — no rights reserved.
