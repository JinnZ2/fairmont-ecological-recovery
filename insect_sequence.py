"""
insect_sequence.py — Layer 1: Insect Sequencing Engine
Fairmont Ecological Recovery Framework
License: CC0

Gates insect reintroduction phases on substrate state.
Thermodynamic rule: you cannot skip phases.
"""

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Optional


class Phase(IntEnum):
    NONE = 0
    SOIL_BUILDERS = 1
    FOOD_WEB_BRIDGE = 2
    POLLINATOR_RECOVERY = 3
    MATURITY_SIGNAL = 4


class ChemTolerance(Enum):
    HIGH = "HIGH"
    MODERATE_HIGH = "MODERATE-HIGH"
    MODERATE = "MODERATE"
    LOW_MODERATE = "LOW-MODERATE"
    LOW = "LOW"


TOLERANCE_ORDER = {
    ChemTolerance.HIGH: 5,
    ChemTolerance.MODERATE_HIGH: 4,
    ChemTolerance.MODERATE: 3,
    ChemTolerance.LOW_MODERATE: 2,
    ChemTolerance.LOW: 1,
}


@dataclass
class InsectSpec:
    name: str
    family: str
    role: str
    phase: Phase
    chemical_tolerance: ChemTolerance
    habitat_need: str
    success_signal: str
    notes: Optional[str] = None


# ── Species database ───────────────────────────────────────────

SPECIES_DB = [
    # Phase 1: Soil Builders
    InsectSpec("Dung beetles", "Scarabaeidae (Onthophagus, Aphodius)",
              "Soil aeration, nutrient cycling, breaks compaction",
              Phase.SOIL_BUILDERS, ChemTolerance.HIGH,
              "Requires any animal manure source — even small livestock",
              "Visible beetle activity in manure pats within 1 season"),
    InsectSpec("Ground beetles", "Carabidae",
              "Predator cycling, soil surface processing",
              Phase.SOIL_BUILDERS, ChemTolerance.HIGH,
              "Debris cover — boards, leaf litter, mulch strips",
              "Found under debris boards within 1 growing season"),
    InsectSpec("Ants", "Formicidae (Formica, Lasius)",
              "Tunnel networks, seed dispersal, soil structure",
              Phase.SOIL_BUILDERS, ChemTolerance.HIGH,
              "Undisturbed ground patches >2m diameter",
              "Visible mound construction"),
    InsectSpec("Springtails", "Collembola",
              "Decomposition, fungal spore dispersal",
              Phase.SOIL_BUILDERS, ChemTolerance.MODERATE_HIGH,
              "Moisture + organic matter — mulch piles",
              "Visible in leaf litter/mulch when disturbed"),

    # Phase 2: Food Web Bridge
    InsectSpec("Hoverflies", "Syrphidae",
              "Pollination + bird food source",
              Phase.FOOD_WEB_BRIDGE, ChemTolerance.MODERATE,
              "Flowering plants — even weedy ones",
              "Visible hovering at any flowering plant"),
    InsectSpec("Grasshoppers", "Acrididae",
              "Plant cycling, primary bird food",
              Phase.FOOD_WEB_BRIDGE, ChemTolerance.MODERATE_HIGH,
              "Grass >6 inches, undisturbed through summer",
              "Audible in grass on warm days"),
    InsectSpec("Crickets", "Gryllidae",
              "Decomposition, bird/amphibian food",
              Phase.FOOD_WEB_BRIDGE, ChemTolerance.MODERATE,
              "Ground cover, debris, moisture",
              "Evening chorus audible"),
    InsectSpec("Carrion beetles", "Silphidae",
              "Nutrient recycling from animal death",
              Phase.FOOD_WEB_BRIDGE, ChemTolerance.HIGH,
              "Presence of any dead organic matter",
              "Found at any carcass or roadkill"),

    # Phase 3: Pollinator Recovery
    InsectSpec("Sweat bees", "Halictidae",
              "Native pollination — toughest native bee",
              Phase.POLLINATOR_RECOVERY, ChemTolerance.MODERATE,
              "Bare soil patches for ground nesting + flowers within 200m",
              "Multiple individuals on flowers simultaneously"),
    InsectSpec("Mason bees", "Osmia",
              "Early spring pollination",
              Phase.POLLINATOR_RECOVERY, ChemTolerance.LOW_MODERATE,
              "Hollow stems, mud source, early-blooming plants",
              "Occupied nesting tubes/stems"),
    InsectSpec("Bumble bees", "Bombus",
              "Deep flower pollination, vibration specialists",
              Phase.POLLINATOR_RECOVERY, ChemTolerance.LOW,
              "Undisturbed bunch grass for nesting + continuous bloom sequence",
              "Queens visible foraging in spring"),
    InsectSpec("Predatory wasps", "Sphecidae",
              "Pest regulation without chemicals",
              Phase.POLLINATOR_RECOVERY, ChemTolerance.MODERATE,
              "Bare soil or hollow cavities + prey insects present",
              "Nest construction observed"),

    # Phase 4: Maturity Signal (not deployed — they arrive)
    InsectSpec("Monarch butterflies", "Danaus plexippus",
              "Milkweed obligate, long-distance migrator",
              Phase.MATURITY_SIGNAL, ChemTolerance.LOW,
              "Milkweed + corridor connectivity",
              "Presence = plant succession + corridor working"),
    InsectSpec("Fireflies", "Lampyridae",
              "Require clean water, healthy soil, darkness",
              Phase.MATURITY_SIGNAL, ChemTolerance.LOW,
              "Moist soil, low light pollution, prey invertebrates",
              "FIREFLIES = SUBSTRATE IS HEALING"),
    InsectSpec("Dragonflies", "Odonata",
              "Aquatic larval stage, aerial predator",
              Phase.MATURITY_SIGNAL, ChemTolerance.LOW,
              "Clean standing/slow water for larvae",
              "Presence = water system functional for full lifecycle"),
    InsectSpec("Native moths", "Diverse (Noctuidae, Saturniidae, etc.)",
              "Night pollination, bat/bird food",
              Phase.MATURITY_SIGNAL, ChemTolerance.LOW,
              "Diverse plant community, low light pollution",
              "Full nocturnal food web reestablished"),
]


