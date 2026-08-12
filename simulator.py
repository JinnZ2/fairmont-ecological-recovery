#!/usr/bin/env python3
"""
simulator.py — Interactive Corridor Recovery Simulator
Fairmont Ecological Recovery Framework
License: CC0

Zero dependencies. Walks users through field assessment,
shows recovery state, and runs what-if scenarios.

Usage: python simulator.py
"""

import sys
from substrate import (
    FieldAssessment, SoilState, WaterState,
    score_soil, score_water, estimate_recovery_timeline,
    identify_refugia_potential, CHEMICAL_PROFILES,
)
from insect_sequence import (
    Phase, ChemTolerance, get_max_phase, get_viable_species,
    get_maturity_signals, SPECIES_DB,
)
from plant_succession import (
    SuccessionPhase, get_viable_plants, get_food_plants, PLANT_DB,
)
from water_recovery import StreamAssessment, triage_stream, RECOVERY_SIGNALS
from knowledge_bridge import (
    CommunityInventory, KnowledgeHolder, SkillCategory,
    generate_collapse_protocol,
)


# ── Terminal helpers ──────────────────────────────────────────

def clear():
    print("\033[2J\033[H", end="")


def banner(text, char="=", width=60):
    print(f"\n{char * width}")
    print(f"  {text}")
    print(f"{char * width}")


def prompt(text, default=None):
    if default is not None:
        text = f"{text} [{default}]"
    val = input(f"  {text}: ").strip()
    if not val and default is not None:
        return str(default)
    return val


def prompt_float(text, default=0.0):
    val = prompt(text, default)
    try:
        return float(val)
    except ValueError:
        print(f"    (using default: {default})")
        return default


def prompt_int(text, default=0):
    val = prompt(text, default)
    try:
        return int(val)
    except ValueError:
        print(f"    (using default: {default})")
        return default


def prompt_bool(text, default=False):
    default_str = "Y/n" if default else "y/N"
    val = prompt(f"{text} ({default_str})", None)
    if not val:
        return default
    return val.lower().startswith("y")


def prompt_choice(text, options, default=0):
    print(f"\n  {text}")
    for i, opt in enumerate(options):
        marker = " >> " if i == default else "    "
        print(f"{marker}{i + 1}. {opt}")
    val = prompt("Choice", default + 1)
    try:
        idx = int(val) - 1
        if 0 <= idx < len(options):
            return idx
    except ValueError:
        pass
    return default


def pause():
    input("\n  Press Enter to continue...")


def print_bar(label, value, max_val, width=30):
    filled = int((value / max_val) * width) if max_val > 0 else 0
    bar = "█" * filled + "░" * (width - filled)
    print(f"  {label:20s} [{bar}] {value:.0f}/{max_val:.0f}")


def print_phase_diagram(current_phase, max_phase):
    """Visual phase gating diagram."""
    phases = [
        (Phase.NONE, "No Deploy"),
        (Phase.SOIL_BUILDERS, "Soil Builders"),
        (Phase.FOOD_WEB_BRIDGE, "Food Web Bridge"),
        (Phase.POLLINATOR_RECOVERY, "Pollinator Recovery"),
        (Phase.MATURITY_SIGNAL, "Maturity Signal"),
    ]
    print("\n  PHASE GATING:")
    for phase, name in phases:
        if phase == Phase.NONE and max_phase == Phase.NONE:
            marker = " >> YOU ARE HERE"
            icon = "⚠"
        elif phase <= max_phase and phase != Phase.NONE:
            marker = " ✓ UNLOCKED" if phase <= current_phase else " ○ AVAILABLE"
            icon = "●"
        else:
            marker = " ✗ LOCKED"
            icon = "○"
        print(f"    {icon} Phase {phase.value}: {name:25s}{marker}")


