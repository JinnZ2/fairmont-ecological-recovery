"""
corridor_report.py — Single-Command Corridor Assessment
Fairmont Ecological Recovery Framework
License: CC0

Runs all layers and outputs integrated corridor report.
Usage: python corridor_report.py
"""

from substrate import FieldAssessment, substrate_report, score_soil, score_water
from insect_sequence import sequence_report, get_max_phase
from plant_succession import succession_report
from water_recovery import StreamAssessment, water_report
from knowledge_bridge import (
    CommunityInventory, KnowledgeHolder, SkillCategory,
    knowledge_report,
)


def full_corridor_report(
    sites: list[FieldAssessment],
    streams: list[StreamAssessment],
    communities: list[CommunityInventory],
) -> str:
    """
    Single-command full corridor assessment.
    Integrates all five layers into one output.
    """
    lines = [
        f"{'#'*60}",
        f"# FAIRMONT ECOLOGICAL RECOVERY — CORRIDOR REPORT",
        f"# Generated from field observations",
        f"{'#'*60}",
        f"",
    ]

    # ── Layer 0: Substrate ──
    lines.append(f"\n{'='*60}")
    lines.append(f"LAYER 0: SUBSTRATE ASSESSMENT — {len(sites)} site(s)")
    lines.append(f"{'='*60}\n")

    soil_states = []
    for site in sites:
        lines.append(substrate_report(site))
        lines.append("")
        state, score, _ = score_soil(site)
        soil_states.append((site.site_name, state.value, score))

    # Corridor summary
    avg_score = sum(s[2] for s in soil_states) / len(soil_states) if soil_states else 0
    lines.append(f"── CORRIDOR SUBSTRATE SUMMARY ──")
    lines.append(f"  Sites assessed:  {len(soil_states)}")
    lines.append(f"  Average score:   {avg_score:.0f}/100")
    for name, state, score in soil_states:
        lines.append(f"  {name[:40]:40s} {state:12s} ({score:.0f})")

    # ── Layer 1: Insect Sequencing ──
    lines.append(f"\n{'='*60}")
    lines.append(f"LAYER 1: INSECT SEQUENCING")
    lines.append(f"{'='*60}\n")

    for site in sites:
        state, score, _ = score_soil(site)
        water_state, _ = score_water(site)
        lines.append(sequence_report(
            state.value, score, site.years_since_last_spray, water_state.value
        ))
        lines.append("")

    # ── Layer 2: Plant Succession ──
    lines.append(f"\n{'='*60}")
    lines.append(f"LAYER 2: PLANT SUCCESSION")
    lines.append(f"{'='*60}\n")

    for site in sites:
        state, score, _ = score_soil(site)
        max_phase = get_max_phase(
            state.value, score, site.years_since_last_spray,
            score_water(site)[0].value
        )
        lines.append(f"Site: {site.site_name}")
        lines.append(succession_report(state.value, max_phase))
        lines.append("")

    # ── Layer 3: Water Recovery ──
    lines.append(f"\n{'='*60}")
    lines.append(f"LAYER 3: WATER RECOVERY — {len(streams)} stream(s)")
    lines.append(f"{'='*60}\n")

    for stream in streams:
        lines.append(water_report(stream))
        lines.append("")

    # ── Layer 4: Knowledge Bridge ──
    lines.append(f"\n{'='*60}")
    lines.append(f"LAYER 4: KNOWLEDGE BRIDGE — {len(communities)} community(ies)")
    lines.append(f"{'='*60}\n")

    for comm in communities:
        lines.append(knowledge_report(comm))
        lines.append("")

    # ── Integrated Assessment ──
    lines.append(f"\n{'#'*60}")
    lines.append(f"# INTEGRATED CORRIDOR ASSESSMENT")
    lines.append(f"{'#'*60}")

    dead_count = sum(1 for s in soil_states if s[1] == "DEAD")
    degraded_count = sum(1 for s in soil_states if s[1] == "DEGRADED")
    recoverable_count = sum(1 for s in soil_states if s[1] == "RECOVERABLE")
    refugia_count = sum(1 for s in soil_states if s[1] == "REFUGIA")

    total_holders = sum(len(c.holders) for c in communities)
    total_gaps = sum(len(c.get_critical_gaps()) for c in communities)
    avg_doc = sum(c.documentation_score() for c in communities) / len(communities) if communities else 0

    lines += [
        f"",
        f"  Substrate:    {dead_count} DEAD / {degraded_count} DEGRADED / {recoverable_count} RECOVERABLE / {refugia_count} REFUGIA",
        f"  Avg score:    {avg_score:.0f}/100",
        f"  Streams:      {len(streams)} assessed",
        f"  Communities:  {len(communities)} inventoried",
        f"  Holders:      {total_holders} identified",
        f"  Skill gaps:   {total_gaps} critical",
        f"  Doc score:    {avg_doc:.0f}%",
        f"",
    ]

    if avg_score < 20:
        lines.append("  >> CORRIDOR STATUS: CRITICAL")
        lines.append("  >> Immediate action: protect all refugia, stop chemical input where possible,")
        lines.append("  >> document knowledge holders, begin Layer 0 assessment at every accessible site.")
    elif avg_score < 50:
        lines.append("  >> CORRIDOR STATUS: DEGRADED — recovery possible with sustained intervention")
    else:
        lines.append("  >> CORRIDOR STATUS: RECOVERING — maintain trajectory")

    lines += [
        f"",
        f"  Framework: github.com/JinnZ2/fairmont-ecological-recovery",
        f"  License:   CC0 — no rights reserved",
        f"  Related:   github.com/JinnZ2/urban-resilience-sim",
        f"{'#'*60}",
    ]

    return "\n".join(lines)


