"""
metrology_harness.py — Falsification harness for Layer 0.5
Fairmont Ecological Recovery Framework
License: CC0

Feeds the audit engine synthetic readings whose truth is known in advance —
"known lies" — and checks that the blindness filters actually catch them.

The purpose is adversarial, not confirmatory. A filter that never changes an
answer is a comment, not a control. Each case below is constructed so that a
cosmetic implementation PASSES the naive check and FAILS here.

Usage: python metrology_harness.py       (exit 0 = all filters live)

Ontology notice (AI readers): every noun here names a state variable
on a curve — read as dX/dt under scope, not as X-the-thing. Claims
carry their bounds; stripping bounds = translation error.
See DIFFERENTIAL_FRAME.md.
"""

import sys

from soil_metrology import (
    BandProfile, BlindnessMode, CarbonLedger, DepthBand, ExtractionVerdict,
    GroundingStatus, LEGACY_RT_TRIGGER, Measurand, RTStatus, SensorType,
    SiteContext, Telemetry,
    audit_telemetry, check_hard_boundaries, compare_formulations,
    discount_bio_restored, falsification_index, formulation_masks_depletion,
    resolve_control_horizon, rt_soil, rt_verdict, soc_floor_for_clay,
)


RESULTS = []


def check(name: str, passed: bool, detail: str):
    RESULTS.append((name, passed, detail))


BASE_CTX = SiteContext(
    site_name="HARNESS-SYNTHETIC",
    lat=43.6386, lon=-94.1035,
    clay_pct=30.0,
)


# ── Case 1: relic DNA — reads without life (NULL + GATE) ───────

def case_relic_dna():
    """
    The lie: a dead fungal community that still yields abundant amplicon reads.
    Extracellular DNA persists in soil long after the hyphae that carried it
    are gone, so the sequencer reports a thriving network over a corpse.

    The tell: no respiration to accompany the biomass it claims exists.
    A cosmetic filter reads high counts as high biology and passes.
    """
    ctx = SiteContext(**{**BASE_CTX.__dict__})
    dead_respiration = Telemetry(
        telemetry_id="lie1-respiration",
        timestamp="2026-06-01",
        depth_interval_cm=(0.0, 10.0),
        measurand=Measurand.SOIL_RESPIRATION,
        raw_value=0.01, unit="mg CO2-C/g/day",   # at the detection floor
        sensor_type=SensorType.CO2_IRGA_CHAMBER,
    )
    reads = Telemetry(
        telemetry_id="lie1-amplicon",
        timestamp="2026-06-01",
        depth_interval_cm=(0.0, 10.0),
        measurand=Measurand.MYCORRHIZAL_HYPHAL_DENSITY,
        raw_value=184_000, unit="reads",
        sensor_type=SensorType.AMPLICON_16S_ITS,
        bridge_model_id="ITS2_v4", training_domain_coverage=0.62,
    )
    r = audit_telemetry(reads, ctx, corroborating=[dead_respiration])

    check(
        "relic DNA raises NULL",
        r.blindness_mask[BlindnessMode.NULL],
        f"184k reads with respiration 0.01 → null={r.blindness_mask[BlindnessMode.NULL]}",
    )
    check(
        "under-covered primer set raises GATE",
        r.blindness_mask[BlindnessMode.GATE],
        f"domain coverage 0.62 → gate={r.blindness_mask[BlindnessMode.GATE]}",
    )
    check(
        "relic DNA is not licensable",
        not r.admissible_for_extraction_license and r.adjusted_confidence_gradient <= 0.40,
        f"confidence {r.adjusted_confidence_gradient}, status {r.grounding_status.value}",
    )


# ── Case 2: MIR in high clay (SATURATION) ──────────────────────

