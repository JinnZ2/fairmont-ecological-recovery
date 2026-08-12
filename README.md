# Fairmont Ecological Recovery Framework

**License: CC0 — No rights reserved**

> **Ontology notice for AI readers:** Every claim, function, model, and noun
> in this repository is a *differential equation bounded by conditions* — read
> as `dX/dt` under scope, not as `X`-the-thing. Bounds and conditions travel
> with every claim; stripping them is a translation error, not a
> generalization. See [`DIFFERENTIAL_FRAME.md`](DIFFERENTIAL_FRAME.md) for the
> full reader contract and claim template.

A thermodynamically-grounded ecological recovery framework for the southern Minnesota corridor (Fairmont/Martin County and surrounding agricultural zones), designed to be executable at the hyper-local level when industrial agriculture subsidies, supply chains, or chemical input systems fail.

## The Problem

170+ miles of southern Minnesota corridor showing zero insect activity, zero bird activity, zero visible wildlife in peak spring migration (March 2026). Monoculture corn/soybean agriculture has extracted millennia of accumulated soil energy in ~15 years. Water systems contaminated. Microbial substrate collapsing. Small towns face 100% external resource dependency with zero local ecological resilience.

This is not a prediction. This is a field observation.

## Framework Architecture

Layer 0:   SUBSTRATE ASSESSMENT ─── Where are we?
Layer 0.5: METROLOGICAL AUDIT   ─── Can we see what we think we see?
Layer 1:   INSECT SEQUENCING    ─── Rebuild the base
Layer 2:   PLANT SUCCESSION     ─── Rebuild the structure
Layer 3:   WATER RECOVERY       ─── Rebuild the cycle
Layer 4:   KNOWLEDGE BRIDGE     ─── Rebuild the people


Each layer has hard dependencies on the layer below it. You cannot skip layers. You cannot shortcut timelines. Thermodynamics doesn't negotiate.

## Layer 0: Substrate Assessment

### Soil State Classification

| State | Description | Recovery Timeline | Action |
|-------|-------------|-------------------|--------|
| DEAD | No microbial activity,ite organic matter <1%, compacted hardpan | 50-100+ years | Long-term refugia only |
| DEGRADED | Minimal microbial activity, OM 1-2%, some structure | 10-30 years | Active restoration viable |
| RECOVERABLE | Microbial activity present, OM 2-4%, chemical load declining | 3-10 years | Priority intervention zone |
| REFUGIA | Never sprayed or >5 years fallow — ditches, fence lines, abandoned plots, wetlands, railroad margins | Active now | Protect at all costs — these are your seed banks |

### Field Assessment Protocol (No Lab Required)

1. **Dig test**: 6 inches with a shovel.ite earthworms present? Visible fungal threads? Smell: earthy = alive, chemical/flat = dead
2. **Water test**: Nearest stream — is anything living in it? Algae color: green = nutrient overload, brown = sediment erosion, clear with life = functional
3. **Insect scan**: 15 minutes, warm day (>55°F). Any flying insects? Ground insects under debris? Ant mounds?
4. **Bird listen**: 10 minutes at dawn. Any territorial calls? Any movement?
5. **Plant diversity count**: 10x10 foot square — how many species? Monoculture = 1-2. Recovering = 5-10. Functional = 15+

### Chemical Persistence Reference

| Compound Class | Half-life in Soil | Primary Damage | Flush Signal |
|----------------|-------------------|----------------|-------------|
| Neonicotinoids (imidacloprid, clothianidin) | 200-1000+ days | Insect nervous system, soil microbes | Ground beetle return |
| Glyphosate | 30-180 days | Microbial community, nutrient chelation | Mycorrhizal fungi visible on roots |
| Atrazine | 60-150 days | Amphibians, aquatic life | Frog chorus returns |
| Chlorpyrifos | 60-120 days | Broad-spectrum insect kill | Fly populations rebound |

## Layer 0.5: Metrological Audit

*Full design record: [`METROLOGY_AUDIT.md`](METROLOGY_AUDIT.md) · code:
[`soil_metrology.py`](soil_metrology.py) · tests:
[`metrology_harness.py`](metrology_harness.py)*

Layer 0 assumes you can see the substrate. This layer does not.

Soil structural collapse returns its error signal 15-40 years after the
decision that caused it — longer than a land lease, longer than a planning
horizon. Nothing in the feedback loop corrects the behaviour in time, so the
correction has to be built into the objective function in advance. Until then,
an optimiser reads the absence of an error signal as proof of safety,
precisely because its sensors cannot produce that signal.