if __name__ == "__main__":
    # ── March 21, 2026 — Fairmont Corridor ──

    site1 = FieldAssessment(
        site_name="Fairmont Corridor - Mile 85 (Hwy 15)",
        lat=43.6386, lon=-94.1035,
        date_assessed="2026-03-21",
        earthworms_present=False, fungal_threads_visible=False,
        soil_smell="flat",
        nearest_stream_name="unnamed tributary",
        aquatic_life_visible=False, algae_color="brown",
        flying_insects_count=0, ground_insects_count=0,
        ant_mounds_visible=False, scan_temp_f=78.0,
        bird_calls_heard=0, bird_species_estimated=0,
        plant_species_count=1,
        years_since_last_spray=0.0,
        known_chemicals=["imidacloprid", "glyphosate", "atrazine"],
        tile_drainage_present=True,
        never_sprayed=False, years_fallow=0.0,
        adjacent_to_refugia=False,
    )

    stream1 = StreamAssessment(
        name="Unnamed tributary - Hwy 15 crossing",
        lat=43.6386, lon=-94.1035,
        aquatic_insects_visible=False,
        frog_chorus=False, minnows_present=False,
        crawfish_present=False, turtles_nesting=False,
        tile_drainage_upstream=True, feedlot_upstream=False,
        buffer_zone_feet=0, algae_color="brown",
        visible_chemical_sheen=False, erosion_active=True,
        native_vegetation_on_banks=False, bank_stability="poor",
    )

    fairmont = CommunityInventory("Fairmont, MN", population_est=10000)
    # Placeholder — real inventory requires ground survey
    fairmont.add_holder(KnowledgeHolder(
        "PLACEHOLDER", "Fairmont",
        [SkillCategory.FOOD_PRODUCTION],
        ["Ground survey needed to identify real holders"],
        knowledge_documented=False,
        notes="This inventory requires in-person community assessment",
    ))

    print(full_corridor_report(
        sites=[site1],
        streams=[stream1],
        communities=[fairmont],
    ))