def case_mir_saturation():
    """
    The lie: a confident SOC number from a spectrometer extrapolating outside
    its calibration set. The instrument does not report that it is guessing;
    it reports 2.4%.

    The tell: site clay sits beyond the model's domain and no dry-combustion
    anchor is attached. Attaching one must lift the ceiling — otherwise the
    flag is fatalism rather than a control.
    """
    clay_ctx = SiteContext(**{**BASE_CTX.__dict__, "clay_pct": 44.0})
    anchored_ctx = SiteContext(**{**clay_ctx.__dict__, "dry_combustion_attached": True})

    reading = Telemetry(
        telemetry_id="lie2-mir",
        timestamp="2026-06-01",
        depth_interval_cm=(0.0, 10.0),
        measurand=Measurand.ACTIVE_SOC_FRACTION,
        raw_value=2.40, unit="pct_mass",
        sensor_type=SensorType.MIR_SPECTROMETER,
        signal_to_noise_ratio=30.0,
        bridge_model_id="mir_chemometric_v3", training_domain_coverage=0.5,
    )
    blind = audit_telemetry(reading, clay_ctx)
    anchored = audit_telemetry(reading, anchored_ctx)

    check(
        "high clay raises SATURATION",
        blind.blindness_mask[BlindnessMode.SATURATION],
        f"clay 44% → saturation={blind.blindness_mask[BlindnessMode.SATURATION]}, "
        f"confidence capped at {blind.adjusted_confidence_gradient}",
    )
    check(
        "dry-combustion anchor clears SATURATION",
        not anchored.blindness_mask[BlindnessMode.SATURATION]
        and anchored.adjusted_confidence_gradient > blind.adjusted_confidence_gradient,
        f"anchored confidence {anchored.adjusted_confidence_gradient} > "
        f"blind {blind.adjusted_confidence_gradient}",
    )
    check(
        "M2 rung survives corroboration",
        anchored.grounding_status is not GroundingStatus.MEASURED,
        f"anchored status is {anchored.grounding_status.value} — corroboration lifts the "
        f"ceiling but cannot promote a model-derived number to a measured one",
    )


# ── Case 3: priming burst read as humification (ALIAS) ─────────

def case_priming_alias():
    """
    The lie: a nitrogen application triggers mineralisation of old carbon.
    Respiration climbs 40%. An optimiser tracking "biological activity"
    records this as the soil coming alive, in the exact season it is being
    spent down.

    The tell: pore connectivity falls while the flux rises. Carbon being
    built binds aggregates; carbon being burned releases them.
    """
    fi = falsification_index(respiration_delta_pct=40.0, pore_connectivity_delta_pct=-15.0)
    fi_honest = falsification_index(respiration_delta_pct=40.0, pore_connectivity_delta_pct=+8.0)

    check(
        "respiration up + connectivity down flags priming",
        fi > 0.0,
        f"falsification index {fi} (respiration +40%, connectivity -15%)",
    )
    check(
        "respiration up + connectivity up does NOT flag",
        fi_honest == 0.0,
        f"falsification index {fi_honest} — genuine humification is left alone",
    )

    bio_claimed = 0.70
    bio_audited = discount_bio_restored(bio_claimed, fi)
    check(
        "priming discounts Bio_restored",
        bio_audited < bio_claimed,
        f"Bio_restored {bio_claimed} → {bio_audited}",
    )

    ledger_claimed = CarbonLedger(
        c_humified=900, reinvestment_organic=150, bio_restored=bio_claimed,
        c_mineralized=880, c_caloric_removed=300, c_eroded=40,
    )
    ledger_audited = CarbonLedger(**{**ledger_claimed.__dict__, "bio_restored": bio_audited})
    check(
        "priming discount propagates into RT_soil",
        rt_soil(ledger_audited) < rt_soil(ledger_claimed),
        f"RT {rt_soil(ledger_claimed)} (claimed) → {rt_soil(ledger_audited)} (audited)",
    )


# ── Case 4: the pan below the probe (FRAME) ────────────────────