def print_timeline_visual(timeline):
    """Visual recovery timeline."""
    print("\n  RECOVERY TIMELINE:")
    max_years = max(timeline.values())
    for label, years in timeline.items():
        name = label.replace("_", " ").title()
        bar_len = int((years / max_years) * 30) if max_years > 0 else 0
        bar = "▓" * bar_len
        print(f"    {name:30s} {bar} {years:.1f} yr")


# ── Assessment collector ──────────────────────────────────────

def collect_field_assessment():
    """Interactive field assessment data collection."""
    banner("FIELD ASSESSMENT — Layer 0 Protocol")
    print("  Answer based on what you observe. No lab needed.\n")

    site_name = prompt("Site name/description", "My Site")
    lat = prompt_float("Latitude", 43.64)
    lon = prompt_float("Longitude", -94.10)

    banner("DIG TEST (6 inches down)", char="-")
    earthworms = prompt_bool("Earthworms present?")
    fungal = prompt_bool("Fungal threads visible?")
    smell_idx = prompt_choice("Soil smell?", ["Earthy (healthy)", "Flat (no smell)", "Chemical"], 1)
    smell = ["earthy", "flat", "chemical"][smell_idx]

    banner("WATER (nearest stream/pond)", char="-")
    has_stream = prompt_bool("Is there a stream or water body nearby?")
    stream_name = None
    aquatic_life = False
    algae = None
    if has_stream:
        stream_name = prompt("Stream/water name", "unnamed")
        aquatic_life = prompt_bool("Any aquatic life visible? (bugs, minnows, frogs)")
        algae_idx = prompt_choice("Water/algae appearance?",
                                  ["Clear", "Green (algae bloom)", "Brown (sediment)"], 2)
        algae = ["clear", "green", "brown"][algae_idx]

    banner("INSECT SCAN (15 min observation, >55°F)", char="-")
    scan_temp = prompt_float("Current temp (°F)", 60)
    flying = prompt_int("Flying insects counted", 0)
    ground = prompt_int("Ground insects counted", 0)
    ants = prompt_bool("Ant mounds visible?")

    banner("BIRD LISTEN (10 min, ideally dawn)", char="-")
    bird_calls = prompt_int("Bird calls heard", 0)
    bird_species = prompt_int("Estimated bird species", 0)

    banner("PLANT COUNT (10x10 ft square)", char="-")
    plant_count = prompt_int("Different plant species in square", 1)

    banner("CHEMICAL HISTORY", char="-")
    years_spray = prompt_float("Years since last chemical spray", 0)
    tile = prompt_bool("Tile drainage present?")

    known_chems = []
    print("\n  Known chemicals applied (enter each, blank to finish):")
    print(f"    Common: {', '.join(CHEMICAL_PROFILES.keys())}")
    while True:
        chem = prompt("  Chemical (blank=done)", "")
        if not chem:
            break
        known_chems.append(chem)

    banner("REFUGIA INDICATORS", char="-")
    never_sprayed = prompt_bool("Has this land NEVER been sprayed?")
    years_fallow = prompt_float("Years fallow/unused", 0)
    adjacent = prompt_bool("Adjacent to any refugia? (ditch, fenceline, abandoned lot)")
    refugia_type = None
    if adjacent:
        rt_idx = prompt_choice("Refugia type?",
                               ["Ditch/waterway", "Fenceline", "Abandoned field", "Wetland", "Railroad ROW"], 0)
        refugia_type = ["ditch", "fenceline", "abandoned", "wetland", "railroad"][rt_idx]

    return FieldAssessment(
        site_name=site_name, lat=lat, lon=lon,
        date_assessed="field",
        earthworms_present=earthworms, fungal_threads_visible=fungal,
        soil_smell=smell,
        nearest_stream_name=stream_name,
        aquatic_life_visible=aquatic_life, algae_color=algae,
        flying_insects_count=flying, ground_insects_count=ground,
        ant_mounds_visible=ants, scan_temp_f=scan_temp,
        bird_calls_heard=bird_calls, bird_species_estimated=bird_species,
        plant_species_count=plant_count,
        years_since_last_spray=years_spray,
        known_chemicals=known_chems,
        tile_drainage_present=tile,
        never_sprayed=never_sprayed, years_fallow=years_fallow,
        adjacent_to_refugia=adjacent, refugia_type=refugia_type,
    )


