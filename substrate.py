"""
substrate.py — Layer 0: Substrate Assessment
Fairmont Ecological Recovery Framework
License: CC0

Scores soil state, water contamination, refugia potential,
and chemical persistence for a given assessment site.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import date


class SoilState(Enum):
    DEAD = "DEAD"
    DEGRADED = "DEGRADED"
    RECOVERABLE = "RECOVERABLE"
    REFUGIA = "REFUGIA"


class WaterState(Enum):
    TOXIC = "TOXIC"
    CONTAMINATED = "CONTAMINATED"
    STRESSED = "STRESSED"
    FUNCTIONAL = "FUNCTIONAL"


@dataclass
class FieldAssessment:
    """No-lab field assessment from Layer 0 protocol."""
    site_name: str
    lat: float
    lon: float
    date_assessed: str

    # Dig test
    earthworms_present: bool = False
    fungal_threads_visible: bool = False
    soil_smell: str = "flat"  # "earthy" | "chemical" | "flat"
    dig_depth_inches: float = 6.0

    # Water test
    nearest_stream_name: Optional[str] = None
    aquatic_life_visible: bool = False
    algae_color: Optional[str] = None  # "green" | "brown" | "clear"
    water_smell: Optional[str] = None

    # Insect scan (15 min, >55F)
    flying_insects_count: int = 0
    ground_insects_count: int = 0
    ant_mounds_visible: bool = False
    scan_temp_f: float = 55.0

    # Bird listen (10 min, dawn)
    bird_calls_heard: int = 0
    bird_species_estimated: int = 0

    # Plant diversity (10x10 ft square)
    plant_species_count: int = 0

    # Chemical history
    years_since_last_spray: float = 0.0
    known_chemicals: list = field(default_factory=list)
    tile_drainage_present: bool = False

    # Refugia indicators
    never_sprayed: bool = False
    years_fallow: float = 0.0
    adjacent_to_refugia: bool = False
    refugia_type: Optional[str] = None  # "ditch" | "fenceline" | "abandoned" | "wetland" | "railroad"


# ── Chemical persistence database ──────────────────────────────

CHEMICAL_PROFILES = {
    "neonicotinoid": {
        "compounds": ["imidacloprid", "clothianidin", "thiamethoxam"],
        "half_life_days_min": 200,
        "half_life_days_max": 1000,
        "primary_damage": "insect nervous system, soil microbes",
        "flush_signal": "ground beetle return",
        "flush_years_estimate": 3.0,
    },
    "glyphosate": {
        "compounds": ["glyphosate", "roundup"],
        "half_life_days_min": 30,
        "half_life_days_max": 180,
        "primary_damage": "microbial community, nutrient chelation",
        "flush_signal": "mycorrhizal fungi visible on roots",
        "flush_years_estimate": 1.0,
    },
    "atrazine": {
        "compounds": ["atrazine"],
        "half_life_days_min": 60,
        "half_life_days_max": 150,
        "primary_damage": "amphibians, aquatic life",
        "flush_signal": "frog chorus returns",
        "flush_years_estimate": 1.5,
    },
    "chlorpyrifos": {
        "compounds": ["chlorpyrifos"],
        "half_life_days_min": 60,
        "half_life_days_max": 120,
        "primary_damage": "broad-spectrum insect kill",
        "flush_signal": "fly populations rebound",
        "flush_years_estimate": 1.0,
    },
}


# ── Scoring engine ─────────────────────────────────────────────

def score_soil(assessment: FieldAssessment) -> tuple[SoilState, float, dict]:
    """
    Returns (SoilState, score 0-100, detail_dict).
    Score is composite: microbial + structure + chemical + biodiversity.
    """
    scores = {}

    # Microbial (0-25)
    microbial = 0.0
    if assessment.earthworms_present:
        microbial += 10
    if assessment.fungal_threads_visible:
        microbial += 10
    if assessment.soil_smell == "earthy":
        microbial += 5
    elif assessment.soil_smell == "chemical":
        microbial -= 5
    scores["microbial"] = max(0, min(25, microbial))

    # Structure / insect activity (0-25)
    structure = 0.0
    structure += min(10, assessment.ground_insects_count * 2)
    if assessment.ant_mounds_visible:
        structure += 8
    structure += min(7, assessment.flying_insects_count)
    scores["structure"] = max(0, min(25, structure))

    # Chemical load (0-25, inverted — lower chemical = higher score)
    chemical = 25.0
    if assessment.years_since_last_spray < 1:
        chemical -= 20
    elif assessment.years_since_last_spray < 3:
        chemical -= 12
    elif assessment.years_since_last_spray < 5:
        chemical -= 5
    if assessment.tile_drainage_present:
        chemical -= 5
    for chem in assessment.known_chemicals:
        for profile in CHEMICAL_PROFILES.values():
            if chem.lower() in [c.lower() for c in profile["compounds"]]:
                persistence_penalty = min(5, profile["half_life_days_max"] / 200)
                chemical -= persistence_penalty
    scores["chemical"] = max(0, min(25, chemical))

    # Biodiversity (0-25)
    biodiversity = 0.0
    biodiversity += min(10, assessment.plant_species_count * 0.7)
    biodiversity += min(8, assessment.bird_species_estimated * 2)
    if assessment.aquatic_life_visible:
        biodiversity += 7
    scores["biodiversity"] = max(0, min(25, biodiversity))

    total = sum(scores.values())

    # Classify
    if assessment.never_sprayed or assessment.years_fallow >= 5:
        state = SoilState.REFUGIA
    elif total >= 60:
        state = SoilState.RECOVERABLE
    elif total >= 30:
        state = SoilState.DEGRADED
    else:
        state = SoilState.DEAD

    return state, total, scores


def score_water(assessment: FieldAssessment) -> tuple[WaterState, dict]:
    """Score water condition from field observations."""
    detail = {
        "stream": assessment.nearest_stream_name,
        "life_visible": assessment.aquatic_life_visible,
        "algae": assessment.algae_color,
    }

    if assessment.nearest_stream_name is None:
        return WaterState.STRESSED, {**detail, "note": "no stream assessed"}

    if assessment.aquatic_life_visible and assessment.algae_color == "clear":
        return WaterState.FUNCTIONAL, detail
    elif assessment.aquatic_life_visible:
        return WaterState.STRESSED, detail
    elif assessment.algae_color == "green":
        return WaterState.CONTAMINATED, detail
    else:
        return WaterState.TOXIC, detail


def estimate_recovery_timeline(assessment: FieldAssessment) -> dict:
    """Estimate years to each recovery milestone."""
    base_years = assessment.years_since_last_spray

    # Chemical flush time
    max_flush = 0
    for chem in assessment.known_chemicals:
        for profile in CHEMICAL_PROFILES.values():
            if chem.lower() in [c.lower() for c in profile["compounds"]]:
                remaining = max(0, profile["flush_years_estimate"] - base_years)
                max_flush = max(max_flush, remaining)

    if not assessment.known_chemicals:
        max_flush = max(0, 3.0 - base_years)  # assume standard ag chemical load

    timeline = {
        "chemical_flush_years": round(max_flush, 1),
        "ground_beetle_return": round(max_flush + 0.5, 1),
        "pollinator_viable": round(max_flush + 3.0, 1),
        "bird_food_web": round(max_flush + 5.0, 1),
        "full_ecosystem_signal": round(max_flush + 10.0, 1),
        "canopy_establishment": round(max_flush + 25.0, 1),
    }
    return timeline


def identify_refugia_potential(assessment: FieldAssessment) -> dict:
    """Assess whether site can serve as refugia anchor."""
    potential = {
        "is_refugia": assessment.never_sprayed or assessment.years_fallow >= 5,
        "adjacent_to_refugia": assessment.adjacent_to_refugia,
        "refugia_type": assessment.refugia_type,
        "priority": "NONE",
    }

    if potential["is_refugia"]:
        potential["priority"] = "PROTECT"
    elif assessment.adjacent_to_refugia and assessment.years_since_last_spray >= 2:
        potential["priority"] = "EXPAND"
    elif assessment.years_since_last_spray >= 1:
        potential["priority"] = "CANDIDATE"
    else:
        potential["priority"] = "LONG_TERM"

    return potential


# ── Report output ──────────────────────────────────────────────

def substrate_report(assessment: FieldAssessment) -> str:
    """Single-call full substrate assessment report."""
    soil_state, soil_score, soil_detail = score_soil(assessment)
    water_state, water_detail = score_water(assessment)
    timeline = estimate_recovery_timeline(assessment)
    refugia = identify_refugia_potential(assessment)

    lines = [
        f"{'='*60}",
        f"SUBSTRATE ASSESSMENT: {assessment.site_name}",
        f"{'='*60}",
        f"Location:  {assessment.lat:.4f}, {assessment.lon:.4f}",
        f"Date:      {assessment.date_assessed}",
        f"",
        f"── SOIL STATE: {soil_state.value} (score: {soil_score:.0f}/100) ──",
        f"  Microbial:     {soil_detail['microbial']:.0f}/25",
        f"  Structure:     {soil_detail['structure']:.0f}/25",
        f"  Chemical:      {soil_detail['chemical']:.0f}/25",
        f"  Biodiversity:  {soil_detail['biodiversity']:.0f}/25",
        f"",
        f"── WATER STATE: {water_state.value} ──",
        f"  Stream:        {water_detail.get('stream', 'N/A')}",
        f"  Life visible:  {water_detail.get('life_visible', 'N/A')}",
        f"  Algae:         {water_detail.get('algae', 'N/A')}",
        f"",
        f"── RECOVERY TIMELINE ──",
    ]
    for k, v in timeline.items():
        lines.append(f"  {k.replace('_', ' ').title():30s} {v} years")

    lines += [
        f"",
        f"── REFUGIA POTENTIAL ──",
        f"  Status:   {refugia['priority']}",
        f"  Is refugia:       {refugia['is_refugia']}",
        f"  Adjacent refugia: {refugia['adjacent_to_refugia']}",
        f"  Type:             {refugia['refugia_type'] or 'N/A'}",
        f"{'='*60}",
    ]
    return "\n".join(lines)


# ── Example usage ──────────────────────────────────────────────

if __name__ == "__main__":
    # March 21, 2026 — Fairmont corridor field observation
    site = FieldAssessment(
        site_name="Fairmont Corridor - Mile 85 (Hwy 15)",
        lat=43.6386,
        lon=-94.1035,
        date_assessed="2026-03-21",
        earthworms_present=False,
        fungal_threads_visible=False,
        soil_smell="flat",
        nearest_stream_name="unnamed tributary",
        aquatic_life_visible=False,
        algae_color="brown",
        flying_insects_count=0,
        ground_insects_count=0,
        ant_mounds_visible=False,
        scan_temp_f=78.0,
        bird_calls_heard=0,
        bird_species_estimated=0,
        plant_species_count=1,
        years_since_last_spray=0.0,
        known_chemicals=["imidacloprid", "glyphosate", "atrazine"],
        tile_drainage_present=True,
        never_sprayed=False,
        years_fallow=0.0,
        adjacent_to_refugia=False,
    )
    print(substrate_report(site))