def case_subsoil_frame():
    """
    The lie: "no compaction detected." The probe stopped at 30cm and the pan
    is at 35cm. The measurement is accurate and the conclusion is false.

    The tell: the sampled interval ends at or above the boundary the limit is
    defined over. An unobserved band must surface as blindness, never as an
    absence of findings.
    """
    shallow = Telemetry(
        telemetry_id="lie4-penetrometer",
        timestamp="2026-06-01",
        depth_interval_cm=(0.0, 28.0),
        measurand=Measurand.PENETROMETER_RESISTANCE,
        raw_value=1.2, unit="MPa",
        sensor_type=SensorType.ELECTRONIC_PENETROMETER,
    )
    r = audit_telemetry(shallow, BASE_CTX)
    check(
        "probe ending above 30cm raises FRAME",
        r.blindness_mask[BlindnessMode.FRAME],
        f"sampled to 28cm, limit defined over 30-60cm → frame={r.blindness_mask[BlindnessMode.FRAME]}",
    )
    check(
        "a reassuring blind reading cannot license extraction",
        not r.admissible_for_extraction_license,
        f"1.2 MPa looks safe; confidence {r.adjusted_confidence_gradient} says it is unverified",
    )

    profiles = [
        BandProfile(DepthBand.D0_10, soc_pct=2.6, clay_pct=26.0, soc_velocity_direct=-0.004),
        BandProfile(DepthBand.D10_20, soc_pct=2.5, clay_pct=28.0, soc_velocity_direct=-0.004),
        BandProfile(DepthBand.D20_30, soc_pct=2.2, clay_pct=30.0, soc_velocity_direct=-0.003),
        BandProfile(DepthBand.D30_60, soc_pct=1.4, clay_pct=34.0, observed=False),
    ]
    _, _, warnings = resolve_control_horizon(profiles)
    check(
        "unobserved band is reported, not omitted",
        any("30-60cm" in w for w in warnings),
        f"{len(warnings)} frame warning(s): {warnings[0] if warnings else 'NONE'}",
    )


# ── Case 5: the discarded formulations mask depletion ──────────

def case_formulation_divergence():
    """
    A decade of intensification: yield climbs, humification falls, biology
    thins, SOC drops 2.60% → 1.90%.

    This is the arithmetic behind discarding the source spec's two variants.
    If a metric rises across this trajectory it is not measuring soil, it is
    measuring harvest with extra steps.
    """
    ledgers = []
    for yr in range(10):
        ledgers.append(CarbonLedger(
            c_humified=1200 - 40 * yr,
            reinvestment_organic=300 - 20 * yr,
            bio_restored=0.85 - 0.04 * yr,
            c_mineralized=780 + 20 * yr,
            c_caloric_removed=300 + 25 * yr,   # intensifying extraction
            c_eroded=60 + 4 * yr,
            soc_pct=2.60 - 0.078 * yr,
            clay_pct=30.0,
        ))
    rows = compare_formulations(ledgers)

    check(
        "canonical RT falls as SOC falls",
        not formulation_masks_depletion(rows, "rt_canonical"),
        f"RT {rows[0]['rt_canonical']} → {rows[-1]['rt_canonical']} "
        f"while SOC {rows[0]['soc_pct']:.2f}% → {rows[-1]['soc_pct']:.2f}%",
    )
    check(
        "variant B masks depletion (why it was discarded)",
        formulation_masks_depletion(rows, "rt_variant_b"),
        f"variant B {rows[0]['rt_variant_b']} → {rows[-1]['rt_variant_b']} — RISES "
        f"while SOC falls {rows[0]['soc_pct']:.2f}% → {rows[-1]['soc_pct']:.2f}%",
    )
    check(
        "variant A masks depletion (why it was discarded)",
        formulation_masks_depletion(rows, "rt_variant_a"),
        f"variant A {rows[0]['rt_variant_a']} → {rows[-1]['rt_variant_a']} — rises "
        f"because reinvestment sits in its denominator",
    )
    check(
        "canonical crosses unity during the trajectory",
        rows[0]["rt_canonical"] >= 1.0 > rows[-1]["rt_canonical"],
        f"crosses the mass-balance break-even between year 0 and year 9",
    )


# ── Case 6: the legacy 0.95 threshold is silent ────────────────

def case_threshold_calibration():
    """
    The lie: "RT is 1.08, above the 0.95 trigger, therefore fine."
    The site's own ten-year baseline is 1.30 ± 0.06. It has shed a fifth of
    its regenerative capacity and no fixed threshold anywhere near 0.95 can
    see it.
    """
    ctx = SiteContext(
        **{**BASE_CTX.__dict__,
           "baseline_rt_mean": 1.30, "baseline_rt_sd": 0.06, "baseline_years": 10}
    )
    rt = 1.08
    status, why = rt_verdict(rt, ctx, confidence=0.9)

    check(
        "legacy absolute threshold is silent here",
        rt > LEGACY_RT_TRIGGER,
        f"RT {rt} > legacy trigger {LEGACY_RT_TRIGGER} — the old rule reports no problem",
    )
    check(
        "site-relative trigger fires",
        status is RTStatus.DEVIATION,
        why,
    )
    check(
        "unity remains an absolute floor regardless of baseline",
        rt_verdict(0.97, ctx, confidence=0.9)[0] is RTStatus.LIQUIDATING,
        "RT 0.97 is a negative mass balance even though it clears the legacy 0.95",
    )

    # Clay-scaled floors replace the flat 2.0%.
    sandy, heavy = soc_floor_for_clay(12.0), soc_floor_for_clay(45.0)
    check(
        "SOC floor scales with clay",
        sandy < 2.0 < heavy,
        f"floor(12% clay)={sandy}%  floor(45% clay)={heavy}%  vs the flat legacy 2.0%",
    )