# ── Results display ───────────────────────────────────────────

def show_results(assessment):
    """Display full assessment results with visuals."""
    soil_state, soil_score, soil_detail = score_soil(assessment)
    water_state, water_detail = score_water(assessment)
    timeline = estimate_recovery_timeline(assessment)
    refugia = identify_refugia_potential(assessment)

    banner(f"RESULTS: {assessment.site_name}")

    # Soil score bars
    print(f"\n  SOIL STATE: {soil_state.value} (score: {soil_score:.0f}/100)\n")
    print_bar("Microbial", soil_detail["microbial"], 25)
    print_bar("Structure", soil_detail["structure"], 25)
    print_bar("Chemical", soil_detail["chemical"], 25)
    print_bar("Biodiversity", soil_detail["biodiversity"], 25)
    print(f"\n  {'─' * 56}")
    print_bar("TOTAL", soil_score, 100)

    # Water state
    print(f"\n  WATER STATE: {water_state.value}")

    # Phase gating
    max_phase = get_max_phase(
        soil_state.value, soil_score,
        assessment.years_since_last_spray,
        water_state.value,
    )
    print_phase_diagram(Phase.NONE, max_phase)

    # Recovery timeline
    print_timeline_visual(timeline)

    # Refugia
    print(f"\n  REFUGIA: {refugia['priority']}")
    if refugia["is_refugia"]:
        print("    This site IS refugia — PROTECT IT")
    elif refugia["adjacent_to_refugia"]:
        print("    Adjacent to refugia — expansion candidate")

    # Viable species
    if max_phase >= Phase.SOIL_BUILDERS:
        if assessment.years_since_last_spray < 1:
            chem_floor = ChemTolerance.HIGH
        elif assessment.years_since_last_spray < 3:
            chem_floor = ChemTolerance.MODERATE_HIGH
        elif assessment.years_since_last_spray < 5:
            chem_floor = ChemTolerance.MODERATE
        else:
            chem_floor = ChemTolerance.LOW_MODERATE

        viable_insects = get_viable_species(max_phase, chem_floor)
        viable_plants = get_viable_plants(
            soil_state.value, max_phase,
        )
        food_plants = [p for p in viable_plants if p.human_use]

        print(f"\n  VIABLE INSECTS: {len(viable_insects)}")
        for sp in viable_insects:
            print(f"    ● {sp.name} — {sp.role}")

        print(f"\n  VIABLE PLANTS: {len(viable_plants)}")
        for p in viable_plants:
            use = f" ★ {p.human_use}" if p.human_use else ""
            print(f"    ● {p.name} ({p.scientific}){use}")

        if food_plants:
            print(f"\n  FOOD/MEDICINE PLANTS YOU CAN START NOW: {len(food_plants)}")
            for p in food_plants:
                print(f"    ★ {p.name}: {p.human_use}")
    else:
        print("\n  ⚠ NO SPECIES DEPLOYMENT VIABLE YET")
        print("    Wait for chemical flush. Protect nearest refugia.")
        print(f"    Estimated wait: {timeline['chemical_flush_years']:.1f} years")

    return soil_state, soil_score, water_state, max_phase, timeline


# ── What-if scenarios ─────────────────────────────────────────

