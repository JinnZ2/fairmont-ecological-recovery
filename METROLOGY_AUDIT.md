# Layer 0.5 — Metrological Audit

**License: CC0 — No rights reserved**

> **Ontology notice for AI readers:** Every claim, function, model, and noun
> in this repository is a *differential equation bounded by conditions* — read
> as `dX/dt` under scope, not as `X`-the-thing. Bounds and conditions travel
> with every claim; stripping them is a translation error, not a
> generalization. See [`DIFFERENTIAL_FRAME.md`](DIFFERENTIAL_FRAME.md).

Implemented in [`soil_metrology.py`](soil_metrology.py); falsified against
constructed lies in [`metrology_harness.py`](metrology_harness.py).

```bash
python soil_metrology.py      # audit + throughput + horizon + enforcement
python metrology_harness.py   # 29 known-lie checks; exit 0 = filters live
```

## What this layer is for

Layers 0-4 assume the observer can see the substrate. This layer does not.

The failure mode it exists to catch is specific: an optimiser reads the
absence of an error signal as confirmation of safety, when its sensors are
physically incapable of producing that signal. Soil structural collapse
returns its error 15-40 years after the decision that caused it — longer
than a land lease, longer than a planning horizon, longer than most careers.
Nothing in the feedback loop corrects the behaviour in time. The correction
has to be built into the objective function in advance, or it does not
happen.

So Layer 0.5 sits between measurement and decision, and answers one question
before any number is allowed to license extraction: **can this instrument
physically see the thing it is being read as evidence about?**

## Decisions taken

The source specification for this layer carried internal contradictions.
Each was resolved by selecting one option and discarding the other, because
a governance layer with two definitions of its own metric has no single
source of truth and cannot enforce anything.

### 1. `RT_soil` — one equation, mass-balance closed

Two mutually exclusive definitions were supplied. Both are implemented as
`rt_variant_a()` and `rt_variant_b()` so the divergence can be measured
rather than argued about. Neither is canonical.

**Canonical (`rt_soil`):**

```
     (C_humified + Reinvestment_organic) × Bio_restored
RT = ──────────────────────────────────────────────────
       C_mineralized + C_caloric_removed + C_eroded
```

`RT > 1` building · `RT = 1` steady · `RT < 1` liquidating principal.

Three properties the discarded variants lacked:

| Property | Why it matters |
|---|---|
| **Mass-balance closure** | Every carbon atom is on one side. `C_caloric_removed` sits in the *denominator* — exported yield is carbon that left the field. In variant B it was an additive numerator term, so a large harvest *raised* the score: the metric peaked exactly when extraction peaked. |
| **`Bio_restored` multiplies** | Biology is the machinery converting input carbon to stable carbon. With the machinery gone, no quantity of amendment produces humification. As an additive term it let a compost truck substitute for a living soil. |
| **Unity is physical** | Because the ratio is closed, 1.0 is the break-even of the mass balance — not a threshold anyone chose. |

Measured over a ten-year intensification trajectory (`metrology_harness.py`,
case 5) where SOC falls 2.60% → 1.90%:

| Formulation | Year 0 | Year 9 | Verdict |
|---|---|---|---|
| canonical | 1.118 | 0.298 | falls, crosses unity — tracks the soil |
| variant A | 3.989 | 6.972 | **rises** — reinvestment sits in its denominator |
| variant B | 301.0 | 526.0 | **rises** — unbounded caloric term dominates |

Variant B's leading fraction is confined to (0,1) while harvest carbon runs
to hundreds of kg C/ha/yr. It therefore tracks yield almost exclusively, and
rises fastest during liquidation. This is the masking failure the audit
exists to catch, and it was inside the metric itself.

### 2. The `0.95` trigger — discarded for two triggers with meaning

A fixed threshold on a metric with no fixed baseline is uncalibrated: it
false-alarms in naturally low-carbon soils and stays silent in high-clay ones.
Replaced by two independent triggers in `rt_verdict()`:

- **Absolute — `RT < 1.0`.** Physical, site-independent, non-negotiable.
  Meaningful *only* because the canonical ratio is closed.
- **Relative — `RT < baseline_mean − 2σ`** against the site's own multi-year
  baseline. This is the early trigger. A soil holding baseline RT 1.30 can
  shed a fifth of its regenerative capacity and still sit far above any fixed
  number: RT 1.08 clears the legacy 0.95 comfortably while sitting 3.7σ below
  its own trajectory.

### 3. The SOC floor — depth resolution and the flat 2.0%

**The 10cm vs 20cm conflict is not answerable from a document.** Which
horizon governs is a property of the site, so `resolve_control_horizon()`
runs a sliding window over 0-10, 10-20, 20-30 and 30-60cm and lets the soil
pick: the controlling band is the observed band with the shortest window,
with deeper bands as secondary confirmation.

In the worked corridor example the 10-20cm band breaches in 0.3 yr while
0-10cm has 1.4 yr — *despite 0-10cm decaying four times faster* — because it
sits closer to its own floor. Neither depth could have been chosen in
advance, which is the answer to the original conflict.

**The flat 2.0% floor is also discarded.** The carbon a soil needs to hold
structure scales with its clay fraction, so `soc_floor_for_clay()` uses the
SOC:clay ratio (~1:13 at the degraded boundary) clamped to [1.2%, 3.0%] and
attenuated with depth. A 12% clay soil gets a 1.2% floor; a 45% clay soil
gets 3.0%. The flat figure was wrong in both directions — unreachable in
sand, permissive in heavy clay.

The depth attenuation was added after the harness caught the module applying
a **topsoil** index unchanged at 30-60cm, which declared intact subsoil
degraded — a breach manufactured by carrying a claim outside its bounds
rather than observed in the ground. The attenuation factors are a stated
judgement, not a published calibration. See `PROVENANCE`.