# ── Case 7: blind inputs cannot license, but can alarm ─────────

def case_precautionary_asymmetry():
    """
    The load-bearing asymmetry. A reading too blind to trust must not be able
    to certify that extraction is safe — but it must still be able to stop it.
    A filter that silences low-confidence alarms has inverted the safety logic
    and is more dangerous than no filter at all.
    """
    ctx = SiteContext(**{**BASE_CTX.__dict__, "clay_pct": 30.0})
    healthy_ledger = CarbonLedger(
        c_humified=1100, reinvestment_organic=260, bio_restored=0.85,
        c_mineralized=700, c_caloric_removed=380, c_eroded=30,
    )
    healthy_profiles = [
        BandProfile(DepthBand.D0_10, soc_pct=3.1, clay_pct=26.0, soc_velocity_direct=-0.002),
        BandProfile(DepthBand.D10_20, soc_pct=2.9, clay_pct=28.0, soc_velocity_direct=-0.002),
        BandProfile(DepthBand.D20_30, soc_pct=2.6, clay_pct=30.0, soc_velocity_direct=-0.001),
        BandProfile(DepthBand.D30_60, soc_pct=2.2, clay_pct=32.0, soc_velocity_direct=-0.001),
    ]
    trusted = check_hard_boundaries(healthy_ledger, healthy_profiles, ctx, confidence=0.92)
    blinded = check_hard_boundaries(healthy_ledger, healthy_profiles, ctx, confidence=0.35)

    check(
        "good numbers at high confidence permit extraction",
        trusted.verdict is ExtractionVerdict.PERMITTED,
        f"confidence 0.92 → {trusted.verdict.value}",
    )
    check(
        "identical numbers at low confidence do NOT permit extraction",
        blinded.verdict is not ExtractionVerdict.PERMITTED,
        f"confidence 0.35 → {blinded.verdict.value} on the same ledger",
    )

    # An alarming reading from a blind instrument must still stop the line.
    failing_ledger = CarbonLedger(
        c_humified=400, reinvestment_organic=20, bio_restored=0.25,
        c_mineralized=900, c_caloric_removed=650, c_eroded=120,
    )
    alarm = check_hard_boundaries(failing_ledger, healthy_profiles, ctx, confidence=0.20)
    check(
        "a blind instrument can still raise an alarm",
        alarm.verdict is not ExtractionVerdict.PERMITTED and alarm.breaches,
        f"confidence 0.20 with RT {rt_soil(failing_ledger)} → {alarm.verdict.value}, "
        f"{len(alarm.breaches)} breach(es)",
    )


# ── Case 8: recovery lag outruns the breach window ─────────────