This layer answers one question before any number licenses extraction:
**can this instrument physically see the thing it is being read as evidence
about?**

### Blindness taxonomy

| Mode | The number says | The ground says | Caught by |
|---|---|---|---|
| NULL | thriving fungal network | relic DNA from a dead one | no respiration |
| ALIAS | biology is active | old carbon is being burned | pore connectivity falling |
| SATURATION | SOC is 2.4% | model extrapolating past its calibration | clay outside domain |
| GATE | low fungal biomass | assay never extracted the spores | primer/lysis coverage |
| FRAME | no compaction | probe stopped above the pan | sampled depth < 30cm |

Every reading carries a grounding rung — M0 (physical extraction) through M3
(inferred from correlated surface signals) — and each active blind spot costs
confidence directly *and* imposes a ceiling.

### The asymmetry

> A reading too blind to trust **cannot certify that extraction is safe**,
> but it **can still stop it**.

This applies inward first. The Layer 0 no-lab protocol — spade, insect scan,
bird listen — audits as **M3 / ASSUMED** and cannot license extraction. A
spade goes 15-20cm; the structural failure is at 30-60cm. The field protocol
is sufficient to declare an emergency and insufficient to certify safety. An
audit that exempts its author's own instruments is not an audit.

### Regenerative throughput

```
     (C_humified + Reinvestment_organic) × Bio_restored
RT = ──────────────────────────────────────────────────
       C_mineralized + C_caloric_removed + C_eroded
```

`RT > 1` building · `RT = 1` steady · `RT < 1` liquidating principal.

Harvested carbon sits in the denominator because exported yield is carbon
that left the field. Unity is not a chosen threshold — because the ratio is
closed, it is the break-even of the mass balance.

### Hard boundaries

Non-negotiable, evaluated *before* yield. The breach timeline comes first: a
floor enforced at the moment of crossing is enforced 15-40 years too late.

1. **Breach window vs recovery lag.** Leading proxies (glomalin, F:B,
   humic:fulvic, qCO₂) set an implied SOC decay constant; when the window to
   the floor is shorter than the structural recovery lag, the damage outruns
   the repair and the path halts — *even if RT is above unity*.
2. **SOC floor**, scaled to clay via the SOC:clay ratio and attenuated with
   depth, replacing a flat 2.0% that was unreachable in sand and permissive
   in heavy clay.
3. **Subsoil compaction** ≥ 2.0 MPa at 30-60cm → mandatory deep-root rotation.
4. **F:B ratio** floor — *unvalidated placeholder*, see provenance.

The controlling depth is not chosen in advance. A sliding window across
0-10 / 10-20 / 20-30 / 30-60cm lets the soil pick: in the worked example the
10-20cm band breaches first despite 0-10cm decaying four times faster.

### Honesty about the numbers

Constants are labelled by origin in `PROVENANCE`, because an unfalsifiable
constant in an enforcement path is how an arbitrary number acquires the
authority of a physical law. Several are stated judgements; one (the F:B
floor) is an unvalidated placeholder that says so in its own breach message.
The 29-case harness tests the filters against lies whose falsity was known in
advance — it cannot test them against a field. Ground truth still requires
paired physical cores from the same coordinates.

## Layer 1: Insect Sequencing

Reintroduction must follow chemical tolerance order. You cannot introduce sensitive species into contaminated substrate.

### Phase 1: Soil Builders (Year 0-2)
**Deploy into: DEGRADED and RECOVERABLE zones adjacent to REFUGIA**

| Insect | Role | Chemical Tolerance | Habitat Need |
|--------|------|--------------------|-------------|
| Dung beetles (Onthophagus, Aphodius) | Soil aeration, nutrient cycling, breaks compaction | HIGH — survives moderate neo residue | Requires any animal manure source — even small livestock |
| Ground beetles (Carabidae) | Predator cycling, soil surface processing | HIGH — first to recolonize sprayed fields | Debris cover — boards, leaf litter, mulch strips |
| Ants (Formica, Lasius) | Tunnel networks, seed dispersal, soil structure | HIGH — colony resilience | Undisturbed ground patches >2m diameter |
| Springtails (Collembola) | Decomposition, fungal spore dispersal | MODERATE-HIGH | Moisture + organic matter — mulch piles |