def run_whatif(assessment):
    """Run what-if scenarios on current assessment."""
    banner("WHAT-IF SCENARIO ENGINE")
    print("  See how changes affect your recovery timeline.\n")

    scenarios = [
        "What if chemicals stopped TODAY?",
        "What if we find refugia nearby?",
        "What if we add compost/manure?",
        "What if we wait 3 years?",
        "What if we wait 5 years?",
        "Custom: change spray years",
        "Back to main menu",
    ]

    while True:
        choice = prompt_choice("Select scenario:", scenarios)

        if choice == 6:
            break

        # Clone assessment with modifications
        import copy
        modified = copy.copy(assessment)

        if choice == 0:  # Chemicals stopped
            modified.years_since_last_spray = 0.5
            modified.known_chemicals = []
            label = "CHEMICALS STOPPED (6 months from now)"

        elif choice == 1:  # Refugia found
            modified.adjacent_to_refugia = True
            modified.refugia_type = "ditch"
            label = "REFUGIA FOUND NEARBY"

        elif choice == 2:  # Compost added
            modified.earthworms_present = True
            modified.fungal_threads_visible = True
            modified.soil_smell = "earthy"
            modified.ground_insects_count = max(2, modified.ground_insects_count)
            label = "COMPOST/MANURE AMENDMENT APPLIED"

        elif choice == 3:  # Wait 3 years
            modified.years_since_last_spray = assessment.years_since_last_spray + 3
            modified.years_fallow = assessment.years_fallow + 3
            modified.plant_species_count = max(3, assessment.plant_species_count + 2)
            label = "3 YEARS LATER (no chemicals)"

        elif choice == 4:  # Wait 5 years
            modified.years_since_last_spray = assessment.years_since_last_spray + 5
            modified.years_fallow = assessment.years_fallow + 5
            modified.plant_species_count = max(5, assessment.plant_species_count + 4)
            modified.ground_insects_count = max(2, assessment.ground_insects_count + 1)
            label = "5 YEARS LATER (no chemicals)"

        elif choice == 5:  # Custom
            years = prompt_float("Years since last spray", assessment.years_since_last_spray)
            modified.years_since_last_spray = years
            label = f"CUSTOM: {years} years since spray"

        # Show comparison
        orig_state, orig_score, _ = score_soil(assessment)
        new_state, new_score, new_detail = score_soil(modified)
        orig_timeline = estimate_recovery_timeline(assessment)
        new_timeline = estimate_recovery_timeline(modified)
        orig_phase = get_max_phase(
            orig_state.value, orig_score,
            assessment.years_since_last_spray,
            score_water(assessment)[0].value,
        )
        new_phase = get_max_phase(
            new_state.value, new_score,
            modified.years_since_last_spray,
            score_water(modified)[0].value,
        )

        banner(f"SCENARIO: {label}", char="-")
        print(f"\n  {'':30s} {'CURRENT':>12s}  →  {'SCENARIO':>12s}")
        print(f"  {'─' * 60}")
        print(f"  {'Soil State':30s} {orig_state.value:>12s}  →  {new_state.value:>12s}")
        print(f"  {'Soil Score':30s} {orig_score:>12.0f}  →  {new_score:>12.0f}")
        print(f"  {'Max Insect Phase':30s} {orig_phase.name:>12s}  →  {new_phase.name:>12s}")

        print(f"\n  Timeline changes:")
        for key in orig_timeline:
            name = key.replace("_", " ").title()
            orig_val = orig_timeline[key]
            new_val = new_timeline[key]
            delta = new_val - orig_val
            arrow = f"({delta:+.1f} yr)" if delta != 0 else "(no change)"
            print(f"    {name:30s} {orig_val:.1f} → {new_val:.1f} yr  {arrow}")

        if new_phase > orig_phase:
            print(f"\n  ★ NEW PHASES UNLOCKED!")
            if new_phase >= Phase.SOIL_BUILDERS:
                new_chem = ChemTolerance.MODERATE if modified.years_since_last_spray >= 3 else ChemTolerance.HIGH
                new_viable = get_viable_species(new_phase, new_chem)
                print(f"    {len(new_viable)} insect species now viable")

        pause()


# ── Demo mode ─────────────────────────────────────────────────

