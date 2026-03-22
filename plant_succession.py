"""
plant_succession.py — Layer 2: Plant Succession
Fairmont Ecological Recovery Framework
License: CC0

Matches plant species to substrate state and insect phase.
Hard dependency: plants follow insects, not the other way around.
"""

from dataclasses import dataclass
from enum import IntEnum
from typing import Optional


class SuccessionPhase(IntEnum):
    PIONEER = 0
    EARLY = 1
    MID = 2
    LATE = 3


@dataclass
class PlantSpec:
    name: str
    scientific: str
    phase: SuccessionPhase
    role: str
    insect_dependency: str
    hardiness_zones: str
    soil_tolerance: str
    years_to_establish: float
    human_use: Optional[str] = None


PLANT_DB = [
    # Pioneer (Year 0-3): Hold the Soil
    PlantSpec("Big bluestem", "Andropogon gerardii", SuccessionPhase.PIONEER,
              "Deep roots (6-10 ft), soil carbon builder",
              "Phase 1 ground beetles shelter in base",
              "3-9", "Clay-loam, sand, poor", 2.0,
              "Biomass, erosion control"),
    PlantSpec("Switchgrass", "Panicum virgatum", SuccessionPhase.PIONEER,
              "Deep roots, biomass accumulator, bunching grass",
              "Phase 2 grasshopper habitat, Phase 3 bumble bee nesting",
              "3-9", "Wide tolerance", 2.0,
              "Biomass fuel, erosion control"),
    PlantSpec("Indian grass", "Sorghastrum nutans", SuccessionPhase.PIONEER,
              "Warm-season carbon builder",
              "Phase 2 cricket/grasshopper habitat",
              "4-9", "Clay-loam preferred", 2.0),
    PlantSpec("White clover", "Trifolium repens", SuccessionPhase.PIONEER,
              "Nitrogen fixation, ground cover, early pollinator food",
              "Phase 2 hoverflies, Phase 3 all bees",
              "3-10", "Tolerates poor soil, self-seeds", 0.5,
              "Nitrogen fixer, cover crop, edible flowers"),
    PlantSpec("Annual rye", "Secale cereale", SuccessionPhase.PIONEER,
              "Fast erosion control, breaks compaction",
              "Minimal — structural role",
              "3-11", "Germinates in almost anything", 0.3,
              "Cover crop, allelopathic weed suppression"),
    PlantSpec("Native sunflower", "Helianthus spp.", SuccessionPhase.PIONEER,
              "Deep taproot, bird food, insect habitat",
              "Phase 2 hoverflies, Phase 3 native bees",
              "3-9", "Aggressive colonizer of disturbed ground", 0.5,
              "Bird feed, human food (seeds), oil"),

    # Early Succession (Year 2-6): Feed the Insects
    PlantSpec("Common milkweed", "Asclepias syriaca", SuccessionPhase.EARLY,
              "Monarch obligate, native bee magnet",
              "Phase 3 pollinators, Phase 4 monarch signal",
              "3-9", "Moderate — needs some soil recovery", 2.0,
              "Fiber, traditional medicine"),
    PlantSpec("Prairie coneflower", "Ratibida pinnata", SuccessionPhase.EARLY,
              "Long bloom season, bird seed source",
              "Phase 2 flies and grasshoppers",
              "3-9", "Tolerates clay", 1.5),
    PlantSpec("Wild bergamot", "Monarda fistulosa", SuccessionPhase.EARLY,
              "Native bee specialist flower",
              "Phase 3 bumble bees specifically",
              "3-9", "Dry to medium soil", 1.0,
              "Tea, traditional medicine, antimicrobial"),
    PlantSpec("Goldenrod", "Solidago spp.", SuccessionPhase.EARLY,
              "Late season critical pollinator resource",
              "Phase 2-3 all pollinators, predatory wasps",
              "3-9", "Wide tolerance, aggressive colonizer", 1.0,
              "Traditional medicine, dye"),
    PlantSpec("Black-eyed Susan", "Rudbeckia hirta", SuccessionPhase.EARLY,
              "Long bloom, bird seed, gap filler",
              "Phase 2 hoverflies, Phase 3 bees",
              "3-9", "Wide tolerance", 0.5),

    # Mid Succession (Year 5-15): Build Structure
    PlantSpec("Willow", "Salix spp.", SuccessionPhase.MID,
              "Fast-growing, stream bank stabilizer",
              "Hosts 400+ insect species",
              "2-9", "Wet soils, stream banks", 3.0,
              "Basketry, aspirin precursor, live stakes for bank repair"),
    PlantSpec("Elderberry", "Sambucus canadensis", SuccessionPhase.MID,
              "Bird food, pollinator resource, structure",
              "Phase 2-3 multiple species",
              "3-9", "Moist, rich soil preferred", 3.0,
              "Berry harvest (cooked), wine, syrup, medicine"),
    PlantSpec("American hazelnut", "Corylus americana", SuccessionPhase.MID,
              "Nut crop, windbreak, soil holder, thicket former",
              "Hosts diverse moth larvae",
              "4-9", "Adaptable", 4.0,
              "Nut crop — calorie-dense human food"),
    PlantSpec("Dogwood", "Cornus spp.", SuccessionPhase.MID,
              "Bird habitat, stream bank, erosion control",
              "Berry crop for migrating birds",
              "3-8", "Moist soils", 3.0,
              "Bird return signal species"),

    # Late Succession (Year 15-50+): Full Cycle
    PlantSpec("Bur oak", "Quercus macrocarpa", SuccessionPhase.LATE,
              "Canopy anchor — 200+ dependent insect species",
              "Full Phase 4 maturity ecosystem",
              "3-8", "Deep roots, drought tolerant once established", 20.0,
              "Acorn crop, timber, 500+ year lifespan"),
    PlantSpec("American plum", "Prunus americana", SuccessionPhase.LATE,
              "Early bloom pollinator, bird food, thicket",
              "Phase 3-4 early spring bee food",
              "3-8", "Adaptable, thicket-forming", 5.0,
              "Fruit harvest, preserves, wildlife corridor"),
    PlantSpec("Basswood", "Tilia americana", SuccessionPhase.LATE,
              "Massive pollinator resource, shade canopy",
              "Sustains large bee populations",
              "3-8", "Rich, moist soil preferred", 15.0,
              "Honey tree, cordage fiber, carving wood"),
]