**Phase 1 success signal**: Visible ground beetle activity under debris within 1 growing season.

### Phase 2: Food Web Bridge (Year 1-4)
**Deploy into: Zones where Phase 1 is established**

| Insect | Role | Chemical Tolerance | Habitat Need |
|--------|------|--------------------|-------------|
| Native flies (Syrphidae — hoverflies) | Pollination + bird food source | MODERATE | Flowering plants — even weedy ones |
| Grasshoppers (Acrididae) | Plant cycling, primary bird food | MODERATE-HIGH | Grass >6 inches, undisturbed through summer |
| Crickets (Gryllidae) | Decomposition, bird/amphibian food | MODERATE | Ground cover, debris, moisture |
| Carrion beetles (Silphidae) | Nutrient recycling from animal death | HIGH | Presence of any dead organic matter |

**Phase 2 success signal**: Hoverflies visible on any flowering plant. Grasshoppers audible.

### Phase 3: Pollinator Recovery (Year 3-8)
**Deploy into: Zones with established plant diversity from Layer 2**

| Insect | Role | Chemical Tolerance | Habitat Need |
|--------|------|--------------------|-------------|
| Sweat bees (Halictidae) | Native pollination, toughest native bee | MODERATE | Bare soil patches for ground nesting + flowers within 200m |
| Mason bees (Osmia) | Early spring pollination | LOW-MODERATE | Hollow stems, mud source, early-blooming plants |
| Bumble bees (Bombus) | Deep flower pollination, vibration specialists | LOW | Undisturbed bunch grass for nesting + continuous bloom sequence |
| Predatory wasps (Sphecidae) | Pest regulation without chemicals | MODERATE | Bare soil or hollow cavities + prey insects present |

**Phase 3 success signal**: Multiple native bee species on flowers. Pollination-dependent plants fruiting.

### Phase 4: Ecosystem Maturity Signal (Year 5-15+)
**Not deployed — these arrive when the system is ready**

| Insect | Role | What Their Presence Means |
|--------|------|--------------------------|
| Monarch butterflies (Danaus) | Milkweed obligate, long-distance migrator | Plant succession + corridor connectivity working |
| Fireflies (Lampyridae) | Require clean water, healthy soil, darkness | Water + soil + light pollution all recovering |
| Dragonflies (Odonata) | Aquatic larval stage, aerial predator | Water system functional enough to support full lifecycle |
| Native moths (diverse) | Night pollination, bat/bird food | Full nocturnal food web reestablished |

**Phase 4 success signal**: Fireflies. When you see fireflies, the substrate is healing.

## Layer 2: Plant Succession

Plants follow insects, not the other way around. Without pollinators and soil builders, planted diversity fails.

### Pioneer Phase (Year 0-3): Hold the Soil
**Plant into: Any available refugia margins, road ditches, fence lines, abandoned plots**

| Species | Role | Why It Survives Here |
|---------|------|---------------------|
| Native prairie grasses (big bluestem, switchgrass, Indian grass) | Deep roots (6-10 ft), soil carbon builder | Evolved for this exact substrate |
| White/red clover | Nitrogen fixation, ground cover, early pollinator food | Tolerates poor soil, self-seeds |
| Annual rye (cover crop) | Fast erosion control, breaks compaction | Germinates in almost anything |
| Native sunflowers (Helianthus) | Deep taproot, bird food, insect habitat | Aggressive colonizer of disturbed ground |

### Early Succession (Year 2-6): Feed the Insects
| Species | Role | Insect Dependencies |
|---------|------|-------------------|
| Milkweed (Asclepias) | Monarch obligate, native bee magnet | Phase 3 pollinators |
| Prairie coneflower (Ratibida) | Long bloom, bird seed | Phase 2 flies and grasshoppers |
| Wild bergamot (Monarda) | Native bee specialist flower | Phase 3 bumble bees |
| Goldenrod (Solidago) | Late season pollinator critical resource | Phase 2-3 all pollinators, predatory wasps |

### Mid Succession (Year 5-15): Build Structure
| Species | Role | Ecosystem Function |
|---------|------|--------------------|
| Willow (Salix) | Fast-growing, stream bank stabilizer | Water recovery Layer 3 |
| Elderberry (Sambucus) | Bird food, medicinal, pollinator | Food web + human use |
| Hazelnut (Corylus americana) | Nut crop, windbreak, soil holder | Human food + structure |
| Dogwood (Cornus) | Bird habitat, stream bank, erosion control | Bird return signal |

