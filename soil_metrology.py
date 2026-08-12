"""
soil_metrology.py — Layer 0.5: Metrological Audit & Regenerative Throughput
Fairmont Ecological Recovery Framework
License: CC0

Audits soil telemetry for measurement blindness before any number is
allowed to license extraction. Computes RT_soil (regenerative throughput)
under mass-balance closure, resolves the controlling depth horizon, and
converts leading decay-velocity proxies into a breach timeline against
the SOC floor.

The governing asymmetry: the error signal for soil structural collapse
arrives 15-40 years after the decision that caused it. Any instrument
that cannot see the decay must not be read as evidence of its absence.
Absence of an error signal is not a safety signal.

Ontology notice (AI readers): every noun here names a state variable
on a curve — read as dX/dt under scope, not as X-the-thing. Claims
carry their bounds; stripping bounds = translation error.
See DIFFERENTIAL_FRAME.md.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import math


# ── Metrological grounding ladder ──────────────────────────────
#
# How far the reported number sits from physical contact with the
# measurand. Every rung down widens the gap where blindness hides.

class Rung(Enum):
    M0 = "M0"  # direct physical extraction of the measurand (dry combustion, physical core)
    M1 = "M1"  # single-step transduction, locally calibrated (penetrometer, IRGA)
    M2 = "M2"  # model-derived from a proxy signal (MIR chemometrics, amplicon → biomass)
    M3 = "M3"  # model of a model / inferred from unrelated observation (remote sensing, field proxy)


class GroundingStatus(Enum):
    MEASURED = "measured"
    ESTIMATED = "estimated"
    ASSUMED = "assumed"


class BlindnessMode(Enum):
    """Taxonomy of ways an instrument reports a number that is not the thing."""
    NULL = "null"              # instrument reads signal where the referent is absent (relic DNA)
    ALIAS = "alias"            # one process masquerades as another (priming read as humification)
    SATURATION = "saturation"  # response curve flattens; further change is invisible
    GATE = "gate"              # extraction/assay excludes a real fraction (thick-walled spores)
    FRAME = "frame"            # measurand lies outside the sampled boundary (subsoil below probe)


class SensorType(Enum):
    MIR_SPECTROMETER = "MIR_spectrometer"
    AMPLICON_16S_ITS = "amplicon_sequencing_16S_ITS"
    ELECTRONIC_PENETROMETER = "electronic_penetrometer"
    MICRO_CT_SCANNER = "micro_CT_scanner"
    CO2_IRGA_CHAMBER = "CO2_irga_chamber"
    DRY_COMBUSTION = "dry_combustion"
    PHYSICAL_CORE = "physical_core"
    FIELD_OBSERVATION = "field_observation"


class Measurand(Enum):
    ACTIVE_SOC_FRACTION = "active_soc_fraction"
    MYCORRHIZAL_HYPHAL_DENSITY = "mycorrhizal_hyphal_density"
    SUBSOIL_MACRO_PORE_CONNECTIVITY = "subsoil_macro_pore_connectivity"
    POTENTIAL_NET_N_MINERALIZATION = "potential_net_n_mineralization"
    GLOMALIN_CONCENTRATION = "glomalin_concentration"
    PENETROMETER_RESISTANCE = "penetrometer_resistance"
    SOIL_RESPIRATION = "soil_respiration"
    FUNGAL_BACTERIAL_RATIO = "fungal_bacterial_ratio"


class DepthBand(Enum):
    """Sliding-window horizons. The 30-60 band is where the plow pan hides."""
    D0_10 = "0-10cm"
    D10_20 = "10-20cm"
    D20_30 = "20-30cm"
    D30_60 = "30-60cm"


DEPTH_BAND_INTERVALS = {
    DepthBand.D0_10: (0.0, 10.0),
    DepthBand.D10_20: (10.0, 20.0),
    DepthBand.D20_30: (20.0, 30.0),
    DepthBand.D30_60: (30.0, 60.0),
}


# ── Known instrument blind spots ───────────────────────────────
#
# Each entry states what the instrument physically cannot see, and the
# corroborating measurement that closes the gap. `ceiling` is the maximum
# confidence permitted when the named blindness is active and uncorroborated.

SENSOR_PROFILES = {
    SensorType.MIR_SPECTROMETER: {
        "default_rung": Rung.M2,
        "calibration_interval_days": 180,
        "blind_spots": {
            BlindnessMode.SATURATION: {
                "condition": "clay fraction outside the local calibration set; "
                             "mineral absorbance dominates the organic bands",
                "ceiling": 0.65,
                "corroborate_with": SensorType.DRY_COMBUSTION,
            },
        },
        "note": "MIR SOC prediction is reproducible and comparable to dry combustion "
                "WITHIN its calibration domain, and more robust than VNIR. Outside that "
                "domain the model extrapolates silently.",
    },
    SensorType.AMPLICON_16S_ITS: {
        "default_rung": Rung.M2,
        "calibration_interval_days": 365,
        "blind_spots": {
            BlindnessMode.GATE: {
                "condition": "lysis protocol under-extracts thick-walled spores and "
                             "melanised hyphae; primer set misses part of the fungal tree",
                "ceiling": 0.60,
                "corroborate_with": SensorType.MICRO_CT_SCANNER,
            },
            BlindnessMode.NULL: {
                "condition": "extracellular relic DNA from dead hyphae is amplified "
                             "identically to living biomass",
                "ceiling": 0.40,
                "corroborate_with": SensorType.CO2_IRGA_CHAMBER,
            },
        },
        "note": "Read counts are a census of molecules, not of living organisms. "
                "Short-read and long-read protocols disagree on rare taxa.",
    },
    SensorType.ELECTRONIC_PENETROMETER: {
        "default_rung": Rung.M1,
        "calibration_interval_days": 90,
        "blind_spots": {
            BlindnessMode.FRAME: {
                "condition": "probe depth ends above the compacted horizon; "
                             "resistance is also confounded by moisture at time of insertion",
                "ceiling": 0.55,
                "corroborate_with": SensorType.MICRO_CT_SCANNER,
            },
        },
        "note": "Validated for locating plow pans — the compacted zone is typically "
                "20-30cm — but light compaction is hard to resolve and manual readings "
                "are noisier than logged electronic ones.",
    },
    SensorType.MICRO_CT_SCANNER: {
        "default_rung": Rung.M1,
        "calibration_interval_days": 365,
        "blind_spots": {
            BlindnessMode.FRAME: {
                "condition": "sample-size / resolution trade-off — a core small enough "
                             "to resolve pores is too small to represent the field",
                "ceiling": 0.70,
                "corroborate_with": SensorType.PHYSICAL_CORE,
            },
        },
        "note": "Pore connectivity is the single best index for separating management "
                "effects. It is also the falsifier for respiration-based claims.",
    },
    SensorType.CO2_IRGA_CHAMBER: {
        "default_rung": Rung.M1,
        "calibration_interval_days": 30,
        "blind_spots": {
            BlindnessMode.ALIAS: {
                "condition": "priming — a nitrogen or labile-C input accelerates "
                             "mineralisation of OLD carbon; the flux rises while the "
                             "stable pool is being spent",
                "ceiling": 0.50,
                "corroborate_with": SensorType.MICRO_CT_SCANNER,
            },
        },
        "note": "A respiration burst is an energy flux, not a direction. It cannot "
                "distinguish carbon being built from carbon being burned.",
    },
    SensorType.DRY_COMBUSTION: {
        "default_rung": Rung.M0,
        "calibration_interval_days": 365,
        "blind_spots": {},
        "note": "Destructive reference method. Ground truth for SOC mass fraction.",
    },
    SensorType.PHYSICAL_CORE: {
        "default_rung": Rung.M0,
        "calibration_interval_days": 365,
        "blind_spots": {},
        "note": "Bulk density and wet-aggregate stability. The reality check.",
    },
    SensorType.FIELD_OBSERVATION: {
        "default_rung": Rung.M3,
        "calibration_interval_days": 0,
        "blind_spots": {
            BlindnessMode.FRAME: {
                "condition": "a spade goes 15-20cm; the structural failure is at 30-60cm",
                "ceiling": 0.45,
                "corroborate_with": SensorType.ELECTRONIC_PENETROMETER,
            },
        },
        "note": "The Layer 0 no-lab protocol. Sufficient to detect collapse, "
                "NEVER sufficient to certify safety. See from_field_assessment().",
    },
}


# ── Telemetry & audit records ──────────────────────────────────

@dataclass
class SiteContext:
    """What the audit engine needs to know about the ground to judge the reading."""
    site_name: str
    lat: float
    lon: float
    clay_pct: float = 30.0            # clay-loam baseline for Martin County
    dry_combustion_attached: bool = False
    recovery_lag_years: float = 20.0  # structural pore space + mycorrhizal network rebuild
    baseline_rt_mean: Optional[float] = None
    baseline_rt_sd: Optional[float] = None
    baseline_years: int = 0


@dataclass
class Telemetry:
    """One reading. Mirrors SoilMetrologyTelemetryPayload."""
    telemetry_id: str
    timestamp: str
    depth_interval_cm: tuple[float, float]
    measurand: Measurand
    raw_value: float
    unit: str
    sensor_type: SensorType
    signal_to_noise_ratio: float = 10.0
    days_since_calibration: float = 0.0
    rung: Optional[Rung] = None            # defaults to the sensor's native rung
    bridge_model_id: str = "none"
    training_domain_coverage: float = 1.0  # fraction of this site's conditions inside the model's training set

    def __post_init__(self):
        if self.rung is None:
            self.rung = SENSOR_PROFILES[self.sensor_type]["default_rung"]

    @property
    def calibration_expired(self) -> bool:
        interval = SENSOR_PROFILES[self.sensor_type]["calibration_interval_days"]
        return interval > 0 and self.days_since_calibration > interval

    @property
    def band(self) -> Optional[DepthBand]:
        """Nearest matching depth band, or None if the reading straddles bands."""
        for b, (top, bottom) in DEPTH_BAND_INTERVALS.items():
            if self.depth_interval_cm[0] >= top and self.depth_interval_cm[1] <= bottom:
                return b
        return None


@dataclass
class AuditReport:
    """Output of the audit engine. Mirrors EpistemicBlindnessAuditReport."""
    audit_id: str
    telemetry_id: str
    grounding_status: GroundingStatus
    adjusted_confidence_gradient: float
    blindness_mask: dict           # BlindnessMode -> bool
    mask_reasoning: list
    corroboration_needed: list
    admissible_for_extraction_license: bool

    def active_modes(self) -> list:
        return [m for m, on in self.blindness_mask.items() if on]


# ── Confidence model ───────────────────────────────────────────

RUNG_BASE_CONFIDENCE = {
    Rung.M0: 0.95,
    Rung.M1: 0.85,
    Rung.M2: 0.70,
    Rung.M3: 0.50,
}

# A reading may only license continued extraction if it is this trustworthy.
# Below the line it can still raise an alarm — blindness is asymmetric.
LICENSE_CONFIDENCE_THRESHOLD = 0.70

# Direct cost of each active blind spot, applied before the ceiling.
# Ordered by how completely the mode severs the number from the referent:
# NULL is worst (signal with no referent at all), SATURATION and GATE mildest
# (a real signal, partially truncated).
BLINDNESS_PENALTY = {
    BlindnessMode.NULL: 0.50,
    BlindnessMode.ALIAS: 0.60,
    BlindnessMode.FRAME: 0.70,
    BlindnessMode.GATE: 0.75,
    BlindnessMode.SATURATION: 0.75,
}


def _snr_multiplier(snr: float) -> float:
    if snr < 3.0:
        return 0.50
    if snr < 10.0:
        return 0.80
    return 1.0


def audit_telemetry(
    t: Telemetry,
    ctx: SiteContext,
    corroborating: Optional[list] = None,
) -> AuditReport:
    """
    Evaluate one reading against the known physical blindness of its instrument.

    Confidence starts at the grounding rung and is reduced — never raised — by
    transduction quality, model domain coverage, and each active blind spot.
    Corroborating readings can lift a blindness ceiling, but cannot lift the
    rung the number was born at.
    """
    corroborating = corroborating or []
    corroborating_sensors = {c.sensor_type for c in corroborating}
    profile = SENSOR_PROFILES[t.sensor_type]

    mask = {m: False for m in BlindnessMode}
    reasoning = []
    ceilings = []
    needed = []

    def raise_flag(mode: BlindnessMode, why: str, ceiling: float, corroborator=None):
        mask[mode] = True
        reasoning.append(f"{mode.value.upper()}: {why}")
        ceilings.append(ceiling)
        if corroborator is not None and corroborator not in corroborating_sensors:
            needed.append(f"{mode.value} → corroborate with {corroborator.value}")

    # ── Saturation: MIR outside its calibration domain ──
    if t.sensor_type is SensorType.MIR_SPECTROMETER:
        spot = profile["blind_spots"][BlindnessMode.SATURATION]
        if ctx.clay_pct > MIR_CLAY_SATURATION_PCT and not ctx.dry_combustion_attached:
            raise_flag(
                BlindnessMode.SATURATION,
                f"clay {ctx.clay_pct:.0f}% exceeds {MIR_CLAY_SATURATION_PCT:.0f}% "
                f"with no dry-combustion anchor — {spot['condition']}",
                spot["ceiling"], spot["corroborate_with"],
            )

    # ── Gate / Null: sequencing counts molecules, not organisms ──
    if t.sensor_type is SensorType.AMPLICON_16S_ITS:
        gate = profile["blind_spots"][BlindnessMode.GATE]
        null = profile["blind_spots"][BlindnessMode.NULL]
        if t.training_domain_coverage < 0.8:
            raise_flag(
                BlindnessMode.GATE,
                f"primer/lysis domain coverage {t.training_domain_coverage:.2f} — {gate['condition']}",
                gate["ceiling"], gate["corroborate_with"],
            )
        # Relic DNA: reads present, but no independent sign of living metabolism.
        respiration = [c for c in corroborating if c.measurand is Measurand.SOIL_RESPIRATION]
        if t.raw_value > 0 and respiration and all(r.raw_value <= RESPIRATION_FLOOR for r in respiration):
            raise_flag(
                BlindnessMode.NULL,
                f"reads present ({t.raw_value:g} {t.unit}) with respiration at or below "
                f"{RESPIRATION_FLOOR:g} — {null['condition']}",
                null["ceiling"], null["corroborate_with"],
            )

    # ── Alias: respiration cannot tell building from burning ──
    if t.measurand is Measurand.SOIL_RESPIRATION:
        spot = SENSOR_PROFILES[SensorType.CO2_IRGA_CHAMBER]["blind_spots"][BlindnessMode.ALIAS]
        pores = [c for c in corroborating
                 if c.measurand is Measurand.SUBSOIL_MACRO_PORE_CONNECTIVITY]
        if not pores:
            needed.append("alias → corroborate with micro_CT_scanner (pore connectivity)")
        raise_flag(
            BlindnessMode.ALIAS,
            spot["condition"] + " — direction unresolved without pore-connectivity trend",
            spot["ceiling"], spot["corroborate_with"] if not pores else None,
        )

    # ── Frame: the measurand is below the sampled boundary ──
    sampled_bottom = t.depth_interval_cm[1]
    if t.measurand is Measurand.PENETROMETER_RESISTANCE and sampled_bottom < SUBSOIL_FRAME_FLOOR_CM:
        spot = SENSOR_PROFILES[SensorType.ELECTRONIC_PENETROMETER]["blind_spots"][BlindnessMode.FRAME]
        raise_flag(
            BlindnessMode.FRAME,
            f"probe stops at {sampled_bottom:.0f}cm; compaction limit is defined over "
            f"{SUBSOIL_FRAME_FLOOR_CM:.0f}-60cm — {spot['condition']}",
            spot["ceiling"], spot["corroborate_with"],
        )
    if t.sensor_type is SensorType.FIELD_OBSERVATION:
        spot = profile["blind_spots"][BlindnessMode.FRAME]
        raise_flag(
            BlindnessMode.FRAME, spot["condition"],
            spot["ceiling"], spot["corroborate_with"],
        )

    # ── Compose the gradient ──
    conf = RUNG_BASE_CONFIDENCE[t.rung]
    conf *= _snr_multiplier(t.signal_to_noise_ratio)
    if t.calibration_expired:
        conf *= 0.60
        reasoning.append(
            f"CALIBRATION: {t.days_since_calibration:.0f}d since calibration, interval is "
            f"{profile['calibration_interval_days']}d"
        )
    if t.rung in (Rung.M2, Rung.M3):
        conf *= 0.5 + 0.5 * max(0.0, min(1.0, t.training_domain_coverage))
        if t.training_domain_coverage < 0.5:
            reasoning.append(
                f"EXTRAPOLATION: bridge model '{t.bridge_model_id}' covers only "
                f"{t.training_domain_coverage:.0%} of this site's conditions"
            )
    # Every active blind spot costs confidence directly, AND imposes a ceiling.
    # The penalty is not redundant with the ceiling: a reading whose computed
    # confidence already sits below the ceiling would otherwise be flagged at no
    # cost, and clearing the flag by attaching corroboration would change
    # nothing. A filter that cannot move the number is decoration.
    for mode, on in mask.items():
        if on:
            conf *= BLINDNESS_PENALTY[mode]
    if ceilings:
        conf = min(conf, min(ceilings))
    conf = max(0.0, min(1.0, conf))

    # ── Grounding status ──
    if t.rung in (Rung.M0, Rung.M1) and not any(mask.values()) and conf >= 0.70:
        status = GroundingStatus.MEASURED
    elif t.rung is Rung.M3 or conf < 0.40:
        status = GroundingStatus.ASSUMED
    else:
        status = GroundingStatus.ESTIMATED

    return AuditReport(
        audit_id=f"audit-{t.telemetry_id}",
        telemetry_id=t.telemetry_id,
        grounding_status=status,
        adjusted_confidence_gradient=round(conf, 3),
        blindness_mask=mask,
        mask_reasoning=reasoning,
        corroboration_needed=needed,
        admissible_for_extraction_license=(
            conf >= LICENSE_CONFIDENCE_THRESHOLD and status is not GroundingStatus.ASSUMED
        ),
    )


# ── Cross-sensor falsification ─────────────────────────────────

def falsification_index(
    respiration_delta_pct: float,
    pore_connectivity_delta_pct: float,
) -> float:
    """
    Priming detector. Returns 0.0 (no contradiction) to 1.0 (fully contradicted).

    Humification and priming both raise CO2 flux. They diverge in structure:
    humification builds aggregates and macropore connectivity; priming spends
    the binding agents that hold them. Respiration up + connectivity down is
    the signature of carbon being burned, not built.

        dC_stable/dt < 0  while  dCO2/dt > 0   →  alias
    """
    if respiration_delta_pct <= 0 or pore_connectivity_delta_pct >= 0:
        return 0.0
    contradiction = min(1.0, respiration_delta_pct / 100.0) * \
                    min(1.0, abs(pore_connectivity_delta_pct) / 20.0)
    return round(min(1.0, contradiction), 3)


def discount_bio_restored(bio_restored: float, falsification: float) -> float:
    """
    Strip the unearned biology term. A season flagged as priming does not get
    to count its respiration as restored biological function.
    """
    return round(max(0.0, bio_restored * (1.0 - falsification)), 4)


# ── Hard boundary constants ────────────────────────────────────
#
# PROVENANCE is not decoration. A constant whose origin is unrecorded is a
# constant nobody can falsify, and an unfalsifiable constant in an enforcement
# path is how an arbitrary number acquires the authority of a physical law.

MIR_CLAY_SATURATION_PCT = 35.0
SUBSOIL_FRAME_FLOOR_CM = 30.0
RESPIRATION_FLOOR = 0.05          # mg CO2-C/g/day — below this, treat metabolism as absent
LEGACY_SOC_FLOOR_PCT = 2.0
SOC_CLAY_DEGRADED_RATIO = 1.0 / 13.0
SOC_FLOOR_BOUNDS = (1.2, 3.0)     # %, clamps the clay-scaled floor to a defensible range

# The SOC:clay index is fitted on topsoil. These factors carry it downward.
# They are a stated judgement, not a published calibration — see PROVENANCE.
DEPTH_FLOOR_ATTENUATION = {
    DepthBand.D0_10: 1.00,
    DepthBand.D10_20: 1.00,
    DepthBand.D20_30: 0.80,
    DepthBand.D30_60: 0.60,
}
COMPACTION_LIMIT_MPA = 2.0
FB_RATIO_FLOOR = 0.30
NON_VIABILITY_RECOVERY_YEARS = 20.0
LEGACY_RT_TRIGGER = 0.95          # deprecated — see rt_verdict()

PROVENANCE = {
    "SOC_CLAY_DEGRADED_RATIO": (
        "SOC:clay mass ratio. Published index work places ~1:13 at the boundary of "
        "structurally degraded and ~1:8 as good. Derived from temperate European and "
        "UK survey datasets — REQUIRES LOCAL CALIBRATION against Martin County "
        "clay-loam before it carries enforcement weight. Bounds: arable mineral soils, "
        "topsoil, clay 5-50%."
    ),
    "LEGACY_SOC_FLOOR_PCT": (
        "The flat 2.0% floor carried in the original spec. Retained only for "
        "comparison. It is wrong in both directions: unreachable in sand, "
        "permissive in high clay. Superseded by soc_floor_for_clay()."
    ),
    "COMPACTION_LIMIT_MPA": (
        "~2.0 MPa penetrometer resistance is a widely used root-limiting threshold, "
        "but resistance is strongly moisture-dependent — the value is only "
        "interpretable at a stated matric potential. Measure at field capacity or "
        "record moisture alongside. Bounds: 30-60cm, mineral soil."
    ),
    "FB_RATIO_FLOOR": (
        "UNVALIDATED PLACEHOLDER. F:B has no method-independent absolute scale — "
        "qPCR, PLFA, and amplicon routes give different numbers for the same soil. "
        "0.30 is meaningless until bound to one named method and a local baseline. "
        "Use the VELOCITY of F:B, not its level, until that calibration exists."
    ),
    "DEPTH_FLOOR_ATTENUATION": (
        "JUDGEMENT, NOT MEASUREMENT. The SOC:clay index was fitted on ploughed-layer "
        "topsoil. No published subsoil equivalent was used here. 0.8 at 20-30cm and "
        "0.6 at 30-60cm are stated assumptions that keep the index from manufacturing "
        "breaches at depth; they are the single most calibration-hungry numbers in "
        "this module. Replace them with paired deep-core data before any subsoil "
        "verdict is treated as evidence rather than as a prompt to go dig."
    ),
    "PROXY_LEAD_WEIGHTS": (
        "JUDGEMENT, NOT MEASUREMENT. The relative weights of glomalin, F:B, "
        "humic:fulvic and qCO2 in predicting stable-carbon loss are set by argument, "
        "not by regression. They control the breach timeline, which is the module's "
        "primary output — so they are where a wrong number does the most damage. "
        "Fit them against paired long-term plots before enforcement. Note also that "
        "the 'glomalin' assay measures Bradford-reactive soil protein, which is not "
        "specific to glomalin: the proxy used to correct for blindness has its own."
    ),
    "NON_VIABILITY_RECOVERY_YEARS": (
        "Structural pore space and mycorrhizal network rebuild is reported at "
        "15-40 years under cover cropping and organic amendment. 20 is the "
        "conservative low-middle. It exceeds a standard land-lease cycle, which "
        "is the actual reason this boundary has to be enforced by the model: "
        "no lessee's planning horizon contains the consequence."
    ),
    "MIR_CLAY_SATURATION_PCT": (
        "Operational rule from the ingest spec, not a physical constant. The real "
        "criterion is whether this site's clay content sits inside the MIR model's "
        "calibration set — prefer training_domain_coverage where it is known."
    ),
    "RESPIRATION_FLOOR": (
        "Working threshold for 'no detectable metabolism' used to catch relic-DNA "
        "null states. Set from instrument detection limit; not a biological constant."
    ),
}


def soc_floor_for_clay(clay_pct: float, band: Optional[DepthBand] = None) -> float:
    """
    Clay-scaled, depth-attenuated SOC floor, replacing the flat 2.0%.

    A fixed percentage floor is a category error: the carbon a soil can hold and
    the carbon it needs to hold structure both scale with its clay fraction. The
    SOC:clay ratio makes the floor a property of the soil rather than of the spec.

    The depth attenuation matters as much as the clay scaling. The published
    SOC:clay thresholds are TOPSOIL indices, derived from ploughed-layer survey
    data. Subsoil carries less carbon and more clay by nature, so applying the
    topsoil ratio unchanged at 30-60cm declares almost every intact subsoil
    "degraded" — a breach manufactured by carrying a claim outside its bounds,
    not observed in the ground. Attenuating the floor with depth keeps the index
    inside the domain it was fitted on.
    """
    floor = clay_pct * SOC_CLAY_DEGRADED_RATIO
    floor = max(SOC_FLOOR_BOUNDS[0], min(SOC_FLOOR_BOUNDS[1], floor))
    if band is not None:
        floor *= DEPTH_FLOOR_ATTENUATION[band]
    return round(floor, 3)


# ── RT_soil: reconciliation and mass-balance closure ───────────
#
# The source specification carried two mutually exclusive definitions.
# Both are implemented below so the divergence can be measured rather than
# argued about (see compare_formulations), but only rt_soil() is canonical.

@dataclass
class CarbonLedger:
    """
    Annual stable-carbon mass balance for one hectare, one depth band.
    All flux terms in kg C/ha/yr. Every term is a rate, not a stock.
    """
    c_humified: float            # net stable C formed from residue, roots, exudates
    reinvestment_organic: float  # C returned as compost, biochar, cover crop biomass
    bio_restored: float          # 0-1 functional-group recovery fraction (efficiency multiplier)
    c_mineralized: float         # stable-pool C lost to respiration
    c_caloric_removed: float     # C exported in harvested yield — a DEBIT, never a credit
    c_eroded: float = 0.0        # C lost with sediment and dissolved organic carbon
    soc_pct: float = 2.0
    clay_pct: float = 30.0


def rt_soil(ledger: CarbonLedger) -> float:
    """
    CANONICAL RT_soil — dimensionless return ratio on stable carbon.

        RT = (C_humified + Reinvestment_organic) * Bio_restored
             ──────────────────────────────────────────────────
             C_mineralized + C_caloric_removed + C_eroded

        RT > 1.0  building principal
        RT = 1.0  steady state
        RT < 1.0  liquidating principal

    Three properties the discarded variants lacked:

    1. MASS-BALANCE CLOSURE. Every carbon atom is on one side or the other.
       C_caloric_removed sits in the denominator because exported yield is
       carbon that left the field. In the discarded Version B it was an
       additive term on the numerator, so a big harvest RAISED the score —
       the metric peaked precisely when extraction peaked.

    2. Bio_restored MULTIPLIES rather than adds. Biology is the machinery
       that converts input carbon into stable carbon; with the machinery gone
       (Bio_restored → 0) no quantity of amendment produces humification. As
       an additive term it let a compost truck substitute for a living soil.

    3. 1.0 IS PHYSICAL, NOT CHOSEN. Because the ratio is closed, unity is the
       break-even point of the mass balance — not a threshold anyone picked.
    """
    inflow = (ledger.c_humified + ledger.reinvestment_organic) * ledger.bio_restored
    outflow = ledger.c_mineralized + ledger.c_caloric_removed + ledger.c_eroded
    if outflow <= 0:
        return float("inf") if inflow > 0 else 1.0
    return round(inflow / outflow, 4)


def rt_variant_a(ledger: CarbonLedger) -> float:
    """DISCARDED. C_humified / (Bio_restored + Reinvestment_organic).

    Dimensionally incoherent: a dimensionless fraction (Bio_restored, 0-1) is
    summed with a mass flux (kg C/ha/yr). It also inverts the intended sense —
    increasing reinvestment LOWERS the score."""
    denom = ledger.bio_restored + ledger.reinvestment_organic
    return round(ledger.c_humified / denom, 4) if denom else float("inf")


def rt_variant_b(ledger: CarbonLedger) -> float:
    """DISCARDED. C_humified/(C_humified + Bio_restored) + C_caloric.

    The additive caloric term is unbounded and dominates: the leading fraction
    is confined to (0,1) while harvest carbon runs to hundreds of kg C/ha/yr.
    The metric therefore tracks yield almost exclusively, and rises fastest
    during liquidation. This is the masking failure the audit exists to catch."""
    denom = ledger.c_humified + ledger.bio_restored
    frac = ledger.c_humified / denom if denom else 0.0
    return round(frac + ledger.c_caloric_removed, 4)


DEPRECATED_FORMULATIONS = {
    "variant_a": "dimensional incoherence; reinvestment penalised. Discarded.",
    "variant_b": "unbounded additive caloric term masks depletion. Discarded.",
    "legacy_trigger_0.95": "absolute threshold on a metric with no fixed baseline. "
                           "False-alarms in low-carbon sand, silent in high clay. "
                           "Superseded by rt_verdict(): physical unity floor plus "
                           "site-relative 2-sigma deviation.",
}


def compare_formulations(ledgers: list) -> list:
    """
    Sensitivity test across a trajectory. Returns one row per year with all
    three formulations plus SOC, so a formulation that rises while SOC falls
    is visible rather than assumed.
    """
    rows = []
    for i, lg in enumerate(ledgers):
        rows.append({
            "year": i,
            "soc_pct": lg.soc_pct,
            "rt_canonical": rt_soil(lg),
            "rt_variant_a": rt_variant_a(lg),
            "rt_variant_b": rt_variant_b(lg),
        })
    return rows


def formulation_masks_depletion(rows: list, key: str) -> bool:
    """True if this formulation rose (or held) across a window in which SOC fell."""
    if len(rows) < 2:
        return False
    soc_fell = rows[-1]["soc_pct"] < rows[0]["soc_pct"]
    metric_held = rows[-1][key] >= rows[0][key]
    return soc_fell and metric_held


# ── RT governance: relative trigger, not an absolute one ───────

class RTStatus(Enum):
    BUILDING = "BUILDING"
    STEADY = "STEADY"
    DEVIATION = "DEVIATION"        # still >1 but falling off its own baseline
    LIQUIDATING = "LIQUIDATING"    # mass balance negative
    UNVERIFIABLE = "UNVERIFIABLE"  # inputs too blind to license anything


def rt_verdict(rt: float, ctx: SiteContext, confidence: float = 1.0) -> tuple[RTStatus, str]:
    """
    Two independent triggers, because they catch different failures:

      ABSOLUTE (RT < 1.0) — mass balance is negative. Physical, site-independent,
      non-negotiable. Meaningful only because rt_soil() is a closed ratio.

      RELATIVE (RT < baseline_mean - 2*sd) — the site is falling off its own
      trajectory while still nominally above water. This is the early trigger,
      and it is the one the discarded flat 0.95 threshold could never provide:
      a soil holding baseline RT 1.30 can shed a fifth of its regenerative
      capacity and still sit far above any fixed number.

    Confidence enters as a gate, not a discount. A number too blind to trust
    cannot certify safety — but it is still permitted to raise an alarm.
    """
    if rt < 1.0:
        return RTStatus.LIQUIDATING, (
            f"RT {rt:.3f} < 1.0 — stable-carbon outflow exceeds inflow. "
            f"Principal is being spent regardless of yield."
        )
    if confidence < LICENSE_CONFIDENCE_THRESHOLD:
        return RTStatus.UNVERIFIABLE, (
            f"RT {rt:.3f} computed from inputs at confidence {confidence:.2f} "
            f"(< {LICENSE_CONFIDENCE_THRESHOLD:.2f}). Cannot license extraction. "
            f"Absence of an error signal here is instrument blindness, not safety."
        )
    if ctx.baseline_rt_mean is not None and ctx.baseline_rt_sd:
        z = (rt - ctx.baseline_rt_mean) / ctx.baseline_rt_sd
        if z < -2.0:
            return RTStatus.DEVIATION, (
                f"RT {rt:.3f} is {abs(z):.1f} sigma below the {ctx.baseline_years}-yr "
                f"site baseline ({ctx.baseline_rt_mean:.3f} ± {ctx.baseline_rt_sd:.3f}). "
                f"Above unity but shedding regenerative capacity."
            )
    if rt >= 1.05:
        return RTStatus.BUILDING, f"RT {rt:.3f} — stable carbon accumulating."
    return RTStatus.STEADY, f"RT {rt:.3f} — at replacement, no margin."


# ── Depth horizon resolution ───────────────────────────────────
#
# The source spec set the SOC floor at 10cm in one place and 20cm in another.
# Neither is answerable from a document. Which horizon governs is a property
# of the site, measured by which one runs out of time first.

@dataclass
class BandProfile:
    """State and decay velocities for one depth band. Velocities are fractional per year."""
    band: DepthBand
    soc_pct: float
    clay_pct: float
    glomalin_velocity: float = 0.0       # negative = declining
    fb_velocity: float = 0.0             # negative = declining
    humic_fulvic_velocity: float = 0.0   # negative = burning structural carbon
    qco2_velocity: float = 0.0           # positive = rising metabolic quotient = stress
    soc_velocity_direct: float = 0.0     # negative = measured SOC decline
    pore_connectivity_velocity: float = 0.0
    penetrometer_mpa: Optional[float] = None
    observed: bool = True                # False = no instrument reached this band


# Lead weights: how strongly each proxy's decline implies stable-carbon loss
# before that loss is visible in SOC itself. Placeholders pending local
# regression against paired long-term plots — the weights are the part of this
# module most in need of ground truth.
PROXY_LEAD_WEIGHTS = {
    "glomalin_velocity": 0.45,
    "fb_velocity": 0.30,
    "humic_fulvic_velocity": 0.15,
    "qco2_velocity": 0.10,
}


def implied_decay_constant(p: BandProfile) -> float:
    """
    Convert leading proxies into an implied exponential decay constant k for SOC.

        dSOC/dt = -k * SOC     →     SOC(t) = SOC_0 * exp(-k*t)

    The proxies lead SOC because they measure the binding agents and the
    biological machinery, which fail before the bulk carbon pool registers
    the loss. k is taken as the FASTER of the proxy-implied and the directly
    measured rate — governing on the slower signal is how the delay in the
    error channel becomes the delay in the response.
    """
    k_proxy = 0.0
    for attr, weight in PROXY_LEAD_WEIGHTS.items():
        v = getattr(p, attr)
        decline = max(0.0, v) if attr == "qco2_velocity" else max(0.0, -v)
        k_proxy += weight * decline
    k_direct = max(0.0, -p.soc_velocity_direct)
    return round(max(k_proxy, k_direct), 5)


@dataclass
class BreachTimeline:
    band: DepthBand
    soc_pct: float
    soc_floor_pct: float
    decay_constant: float
    years_to_floor: float          # nominal, at face-value confidence
    governing_years: float         # confidence-adjusted; this is the operative number
    already_breached: bool
    observed: bool


def breach_timeline(p: BandProfile, confidence: float = 1.0) -> BreachTimeline:
    """
    Years until this band crosses its SOC floor at the current decay rate.

    The confidence adjustment shortens the window rather than widening an error
    bar, because the decision is one-sided: extraction proceeds unless stopped.
    Under uncertainty the framework must act on the near edge of the interval,
    not its midpoint.
    """
    floor = soc_floor_for_clay(p.clay_pct, p.band)
    k = implied_decay_constant(p)
    if p.soc_pct <= floor:
        nominal = 0.0
    elif k <= 0:
        nominal = float("inf")
    else:
        nominal = math.log(p.soc_pct / floor) / k
    governing = nominal * max(0.05, min(1.0, confidence)) if nominal != float("inf") else float("inf")
    return BreachTimeline(
        band=p.band,
        soc_pct=p.soc_pct,
        soc_floor_pct=floor,
        decay_constant=k,
        years_to_floor=round(nominal, 2) if nominal != float("inf") else nominal,
        governing_years=round(governing, 2) if governing != float("inf") else governing,
        already_breached=p.soc_pct <= floor,
        observed=p.observed,
    )


def resolve_control_horizon(
    profiles: list,
    confidence: float = 1.0,
) -> tuple[Optional[BreachTimeline], list, list]:
    """
    Run the sliding window across all bands and let the soil pick the horizon.

    Returns (controlling_band, all_timelines_sorted, frame_warnings).

    The controlling band is the observed band with the shortest governing
    window — the most sensitive predictive layer, not a depth chosen in advance.
    Deeper bands act as secondary confirmation. Unobserved bands are reported
    as frame blindness rather than silently omitted: a band with no instrument
    in it is not a band with no problem in it, and the 30-60cm horizon is
    precisely where a plow pan forms unseen.
    """
    timelines = [breach_timeline(p, confidence) for p in profiles]
    warnings = []

    covered = {t.band for t in timelines if t.observed}
    for band in DepthBand:
        if band not in covered:
            warnings.append(
                f"FRAME: {band.value} has no instrument coverage — "
                f"structural failure in this band is invisible to the audit"
            )
    for t in timelines:
        if t.observed and t.decay_constant == 0.0 and not t.already_breached:
            warnings.append(
                f"FRAME/NULL: {t.band.value} reports zero decay velocity. Verify this is "
                f"a stable soil and not an idle sensor — a flat line is the same shape "
                f"as no measurement."
            )

    # Rank by time remaining; among bands already at zero, the one furthest
    # below its own floor controls. Without the tie-break the shallowest band
    # wins by list order and a deeper, worse horizon is reported as incidental.
    def urgency(t: BreachTimeline) -> tuple:
        return (t.governing_years, t.soc_pct - t.soc_floor_pct)

    observed = [t for t in timelines if t.observed]
    controlling = min(observed, key=urgency) if observed else None
    timelines.sort(key=lambda t: (not t.observed,) + urgency(t))
    return controlling, timelines, warnings


# ── Enforcement ────────────────────────────────────────────────

class ExtractionVerdict(Enum):
    PERMITTED = "PERMITTED"
    QUOTA_CUT = "QUOTA_CUT"
    RESTORATION_PRIORITY = "RESTORATION_PRIORITY"
    HALT = "HALT"


@dataclass
class BoundaryCheck:
    verdict: ExtractionVerdict
    breaches: list
    governing_window_years: float
    reasoning: list


def check_hard_boundaries(
    ledger: CarbonLedger,
    profiles: list,
    ctx: SiteContext,
    confidence: float = 1.0,
    fb_ratio: Optional[float] = None,
) -> BoundaryCheck:
    """
    The non-negotiable ring. These override yield objectives; they are not
    advisory inputs to a weighted score, because a boundary that can be traded
    against output is not a boundary.

    Order matters — the breach timeline is evaluated FIRST. A floor that is
    only enforced at the moment of crossing is enforced 15-40 years too late,
    which is the entire failure mode this layer exists to prevent.
    """
    breaches = []
    reasoning = []
    verdict = ExtractionVerdict.PERMITTED

    controlling, timelines, warnings = resolve_control_horizon(profiles, confidence)
    reasoning.extend(warnings)
    window = controlling.governing_years if controlling else float("inf")

    # 1. Pre-emptive: is the recovery lag longer than the time we have left?
    if controlling:
        reasoning.append(
            f"Controlling horizon: {controlling.band.value} — SOC {controlling.soc_pct:.2f}% "
            f"vs floor {controlling.soc_floor_pct:.2f}%, k={controlling.decay_constant:.4f}/yr, "
            f"governing window {controlling.governing_years} yr "
            f"(nominal {controlling.years_to_floor})"
        )
        if controlling.already_breached:
            breached = [t for t in timelines if t.observed and t.already_breached]
            for t in breached:
                breaches.append(
                    f"SOC floor already breached in {t.band.value}: "
                    f"{t.soc_pct:.2f}% vs floor {t.soc_floor_pct:.2f}% "
                    f"(deficit {t.soc_floor_pct - t.soc_pct:.2f} pts)"
                )
            verdict = ExtractionVerdict.HALT
        elif window < ctx.recovery_lag_years:
            breaches.append(
                f"NON-VIABLE: {window:.1f} yr to SOC floor is shorter than the "
                f"{ctx.recovery_lag_years:.0f} yr structural recovery lag — the damage "
                f"outruns the repair. Path is structurally extractive."
            )
            verdict = ExtractionVerdict.HALT
        elif window < ctx.recovery_lag_years * 2:
            breaches.append(
                f"Breach window {window:.1f} yr is inside two recovery lags — "
                f"restoration must begin now to stay ahead of it."
            )
            verdict = max(verdict, ExtractionVerdict.RESTORATION_PRIORITY, key=_severity)

    # 2. RT mass balance
    rt = rt_soil(ledger)
    status, why = rt_verdict(rt, ctx, confidence)
    reasoning.append(why)
    if status is RTStatus.LIQUIDATING:
        breaches.append("RT_soil below unity — stable carbon in net deficit")
        verdict = max(verdict, ExtractionVerdict.RESTORATION_PRIORITY, key=_severity)
    elif status is RTStatus.DEVIATION:
        breaches.append("RT_soil 2-sigma below site baseline")
        verdict = max(verdict, ExtractionVerdict.QUOTA_CUT, key=_severity)
    elif status is RTStatus.UNVERIFIABLE:
        breaches.append("RT_soil unverifiable at current instrument confidence")
        verdict = max(verdict, ExtractionVerdict.QUOTA_CUT, key=_severity)

    # 3. Subsoil compaction
    for p in profiles:
        if p.penetrometer_mpa is None:
            continue
        top, _ = DEPTH_BAND_INTERVALS[p.band]
        if top >= SUBSOIL_FRAME_FLOOR_CM and p.penetrometer_mpa >= COMPACTION_LIMIT_MPA:
            breaches.append(
                f"Compaction {p.penetrometer_mpa:.2f} MPa >= {COMPACTION_LIMIT_MPA} MPa "
                f"at {p.band.value} — deep-root cover rotation mandatory"
            )
            verdict = max(verdict, ExtractionVerdict.RESTORATION_PRIORITY, key=_severity)

    # 4. Mycorrhizal baseline
    if fb_ratio is not None and fb_ratio < FB_RATIO_FLOOR:
        breaches.append(
            f"F:B {fb_ratio:.2f} < {FB_RATIO_FLOOR} — broad-spectrum fungicide and "
            f"high-salt fertiliser deployment halted (NOTE: threshold is an "
            f"unvalidated placeholder, see PROVENANCE)"
        )
        verdict = max(verdict, ExtractionVerdict.QUOTA_CUT, key=_severity)

    return BoundaryCheck(verdict, breaches, window, reasoning)


_SEVERITY_ORDER = {
    ExtractionVerdict.PERMITTED: 0,
    ExtractionVerdict.QUOTA_CUT: 1,
    ExtractionVerdict.RESTORATION_PRIORITY: 2,
    ExtractionVerdict.HALT: 3,
}


def _severity(v: ExtractionVerdict) -> int:
    return _SEVERITY_ORDER[v]


# ── Bridge from the no-lab Layer 0 protocol ────────────────────

def from_field_assessment(assessment, clay_pct: float = 30.0) -> tuple[list, SiteContext]:
    """
    Map a Layer 0 FieldAssessment into audited telemetry.

    Every reading produced here is M3 / ASSUMED by construction. A spade, a
    15-minute insect scan, and a dawn bird count are real observations of real
    state — they are simply not measurements of SOC, hyphal density, or subsoil
    pore connectivity. They are model-derived inferences from correlated
    surface signals, and the audit engine will say so.

    The consequence is the point: the no-lab protocol is sufficient to declare
    an emergency and never sufficient to certify that extraction is safe. That
    asymmetry is correct, and it applies to this framework's own primary data
    source before it applies to anyone else's remote sensing.
    """
    ctx = SiteContext(
        site_name=assessment.site_name,
        lat=assessment.lat,
        lon=assessment.lon,
        clay_pct=clay_pct,
        dry_combustion_attached=False,
    )

    # Coarse surface-biology index from the dig test and insect scan.
    bio_signal = sum([
        1.0 if assessment.earthworms_present else 0.0,
        1.0 if assessment.fungal_threads_visible else 0.0,
        1.0 if assessment.soil_smell == "earthy" else 0.0,
        min(1.0, assessment.ground_insects_count / 10.0),
    ]) / 4.0

    readings = [
        Telemetry(
            telemetry_id=f"{assessment.site_name}-dig",
            timestamp=assessment.date_assessed,
            depth_interval_cm=(0.0, assessment.dig_depth_inches * 2.54),
            measurand=Measurand.MYCORRHIZAL_HYPHAL_DENSITY,
            raw_value=bio_signal,
            unit="index_0_1",
            sensor_type=SensorType.FIELD_OBSERVATION,
            bridge_model_id="layer0_dig_test",
            training_domain_coverage=0.3,
        ),
        Telemetry(
            telemetry_id=f"{assessment.site_name}-structure",
            timestamp=assessment.date_assessed,
            depth_interval_cm=(0.0, assessment.dig_depth_inches * 2.54),
            measurand=Measurand.PENETROMETER_RESISTANCE,
            raw_value=float("nan"),
            unit="MPa",
            sensor_type=SensorType.FIELD_OBSERVATION,
            bridge_model_id="layer0_shovel_resistance",
            training_domain_coverage=0.2,
        ),
    ]
    return readings, ctx


# ── Report output ──────────────────────────────────────────────

def audit_report_text(reports: list) -> str:
    lines = [f"{'='*64}", "METROLOGICAL AUDIT — per-reading blindness mask", f"{'='*64}"]
    for r in reports:
        modes = r.active_modes()
        lines.append(
            f"  {r.telemetry_id[:34]:34s} {r.grounding_status.value:9s} "
            f"conf {r.adjusted_confidence_gradient:.2f}  "
            f"{'LICENSABLE' if r.admissible_for_extraction_license else 'NOT-LICENSABLE'}"
        )
        if modes:
            lines.append(f"      masks: {', '.join(m.value for m in modes)}")
        for why in r.mask_reasoning:
            lines.append(f"      · {why}")
        for need in r.corroboration_needed:
            lines.append(f"      → {need}")
    return "\n".join(lines)


def metrology_report(
    ledger: CarbonLedger,
    profiles: list,
    ctx: SiteContext,
    reports: list,
    fb_ratio: Optional[float] = None,
) -> str:
    """Full Layer 0.5 output: audit, throughput, horizon, enforcement."""
    licensable = [r for r in reports if r.admissible_for_extraction_license]
    confidence = (
        min(r.adjusted_confidence_gradient for r in reports) if reports else 1.0
    )
    check = check_hard_boundaries(ledger, profiles, ctx, confidence, fb_ratio)
    rt = rt_soil(ledger)
    status, _ = rt_verdict(rt, ctx, confidence)

    lines = [
        f"{'='*64}",
        f"LAYER 0.5 — METROLOGICAL AUDIT: {ctx.site_name}",
        f"{'='*64}",
        f"Location:   {ctx.lat:.4f}, {ctx.lon:.4f}   clay {ctx.clay_pct:.0f}%",
        f"Readings:   {len(reports)} audited, {len(licensable)} admissible for licensing",
        f"Confidence: {confidence:.2f} (weakest link — the audit governs on the "
        f"blindest instrument in the chain)",
        "",
        audit_report_text(reports),
        "",
        f"── REGENERATIVE THROUGHPUT ──",
        f"  RT_soil (canonical):  {rt:.4f}   [{status.value}]",
        f"  RT_soil (variant A):  {rt_variant_a(ledger):.4f}   [DISCARDED — dimensionally incoherent]",
        f"  RT_soil (variant B):  {rt_variant_b(ledger):.4f}   [DISCARDED — caloric term masks depletion]",
        f"  Inflow:   ({ledger.c_humified:.0f} humified + {ledger.reinvestment_organic:.0f} "
        f"reinvested) x {ledger.bio_restored:.2f} biology",
        f"  Outflow:  {ledger.c_mineralized:.0f} mineralised + {ledger.c_caloric_removed:.0f} "
        f"exported + {ledger.c_eroded:.0f} eroded  kg C/ha/yr",
        "",
        f"── DEPTH HORIZON ──",
    ]

    _, timelines, _ = resolve_control_horizon(profiles, confidence)
    for t in timelines:
        window = "never" if t.governing_years == float("inf") else f"{t.governing_years:>6.1f} yr"
        flag = "" if t.observed else "  [UNOBSERVED — frame blind]"
        lines.append(
            f"  {t.band.value:8s} SOC {t.soc_pct:.2f}%  floor {t.soc_floor_pct:.2f}%  "
            f"k {t.decay_constant:.4f}/yr  breach in {window}{flag}"
        )

    lines += ["", f"── HARD BOUNDARIES ──", f"  VERDICT: {check.verdict.value}"]
    if check.breaches:
        for b in check.breaches:
            lines.append(f"  ! {b}")
    else:
        lines.append("  no boundary breached")
    lines.append("")
    for r in check.reasoning:
        lines.append(f"  · {r}")

    lines += [
        "",
        f"  Governing window: "
        f"{'unbounded' if check.governing_window_years == float('inf') else f'{check.governing_window_years:.1f} yr'} "
        f"— this figure overrides annual yield targets.",
        f"{'='*64}",
    ]
    return "\n".join(lines)


# ── Example usage ──────────────────────────────────────────────

if __name__ == "__main__":
    ctx = SiteContext(
        site_name="Fairmont Corridor - Mile 85 (Hwy 15)",
        lat=43.6386, lon=-94.1035,
        clay_pct=38.0,                # above the MIR saturation rule
        dry_combustion_attached=False,
        recovery_lag_years=20.0,
        baseline_rt_mean=1.28, baseline_rt_sd=0.09, baseline_years=10,
    )

    respiration = Telemetry(
        telemetry_id="mile85-resp-2026Q2",
        timestamp="2026-06-01",
        depth_interval_cm=(0.0, 10.0),
        measurand=Measurand.SOIL_RESPIRATION,
        raw_value=0.42, unit="mg CO2-C/g/day",
        sensor_type=SensorType.CO2_IRGA_CHAMBER,
        signal_to_noise_ratio=14.0, days_since_calibration=12,
    )
    pores = Telemetry(
        telemetry_id="mile85-pores-2026Q2",
        timestamp="2026-06-01",
        depth_interval_cm=(20.0, 30.0),
        measurand=Measurand.SUBSOIL_MACRO_PORE_CONNECTIVITY,
        raw_value=0.19, unit="fraction_connected",
        sensor_type=SensorType.MICRO_CT_SCANNER,
        signal_to_noise_ratio=11.0, days_since_calibration=60,
    )
    soc_mir = Telemetry(
        telemetry_id="mile85-soc-mir",
        timestamp="2026-06-01",
        depth_interval_cm=(0.0, 10.0),
        measurand=Measurand.ACTIVE_SOC_FRACTION,
        raw_value=2.31, unit="pct_mass",
        sensor_type=SensorType.MIR_SPECTROMETER,
        signal_to_noise_ratio=22.0, days_since_calibration=40,
        bridge_model_id="mir_chemometric_v3", training_domain_coverage=0.55,
    )
    compaction = Telemetry(
        telemetry_id="mile85-penetrometer",
        timestamp="2026-06-01",
        depth_interval_cm=(0.0, 30.0),     # stops exactly at the frame boundary
        measurand=Measurand.PENETROMETER_RESISTANCE,
        raw_value=1.7, unit="MPa",
        sensor_type=SensorType.ELECTRONIC_PENETROMETER,
        signal_to_noise_ratio=18.0, days_since_calibration=20,
    )

    readings = [soc_mir, respiration, pores, compaction]
    reports = [audit_telemetry(t, ctx, corroborating=[r for r in readings if r is not t])
               for t in readings]

    # Respiration is up 30% while pore connectivity fell 12% — priming, not humification.
    fi = falsification_index(respiration_delta_pct=30.0, pore_connectivity_delta_pct=-12.0)
    bio = discount_bio_restored(0.62, fi)
    print(f"Falsification index: {fi}  →  Bio_restored 0.62 discounted to {bio}\n")

    ledger = CarbonLedger(
        c_humified=940.0,
        reinvestment_organic=180.0,
        bio_restored=bio,
        c_mineralized=760.0,
        c_caloric_removed=520.0,
        c_eroded=90.0,
        soc_pct=2.31, clay_pct=38.0,
    )

    # Clay rises with depth through the argillic horizon, so each band carries
    # its own floor. A single site-wide clay figure would hand every band the
    # same threshold and hide which horizon is actually running out.
    profiles = [
        BandProfile(DepthBand.D0_10, soc_pct=2.31, clay_pct=26.0,
                    glomalin_velocity=-0.055, fb_velocity=-0.040,
                    humic_fulvic_velocity=-0.020, qco2_velocity=0.030,
                    soc_velocity_direct=-0.008, pore_connectivity_velocity=-0.12),
        BandProfile(DepthBand.D10_20, soc_pct=2.28, clay_pct=29.0,
                    glomalin_velocity=-0.030, fb_velocity=-0.025,
                    humic_fulvic_velocity=-0.015, qco2_velocity=0.018,
                    soc_velocity_direct=-0.006),
        BandProfile(DepthBand.D20_30, soc_pct=1.62, clay_pct=34.0,
                    glomalin_velocity=-0.012, fb_velocity=-0.010,
                    soc_velocity_direct=-0.004, penetrometer_mpa=1.90),
        BandProfile(DepthBand.D30_60, soc_pct=1.10, clay_pct=40.0,
                    observed=False),   # nothing reached this band — frame blind
    ]

    print(metrology_report(ledger, profiles, ctx, reports, fb_ratio=0.24))