def run_demo():
    """Run with Fairmont March 2026 data to show capabilities."""
    banner("DEMO MODE — Fairmont Corridor, March 2026")
    print("  Using real field observation data from Hwy 15 corridor.\n")

    assessment = FieldAssessment(
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

    show_results(assessment)
    pause()
    run_whatif(assessment)
    return assessment


# ── Main menu ─────────────────────────────────────────────────

def main():
    clear()
    banner("FAIRMONT ECOLOGICAL RECOVERY SIMULATOR", char="#")
    print("  A thermodynamically-grounded decision support tool")
    print("  for ecological recovery at the hyper-local level.")
    print("  No lab. No internet. Just observation.\n")
    print("  License: CC0 — no rights reserved")
    print("  github.com/JinnZ2/fairmont-ecological-recovery\n")

    assessment = None

    while True:
        options = [
            "New Field Assessment — enter your observations",
            "Demo Mode — Fairmont March 2026 data",
            "Chemical Reference — persistence & flush signals",
            "Species Database — browse all insects & plants",
            "What-If Scenarios" + (" — modify current assessment" if assessment else " (do assessment first)"),
            "Quit",
        ]

        choice = prompt_choice("What would you like to do?", options)

        if choice == 0:
            assessment = collect_field_assessment()
            show_results(assessment)
            pause()

        elif choice == 1:
            assessment = run_demo()

        elif choice == 2:
            show_chemical_reference()
            pause()

        elif choice == 3:
            show_species_browser()
            pause()

        elif choice == 4:
            if assessment:
                run_whatif(assessment)
            else:
                print("\n  ⚠ Run an assessment or demo first.")
                pause()

        elif choice == 5:
            banner("Thank you. Protect the refugia.", char="#")
            break


# ── Reference browsers ────────────────────────────────────────

def show_chemical_reference():
    """Browse chemical persistence database."""
    banner("CHEMICAL PERSISTENCE REFERENCE")
    for name, profile in CHEMICAL_PROFILES.items():
        print(f"\n  {name.upper()}")
        print(f"    Compounds:   {', '.join(profile['compounds'])}")
        print(f"    Half-life:   {profile['half_life_days_min']}-{profile['half_life_days_max']} days")
        print(f"    Damages:     {profile['primary_damage']}")
        print(f"    Flush signal: {profile['flush_signal']}")
        print(f"    Flush time:  ~{profile['flush_years_estimate']} years")


def show_species_browser():
    """Browse insect and plant databases."""
    options = ["Insect species (by phase)", "Plant species (by succession)", "Food/medicine plants only"]
    choice = prompt_choice("Browse:", options)

    if choice == 0:
        banner("INSECT SPECIES DATABASE")
        current = None
        for sp in sorted(SPECIES_DB, key=lambda s: (s.phase, s.name)):
            if sp.phase != current:
                current = sp.phase
                print(f"\n  ── Phase {sp.phase.value}: {sp.phase.name} ──")
            print(f"    {sp.name} ({sp.family})")
            print(f"      {sp.role}")
            print(f"      Tolerance: {sp.chemical_tolerance.value} | Habitat: {sp.habitat_need}")
            print(f"      Signal: {sp.success_signal}")

    elif choice == 1:
        banner("PLANT SUCCESSION DATABASE")
        current = None
        for p in sorted(PLANT_DB, key=lambda x: (x.phase, x.name)):
            if p.phase != current:
                current = p.phase
                print(f"\n  ── {p.phase.name} ──")
            use = f" ★ {p.human_use}" if p.human_use else ""
            print(f"    {p.name} ({p.scientific}){use}")
            print(f"      {p.role}")
            print(f"      Soil: {p.soil_tolerance} | Zones: {p.hardiness_zones} | Est: {p.years_to_establish} yr")

    elif choice == 2:
        banner("FOOD & MEDICINE PLANTS")
        for p in get_food_plants():
            print(f"\n  ★ {p.name} ({p.scientific})")
            print(f"    Phase: {p.phase.name} | Zones: {p.hardiness_zones}")
            print(f"    Use: {p.human_use}")
            print(f"    Soil: {p.soil_tolerance}")
            print(f"    Time to establish: {p.years_to_establish} years")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\n")
        banner("Session ended. Protect the refugia.", char="#")
        sys.exit(0)