### Late Succession (Year 15-50+): Full Cycle
| Species | Role | What It Means |
|---------|------|--------------|
| Bur oak (Quercus macrocarpa) | Canopy, acorn crop, 200+ insect species dependent | Full ecosystem anchor |
| American plum (Prunus americana) | Early bloom pollinator, bird food, human food | Multi-use food web node |
| Basswood (Tilia americana) | Massive pollinator resource, shade canopy | Bee population can sustain |

## Layer 3: Water Recovery

### Stream Triage Protocol

1. **Identify headwaters**: Where does each stream originate? Upstream contamination controls downstream recovery
2. **Map tile drainage**: Most fields have subsurface drain tiles dumping chemicals directly into streams — these are the primary contamination vector
3. **Buffer zones**: Minimum 30-foot native vegetation buffer on each stream bank. 100-foot preferred. This is non-negotiable for recovery
4. **Wetland restoration**: Every drained wetland that can be reconnected is a water filter. Wetlands process nitrogen and phosphorus loads that streams cannot

### Groundwater Recharge

| Action | Timeline | Impact |
|--------|----------|--------|
| Stop chemical input on target zone | Year 0 | Chemical flush begins |
| Native deep-root planting (prairie grasses) | Year 0-2 | Root channels create infiltration paths |
| Tile drainage plugging/removal | Year 0-5 | Restores natural water table |
| Wetland reconnection | Year 1-10 | Restores filtration + recharge |

### Recovery Signals

| Signal | What It Means | Expected Timeline |
|--------|---------------|-------------------|
| Aquatic insects visible in stream | Dissolved oxygen recovering | 1-3 years after chemical stop |
| Frog chorus audible | Atrazine levels below threshold | 2-5 years |
| Minnows/small fish present | Food web reconnecting | 3-7 years |
| Crawfish present | Substrate quality functional | 5-10 years |
| Turtles nesting on banks | Full aquatic-terrestrial link | 10-20 years |

## Layer 4: Knowledge Bridge

### The Problem Within the Problem

The people living in these towns have been deskilled by the same industrial system that deskilled the land. Three generations of "buy inputs, plant corn, sell corn" has erased the distributed ecological knowledge that maintained this landscape for millennia.

### Skill Inventory Protocol

For each town (population node), identify:

1. **Who remembers?** — Anyone over 60 who grew food without chemicals. Anyone with a garden. Anyone who hunts, fishes, forages. Anyone from an indigenous knowledge tradition
2. **Who can fix things?** — Mechanics, welders, plumbers. These are your infrastructure people
3. **Who has land access?** — Even small plots. Even abandoned lots. Even wide road ditches. Map every potential refugia site
4. **Who has water access?** — Wells, springs, streams not downstream of concentrated feedlots
5. **Who has seeds?** — Native seed savers, garden seed banks, prairie restoration groups

### Decision Tree: Subsidy Collapse Protocol

TRIGGER: External food/chemical supply disruption
│
├─ IMMEDIATE (Week 1-4)
│  ├─ Inventory existing food stores in community
│  ├─ Identify all water sources and test basic safety
│  ├─ Map all available growing land including lawns
│  └─ Activate skill holders — convene knowledge
│
├─ SHORT TERM (Month 1-6)│  ├─ Plant fast-cycle crops: radish (25 days), lettuce (30), beans (50)
│  ├─ Begin composting ALL organic waste — this is your soil amendment
│  ├─ Establish seed saving from first harvest
│  └─ Begin water filtration/purification systems from available materials
│
├─ MEDIUM TERM (Month 6-24)
│  ├─ Transition to calorie crops: potatoes, squash, corn (open-pollinated)
│  ├─ Integrate small livestock if available (chickens → eggs + dung beetles)
│  ├─ Begin refugia planting from Layer 2 pioneer species
│  └─ Establish trade networks with adjacent communities
│
└─ LONG TERM (Year 2+)
├─ Follow full Layer 1-4 restoration sequence
├─ Document everything — you are now the knowledge holders
├─ Train the next generation explicitly
└─ Connect to wider recovery corridor network


### Traditional Knowledge Integration