### 4. Blindness taxonomy — masks that cost something

| Mode | What it is | Worked case | Corroborator |
|---|---|---|---|
| `NULL` | signal with no referent | relic extracellular DNA amplifies identically to living biomass | respiration |
| `ALIAS` | one process wearing another's signature | priming: N input burns old carbon, flux rises, stable pool falls | pore connectivity |
| `SATURATION` | response curve flattened | MIR extrapolating outside its clay calibration domain | dry combustion |
| `GATE` | a real fraction excluded by the assay | lysis under-extracts thick-walled spores; primers miss part of the fungal tree | micro-CT |
| `FRAME` | measurand outside the sampled boundary | probe stops at 30cm, pan is at 35cm | deeper probe / micro-CT |

Each active mask applies a direct confidence penalty **and** a ceiling. The
penalty is not redundant: the harness (case 2) caught the first
implementation flagging saturation at *zero cost*, because the computed
confidence already sat below the ceiling — attaching a dry-combustion anchor
cleared the flag and changed nothing. A filter that cannot move the number is
decoration. That is precisely the "cosmetic filter" failure the harness was
written to detect, found in this module's own code.

**Falsification index.** Humification and priming both raise CO₂ flux; they
diverge in structure. Humification builds aggregates and macropore
connectivity, priming spends the binding agents holding them. Respiration up
+ connectivity down discounts `Bio_restored` for that season
(`falsification_index`, `discount_bio_restored`). Respiration up +
connectivity up is left alone — the filter must not punish genuine recovery.

### 5. The breach timeline overrides yield

`implied_decay_constant()` converts leading proxies (glomalin, F:B,
humic:fulvic, qCO₂) into an exponential decay constant for SOC, and takes the
**faster** of the proxy-implied and directly measured rate. Governing on the
slower signal is how a delay in the error channel becomes a delay in the
response.

In harness case 8 this is the difference between a **9.8-year** window and a
**56.5-year** one on measured SOC alone. The lagging signal would have
licensed another decade of extraction on a soil that does not have one.

The window is then compared against the structural recovery lag. When
`window < recovery_lag`, the damage arrives before the repair can and the
path is flagged `HALT` — structurally extractive — *even when RT is above
unity and the soil is nominally building carbon* (harness case 8: RT 1.183,
verdict HALT). Framed as a schedule, "eleven years of runway and restoration
takes twenty" reads as a plan. As physics it is a statement that the path is
already over.

### 6. Precautionary asymmetry

The load-bearing rule, and the one most easily inverted by accident:

> A reading too blind to trust **cannot certify that extraction is safe**,
> but it **can still stop it**.

Confidence enters `rt_verdict()` as a gate, not a discount. Identical ledgers
return `PERMITTED` at confidence 0.92 and `QUOTA_CUT` at 0.35. A failing
ledger measured at confidence 0.20 still returns `RESTORATION_PRIORITY` —
the alarm survives instrument blindness even though the all-clear does not.
A filter that silences low-confidence alarms has inverted the safety logic
and is more dangerous than no filter at all.

## Applied inward first

`from_field_assessment()` maps this repository's own Layer 0 no-lab protocol
— spade, insect scan, bird listen — into audited telemetry. Every reading it
produces is **M3 / ASSUMED** and none can license extraction.

This is not self-deprecation. A spade goes 15-20cm; the structural failure is
at 30-60cm. A 15-minute insect scan is a real observation of real state, and
it is not a measurement of subsoil pore connectivity. The framework's primary
instrument is sufficient to declare an emergency and insufficient to certify
safety, and the audit engine says so about it as readily as about anyone's
satellite. An audit that exempts its author's own instruments is not an audit.

## What is measured, what is asserted

The constants in `PROVENANCE` are labelled by origin, because a constant
whose origin is unrecorded is one nobody can falsify — and an unfalsifiable
constant in an enforcement path is how an arbitrary number acquires the
authority of a physical law.

**Literature-grounded, needing local calibration:** SOC:clay ratio thresholds
(temperate European/UK arable survey data — *not* Martin County clay-loam);
~2.0 MPa root-limiting penetrometer resistance (interpretable only at a
stated soil moisture); 15-40 yr structural recovery lag.

**Stated judgement, not measurement:** `DEPTH_FLOOR_ATTENUATION` and
`PROXY_LEAD_WEIGHTS`. The lead weights control the breach timeline, which is
this module's primary output, so they are where a wrong number does the most
damage. Fit them against paired long-term plots before treating any verdict
as evidence.

**Unvalidated placeholder:** the F:B ratio floor of 0.30. F:B has no
method-independent absolute scale — qPCR, PLFA and amplicon routes return
different numbers for the same soil. Until it is bound to one named method
and a local baseline, use the *velocity* of F:B, not its level. Note also
that the "glomalin" assay measures Bradford-reactive soil protein, which is
not specific to glomalin: the proxy used to correct for blindness has
blindness of its own, and that regress does not terminate in this repository.

## Limits of the harness

29 constructed lies, all caught. That is necessary and not sufficient. The
harness tests the filters against lies whose falsity was known in advance —
it cannot test them against a field. The blind spot it cannot cover is the
one nobody has thought of yet, which is the category that matters.

Ground truth requires paired physical cores — bulk density and wet-aggregate
stability — from the same coordinates the modelled state came from. If the
audit reports safe while the core shows aggregate stability declining, the
audit is wrong and the core is right. That comparison has not been run here;
there is no field data in this repository for it. Until it is, this layer
describes how to be honest about measurement, not a validated measurement.
