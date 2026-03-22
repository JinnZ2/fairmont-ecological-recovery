"""
water_recovery.py — Layer 3: Water Recovery
Fairmont Ecological Recovery Framework
License: CC0

Stream triage, groundwater recharge timeline,
and recovery signal tracking.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class StreamAssessment:
    name: str
    lat: float
    lon: float
    
    # Observation
    aquatic_insects_visible: bool = False
    frog_chorus: bool = False
    minnows_present: bool = False
    crawfish_present: bool = False
    turtles_nesting: bool = False
    
    # Contamination vectors
    tile_drainage_upstream: bool = True
    feedlot_upstream: bool = False
    buffer_zone_feet: float = 0.0
    
    # Algae / visual
    algae_color: Optional[str] = None  # "green" | "brown" | "clear"
    visible_chemical_sheen: bool = False
    erosion_active: bool = False
    
    # Bank condition
    native_vegetation_on_banks: bool = False
    bank_stability: str = "poor"  # "poor" | "moderate" | "stable"


@dataclass
class WatershedAction:
    action: str
    priority: int  # 1=immediate, 2=short, 3=medium, 4=long
    timeline: str
    impact: str
    prerequisites: list = field(default_factory=list)


# ── Recovery signal database ──────────────────────────────────

RECOVERY_SIGNALS = [
    {
        "signal": "Aquatic insects visible in stream",
        "meaning": "Dissolved oxygen recovering",
        "timeline_years_after_chemical_stop": "1-3",
        "order": 1,
    },
    {
        "signal": "Frog chorus audible",
        "meaning": "Atrazine levels below amphibian threshold",
        "timeline_years_after_chemical_stop": "2-5",
        "order": 2,
    },
    {
        "signal": "Minnows/small fish present",
        "meaning": "Food web reconnecting across trophic levels",
        "timeline_years_after_chemical_stop": "3-7",
        "order": 3,
    },
    {
        "signal": "Crawfish present",
        "meaning": "Substrate quality functional — sediment clean",
        "timeline_years_after_chemical_stop": "5-10",
        "order": 4,
    },
    {
        "signal": "Turtles nesting on banks",
        "meaning": "Full aquatic-terrestrial link established",
        "timeline_years_after_chemical_stop": "10-20",
        "order": 5,
    },
]


# ── Triage engine ─────────────────────────────────────────────

def triage_stream(assessment: StreamAssessment) -> dict:
    """
    Assess stream recovery priority and generate action plan.
    Returns priority tier and ordered action list.
    """
    # Score current state (0-100)
    score = 0
    if assessment.aquatic_insects_visible: score += 20
    if assessment.frog_chorus: score += 20
    if assessment.minnows_present: score += 15
    if assessment.crawfish_present: score += 15
    if assessment.turtles_nesting: score += 10
    if assessment.native_vegetation_on_banks: score += 10
    if assessment.buffer_zone_feet >= 100: score += 10
    elif assessment.buffer_zone_feet >= 30: score += 5

    # Contamination penalty
    if assessment.tile_drainage_upstream: score -= 15
    if assessment.feedlot_upstream: score -= 20
    if assessment.visible_chemical_sheen: score -= 15
    if assessment.erosion_active: score -= 10
    if assessment.algae_color == "green": score -= 10

    score = max(0, min(100, score))

    # Tier classification
    if score >= 60:
        tier = "RECOVERING"
    elif score >= 30:
        tier = "STRESSED"
    elif score >= 10:
        tier = "CONTAMINATED"
    else:
        tier = "CRITICAL"

    # Generate actions
    actions = []

    if assessment.buffer_zone_feet < 30:
        actions.append(WatershedAction(
            "Establish 30-foot minimum native vegetation buffer",
            priority=1, timeline="Year 0-1",
            impact="Reduces sediment/chemical runoff 50-80%",
        ))
    if assessment.buffer_zone_feet < 100:
        actions.append(WatershedAction(
            "Expand buffer to 100 feet with native plantings",
            priority=2, timeline="Year 1-3",
            impact="Full filtration capacity for agricultural runoff",
            prerequisites=["30-foot buffer established"],
        ))
    if assessment.tile_drainage_upstream:
        actions.append(WatershedAction(
            "Map and assess tile drainage discharge points",
            priority=1, timeline="Year 0",
            impact="Identifies primary contamination vectors",
        ))
        actions.append(WatershedAction(
            "Install constructed wetland at tile drainage outlets",
            priority=2, timeline="Year 1-5",
            impact="Processes nitrogen/phosphorus before stream entry",
            prerequisites=["Tile drainage mapped"],
        ))
    if assessment.feedlot_upstream:
        actions.append(WatershedAction(
            "Establish manure management buffer — minimum 200ft from stream",
            priority=1, timeline="Year 0",
            impact="Reduces E. coli and nutrient loading",
        ))
    if assessment.erosion_active:
        actions.append(WatershedAction(
            "Plant willow live stakes on eroding banks",
            priority=1, timeline="Year 0 (dormant season)",
            impact="Bank stabilization within 2 growing seasons",
        ))
    if not assessment.native_vegetation_on_banks:
        actions.append(WatershedAction(
            "Seed native sedges and grasses on stream banks",
            priority=2, timeline="Year 0-2",
            impact="Root network stabilizes banks, filters runoff",
        ))

    # Always include long-term
    actions.append(WatershedAction(
        "Monitor recovery signals annually (see signal checklist)",
        priority=3, timeline="Ongoing",
        impact="Tracks system recovery trajectory",
    ))

    # Current recovery signals achieved
    achieved = []
    next_expected = None
    for sig in RECOVERY_SIGNALS:
        field_map = {
            1: assessment.aquatic_insects_visible,
            2: assessment.frog_chorus,
            3: assessment.minnows_present,
            4: assessment.crawfish_present,
            5: assessment.turtles_nesting,
        }
        if field_map.get(sig["order"], False):
            achieved.append(sig["signal"])
        elif next_expected is None:
            next_expected = sig

    return {
        "stream": assessment.name,
        "score": score,
        "tier": tier,
        "actions": actions,
        "signals_achieved": achieved,
        "next_signal": next_expected,
    }


def groundwater_recharge_timeline(
    years_since_spray: float,
    tile_drainage_removed: bool,
    native_deep_roots_planted: bool,
    wetlands_reconnected: bool,
) -> dict:
    """Estimate groundwater recharge recovery."""
    base = max(0, 3 - years_since_spray)

    factors = {
        "chemical_flush": f"{base:.1f} years remaining",
        "infiltration_recovery": "Active" if native_deep_roots_planted else f"{2.0 + base:.1f} years (need deep-root planting)",
        "tile_drainage": "Removed — natural water table restoring" if tile_drainage_removed else "BLOCKING — subsurface drainage preventing recharge",
        "wetland_filtration": "Connected" if wetlands_reconnected else "Disconnected — reduces filtration capacity 60-80%",
    }

    overall = base
    if not tile_drainage_removed: overall += 5
    if not native_deep_roots_planted: overall += 3
    if not wetlands_reconnected: overall += 5

    factors["estimated_functional_recharge"] = f"{overall:.0f} years"
    return factors


# ── Report ────────────────────────────────────────────────────

def water_report(assessment: StreamAssessment,
                 years_since_spray: float = 0) -> str:
    """Full water recovery report for a stream assessment."""
    result = triage_stream(assessment)
    recharge = groundwater_recharge_timeline(
        years_since_spray=years_since_spray,
        tile_drainage_removed=not assessment.tile_drainage_upstream,
        native_deep_roots_planted=assessment.native_vegetation_on_banks,
        wetlands_reconnected=False,
    )

    lines = [
        f"{'='*60}",
        f"WATER RECOVERY REPORT: {assessment.name}",
        f"{'='*60}",
        f"Location:  {assessment.lat:.4f}, {assessment.lon:.4f}",
        f"Tier:      {result['tier']} (score {result['score']}/100)",
        f"",
        f"── RECOVERY SIGNALS ──",
    ]
    for sig in RECOVERY_SIGNALS:
        status = "✓" if sig["signal"] in result["signals_achieved"] else "○"
        lines.append(f"  {status} {sig['signal']} ({sig['timeline_years_after_chemical_stop']} yr)")

    if result["next_signal"]:
        lines.append(f"\n  NEXT EXPECTED: {result['next_signal']['signal']}")
        lines.append(f"  Timeline: {result['next_signal']['timeline_years_after_chemical_stop']} years after chemical stop")

    lines += [f"", f"── ACTIONS (priority order) ──"]
    for a in sorted(result["actions"], key=lambda x: x.priority):
        lines.append(f"  [{a.priority}] {a.action}")
        lines.append(f"      Timeline: {a.timeline}")
        lines.append(f"      Impact:   {a.impact}")
        if a.prerequisites:
            lines.append(f"      Requires: {', '.join(a.prerequisites)}")

    lines += [f"", f"── GROUNDWATER RECHARGE ──"]
    for k, v in recharge.items():
        lines.append(f"  {k.replace('_', ' ').title():40s} {v}")

    lines.append(f"{'='*60}")
    return "\n".join(lines)


if __name__ == "__main__":
    stream = StreamAssessment(
        name="Unnamed tributary - Hwy 15 crossing",
        lat=43.6386, lon=-94.1035,
        aquatic_insects_visible=False,
        frog_chorus=False,
        minnows_present=False,
        crawfish_present=False,
        turtles_nesting=False,
        tile_drainage_upstream=True,
        feedlot_upstream=False,
        buffer_zone_feet=0,
        algae_color="brown",
        visible_chemical_sheen=False,
        erosion_active=True,
        native_vegetation_on_banks=False,
        bank_stability="poor",
    )
    print(water_report(stream, years_since_spray=0))