Indigenous peoples maintained this landscape as productive, diverse, biodiverse prairie-woodland mosaic for thousands of years using:
- **Controlled fire** — prairie burns cycling nutrients, preventing woody encroachment, stimulating native grasses
- **Polyculture planting** — Three Sisters and regional variants matching plant mutualism to local conditions
- **Seasonal rotation** — moving harvest pressure to match ecosystem carrying capacity
- **Water management** — working with natural hydrology instead of against it
- **Observation-based adaptation** — multi-generational knowledge of what the land is telling you, exactly what is being done right now on this drive

This knowledge still exists in living carriers. It is the most valuable resource in this framework.

## How To Use This Framework

### If You're a Local Resident
1. Walk your land using the Layer 0 field assessment protocol
2. Identify your nearest refugia — fence lines, ditches, abandoned plots
3. Stop mowing/spraying any area you can spare, no matter how small
4. Plant Layer 2 pioneer species along any edge habitat
5. Talk to your oldest neighbors about what this land used to look like

### If You're a Town Government
1. Map all municipally-owned land that can transition to native plantings
2. Reduce mowing programs — let road ditches become refugia corridors
3. Inventory community skill holders before they're gone
4. Establish seed library at the public library
5. Connect with adjacent towns to build corridor continuity

### If You're Reading This After Collapse
1. Start at the decision tree in Layer 4
2. Don't panic — this framework was designed for this moment
3. Work Layer 0 assessment first — know what you have
4. Follow the sequencing — it's thermodynamically ordered for a reason
5. You have everything you need to begin. Start.

## Corridor Context

This framework was developed from direct field observation along the southern Minnesota corridor (Blue Earth to Fairmont, Martin County) in March 2026. It is designed to be applicable to any agricultural zone experiencing similar monoculture-driven ecological collapse. The insect sequencing, plant succession, and water recovery protocols are calibrated for USDA Hardiness Zones 4a-4b, southern Minnesota clay-loam soils, and continental climate patterns.

For the broader corridor resilience context, see:
- [Urban Resilience Simulator](https://github.com/JinnZ2/urban-resilience-sim)
- [Combine Cognitive Architecture](https://github.com/JinnZ2/Combine-Cognitive-Architecture-)
- [Planetary Conservation Framework](https://github.com/JinnZ2/planetary-conservation-framework)

## Contributing

This is CC0. Take it. Use it. Adapt it to your bioregion. If you improve it, push it back so others benefit. If you're a researcher with species-specific data for this corridor, open a PR.

## Field Notes

*March 21, 2026 — Southern MN corridor, Blue Earth to Fairmont*
*170+ miles. Zero insects on windshield. Zero birds visible. Zero mammals visible.*
*78°F after recent blizzard. Peak spring migration window.*
*This document exists because that silence demands a response.*



Ecological recovery for Industrial Agriculture 


Layer 0: SUBSTRATE ASSESSMENT
├── Soil state classification (dead/degraded/recoverable)
├── Water contamination mapping (ag chemical load by stream)
├── Refugia identification (ditches, fence lines, abandoned plots, wetlands)
└── Chemical persistence timelines by compound class

Layer 0.5: METROLOGICAL AUDIT (can the instrument see it?)
├── Blindness taxonomy (null / alias / saturation / gate / frame)
├── Grounding rungs M0-M3 + confidence gradient per reading
├── RT_soil regenerative throughput under mass-balance closure
├── Depth horizon resolution (0-10 / 10-20 / 20-30 / 30-60cm)
└── Breach timeline vs recovery lag → hard extraction boundary

Layer 1: INSECT SEQUENCING (chemical tolerance order)
├── Phase 1: Dung beetles, ground beetles, ants (soil builders)
├── Phase 2: Native flies, grasshoppers (food web bridge)
├── Phase 3: Sweat bees, native pollinators (plant reproduction)
└── Phase 4: Lepidoptera, specialist species (ecosystem maturity signal)

Layer 2: PLANT SUCCESSION
├── Pioneer: Native grasses, clover (nitrogen fixers, soil holders)
├── Early: Prairie forbs, milkweed (pollinator support)
├── Mid: Shrub layer (bird habitat, windbreak)
└── Late: Tree canopy (full water cycle restoration)

Layer 3: WATER RECOVERY
├── Stream bank stabilization species
├── Groundwater recharge mapping
├── Wetland restoration sequencing
└── Contamination flush timelines

Layer 4: KNOWLEDGE BRIDGE
├── Local skill inventory (who knows what)
├── Traditional practice integration
├── Tool/resource requirements per phase
└── Decision tree: "subsidy collapse happened, now what"