# ── Matching engine ────────────────────────────────────────────

def get_viable_plants(soil_state: str, insect_phase: int,
                      years_available: float = 0) -> list[PlantSpec]:
    """
    Return plants viable for current conditions.
    Gate: soil state limits succession phase, insect phase must support.
    """
    # Soil gates max succession phase
    soil_gate = {
        "DEAD": SuccessionPhase.PIONEER,
        "DEGRADED": SuccessionPhase.EARLY,
        "RECOVERABLE": SuccessionPhase.MID,
        "REFUGIA": SuccessionPhase.LATE,
    }
    max_succession = soil_gate.get(soil_state, SuccessionPhase.PIONEER)

    # Insect phase gates (need insects before dependent plants)
    if insect_phase < 2:
        max_succession = min(max_succession, SuccessionPhase.PIONEER)
    elif insect_phase < 3:
        max_succession = min(max_succession, SuccessionPhase.EARLY)

    return [p for p in PLANT_DB if p.phase <= max_succession]


def get_food_plants(phase: Optional[SuccessionPhase] = None) -> list[PlantSpec]:
    """Return plants with human food/medicine use."""
    plants = PLANT_DB if phase is None else [p for p in PLANT_DB if p.phase == phase]
    return [p for p in plants if p.human_use]


def succession_report(soil_state: str, insect_phase: int) -> str:
    """Full plant succession report gated on substrate."""
    viable = get_viable_plants(soil_state, insect_phase)
    food = get_food_plants()

    lines = [
        f"{'='*60}",
        f"PLANT SUCCESSION REPORT",
        f"{'='*60}",
        f"Soil state:    {soil_state}",
        f"Insect phase:  {insect_phase}",
        f"",
    ]

    current_phase = None
    for p in sorted(viable, key=lambda x: (x.phase, x.name)):
        if p.phase != current_phase:
            current_phase = p.phase
            phase_years = {0: "0-3", 1: "2-6", 2: "5-15", 3: "15-50+"}
            lines.append(f"\n── {current_phase.name} (Year {phase_years[current_phase.value]}) ──")
        lines.append(f"  {p.name} ({p.scientific})")
        lines.append(f"    Role:     {p.role}")
        lines.append(f"    Insects:  {p.insect_dependency}")
        lines.append(f"    Soil:     {p.soil_tolerance}")
        if p.human_use:
            lines.append(f"    HUMAN USE: {p.human_use}")

    lines += [
        f"",
        f"── FOOD/MEDICINE PLANTS (all phases) ──",
    ]
    for p in food:
        lines.append(f"  {p.name}: {p.human_use}")

    lines.append(f"{'='*60}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(succession_report("DEAD", 0))