# ── Phase gating engine ────────────────────────────────────────

def get_max_phase(soil_state: str, soil_score: float,
                  years_since_spray: float,
                  water_state: str) -> Phase:
    """
    Determine maximum allowed insect phase based on substrate.
    THERMODYNAMIC GATE: Cannot skip phases.
    """
    if soil_state == "DEAD" and years_since_spray < 2:
        return Phase.NONE
    if soil_state == "DEAD":
        return Phase.SOIL_BUILDERS
    if soil_state == "DEGRADED" and soil_score < 40:
        return Phase.SOIL_BUILDERS
    if soil_state == "DEGRADED":
        return Phase.FOOD_WEB_BRIDGE
    if soil_state == "RECOVERABLE" and water_state in ("FUNCTIONAL", "STRESSED"):
        return Phase.POLLINATOR_RECOVERY
    if soil_state == "RECOVERABLE":
        return Phase.FOOD_WEB_BRIDGE
    if soil_state == "REFUGIA":
        return Phase.POLLINATOR_RECOVERY
    return Phase.SOIL_BUILDERS


def get_viable_species(max_phase: Phase,
                       chemical_floor: ChemTolerance = ChemTolerance.MODERATE
                       ) -> list[InsectSpec]:
    """
    Return species viable for current conditions.
    Filters by phase gate AND chemical tolerance floor.
    """
    floor_val = TOLERANCE_ORDER[chemical_floor]
    viable = []
    for sp in SPECIES_DB:
        if sp.phase <= max_phase and sp.phase != Phase.MATURITY_SIGNAL:
            if TOLERANCE_ORDER[sp.chemical_tolerance] >= floor_val:
                viable.append(sp)
    return viable


def get_phase_species(phase: Phase) -> list[InsectSpec]:
    """Return all species in a specific phase."""
    return [sp for sp in SPECIES_DB if sp.phase == phase]


def get_maturity_signals() -> list[InsectSpec]:
    """Return Phase 4 species — these are observation targets, not deployments."""
    return [sp for sp in SPECIES_DB if sp.phase == Phase.MATURITY_SIGNAL]


# ── Sequencing report ──────────────────────────────────────────

def sequence_report(soil_state: str, soil_score: float,
                    years_since_spray: float,
                    water_state: str) -> str:
    """Full insect sequencing assessment."""
    max_ph = get_max_phase(soil_state, soil_score, years_since_spray, water_state)

    # Determine chemical tolerance floor from spray history
    if years_since_spray < 1:
        chem_floor = ChemTolerance.HIGH
    elif years_since_spray < 3:
        chem_floor = ChemTolerance.MODERATE_HIGH
    elif years_since_spray < 5:
        chem_floor = ChemTolerance.MODERATE
    else:
        chem_floor = ChemTolerance.LOW_MODERATE

    viable = get_viable_species(max_ph, chem_floor)
    maturity = get_maturity_signals()

    lines = [
        f"{'='*60}",
        f"INSECT SEQUENCING REPORT",
        f"{'='*60}",
        f"Substrate:  {soil_state} (score {soil_score:.0f}/100)",
        f"Spray gap:  {years_since_spray} years",
        f"Water:      {water_state}",
        f"",
        f"MAX PHASE ALLOWED: {max_ph.name} (Phase {max_ph.value})",
        f"CHEM TOLERANCE FLOOR: {chem_floor.value}",
        f"",
    ]

    if max_ph == Phase.NONE:
        lines.append(">> NO INSECT DEPLOYMENT VIABLE")
        lines.append(">> Wait for chemical flush. Protect nearest refugia.")
        lines.append(f"{'='*60}")
        return "\n".join(lines)

    lines.append(f"── VIABLE SPECIES ({len(viable)}) ──")
    current_phase = None
    for sp in sorted(viable, key=lambda s: (s.phase, s.name)):
        if sp.phase != current_phase:
            current_phase = sp.phase
            lines.append(f"\n  Phase {sp.phase.value}: {sp.phase.name}")
            lines.append(f"  {'─'*40}")
        lines.append(f"    {sp.name} ({sp.family})")
        lines.append(f"      Role:      {sp.role}")
        lines.append(f"      Tolerance: {sp.chemical_tolerance.value}")
        lines.append(f"      Habitat:   {sp.habitat_need}")
        lines.append(f"      Signal:    {sp.success_signal}")

    lines += [
        f"",
        f"── MATURITY SIGNALS (observe, don't deploy) ──",
    ]
    for sp in maturity:
        lines.append(f"  {sp.name}: {sp.success_signal}")

    lines.append(f"{'='*60}")
    return "\n".join(lines)


if __name__ == "__main__":
    # Fairmont corridor — March 2026
    print(sequence_report(
        soil_state="DEAD",
        soil_score=2.0,
        years_since_spray=0.0,
        water_state="TOXIC",
    ))