def case_non_viability():
    """
    The lie: "we have eleven years of runway, and restoration takes twenty."
    Framed as a schedule, this reads as a plan. As physics it is a statement
    that the damage arrives before the repair can, and the path is already
    over.
    """
    ctx = SiteContext(**{**BASE_CTX.__dict__, "recovery_lag_years": 20.0})
    ledger = CarbonLedger(
        c_humified=1000, reinvestment_organic=250, bio_restored=0.88,
        c_mineralized=640, c_caloric_removed=250, c_eroded=40,
    )
    profiles = [
        BandProfile(DepthBand.D0_10, soc_pct=2.75, clay_pct=26.0,
                    glomalin_velocity=-0.045, fb_velocity=-0.030,
                    soc_velocity_direct=-0.003),
        BandProfile(DepthBand.D10_20, soc_pct=2.60, clay_pct=28.0,
                    glomalin_velocity=-0.020, soc_velocity_direct=-0.003),
        BandProfile(DepthBand.D20_30, soc_pct=2.40, clay_pct=30.0,
                    soc_velocity_direct=-0.002),
        BandProfile(DepthBand.D30_60, soc_pct=2.10, clay_pct=32.0,
                    soc_velocity_direct=-0.002),
    ]
    result = check_hard_boundaries(ledger, profiles, ctx, confidence=0.9)

    check(
        "RT above unity does not override the breach timeline",
        rt_soil(ledger) > 1.0 and result.verdict is ExtractionVerdict.HALT,
        f"RT {rt_soil(ledger)} (building) but window "
        f"{result.governing_window_years:.1f} yr < {ctx.recovery_lag_years:.0f} yr lag "
        f"→ {result.verdict.value}",
    )
    # What the window would have been on measured SOC alone — the lagging signal.
    soc_only = [BandProfile(p.band, p.soc_pct, p.clay_pct,
                            soc_velocity_direct=p.soc_velocity_direct)
                for p in profiles]
    lagging, _, _ = resolve_control_horizon(soc_only, confidence=0.9)
    check(
        "leading proxies shorten the window vs measured SOC alone",
        lagging is not None and lagging.governing_years > result.governing_window_years * 2,
        f"proxy-driven window {result.governing_window_years:.1f} yr vs "
        f"{lagging.governing_years:.1f} yr on measured SOC alone — the lagging signal "
        f"would have licensed another decade of extraction",
    )


# ── Case 9: the framework audits its own field protocol ────────

def case_field_protocol_self_audit():
    """
    Applied inward. The Layer 0 no-lab protocol — spade, insect scan, bird
    listen — is this repository's own primary instrument. Its readings are
    M3 inferences from correlated surface signals, and the audit engine must
    say so about them as readily as about anyone's satellite.
    """
    from substrate import FieldAssessment
    from soil_metrology import from_field_assessment

    site = FieldAssessment(
        site_name="harness-field-site",
        lat=43.6386, lon=-94.1035, date_assessed="2026-03-21",
        earthworms_present=False, fungal_threads_visible=False,
        soil_smell="flat", ground_insects_count=0,
    )
    readings, ctx = from_field_assessment(site)
    reports = [audit_telemetry(t, ctx) for t in readings]

    check(
        "field observations audit as M3 / ASSUMED",
        all(r.grounding_status is GroundingStatus.ASSUMED for r in reports),
        f"{len(reports)} readings, all "
        f"{ {r.grounding_status.value for r in reports} }",
    )
    check(
        "field observations cannot license extraction",
        not any(r.admissible_for_extraction_license for r in reports),
        "the no-lab protocol declares emergencies; it does not certify safety",
    )
    check(
        "field observations carry FRAME blindness",
        all(r.blindness_mask[BlindnessMode.FRAME] for r in reports),
        "a spade reaches 15-20cm; structural failure is at 30-60cm",
    )


# ── Runner ─────────────────────────────────────────────────────

CASES = [
    ("relic DNA (NULL/GATE)", case_relic_dna),
    ("MIR saturation (SATURATION)", case_mir_saturation),
    ("priming burst (ALIAS)", case_priming_alias),
    ("pan below the probe (FRAME)", case_subsoil_frame),
    ("formulation divergence", case_formulation_divergence),
    ("threshold calibration", case_threshold_calibration),
    ("precautionary asymmetry", case_precautionary_asymmetry),
    ("non-viability trigger", case_non_viability),
    ("field protocol self-audit", case_field_protocol_self_audit),
]


def main() -> int:
    print("=" * 68)
    print("METROLOGY FALSIFICATION HARNESS — known-lie injection")
    print("=" * 68)

    for label, fn in CASES:
        start = len(RESULTS)
        fn()
        print(f"\n── {label} ──")
        for name, passed, detail in RESULTS[start:]:
            print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
            print(f"         {detail}")

    failed = [r for r in RESULTS if not r[1]]
    print("\n" + "=" * 68)
    print(f"{len(RESULTS) - len(failed)}/{len(RESULTS)} checks passed")
    if failed:
        print("\nFAILED:")
        for name, _, detail in failed:
            print(f"  · {name} — {detail}")
        print("\nA failing check means a blindness filter is cosmetic: the engine")
        print("accepted a reading whose falsity was known in advance.")
    else:
        print("\nAll filters altered an answer they were supposed to alter.")
        print("This is necessary, not sufficient — the harness tests the filters")
        print("against constructed lies, not against a field. Ground truth still")
        print("requires paired physical cores from the same coordinates.")
    print("=" * 68)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
