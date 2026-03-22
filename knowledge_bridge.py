"""
knowledge_bridge.py — Layer 4: Knowledge Bridge
Fairmont Ecological Recovery Framework
License: CC0

Skill inventory, knowledge holder tracking,
and collapse decision tree engine.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class SkillCategory(Enum):
    FOOD_PRODUCTION = "food_production"
    WATER_MANAGEMENT = "water_management"
    MECHANICAL = "mechanical"
    ECOLOGICAL = "ecological"
    MEDICAL = "medical"
    TRADITIONAL = "traditional"
    CONSTRUCTION = "construction"
    COMMUNICATION = "communication"


class Urgency(Enum):
    IMMEDIATE = "IMMEDIATE"    # Week 1-4
    SHORT_TERM = "SHORT_TERM"  # Month 1-6
    MEDIUM_TERM = "MEDIUM_TERM"  # Month 6-24
    LONG_TERM = "LONG_TERM"    # Year 2+


@dataclass
class KnowledgeHolder:
    """A person carrying critical knowledge."""
    identifier: str  # anonymized — "Holder_01" etc.
    location: str
    categories: list[SkillCategory]
    specific_skills: list[str]
    age_range: Optional[str] = None  # "60+", "40-60", "20-40"
    available: bool = True
    knowledge_documented: bool = False
    notes: Optional[str] = None


@dataclass
class CommunityResource:
    """Physical resource in a community."""
    resource_type: str  # "land", "water", "seeds", "tools", "shelter"
    description: str
    location: str
    access_status: str  # "available", "restricted", "unknown"
    capacity_notes: Optional[str] = None


@dataclass 
class CollapseAction:
    """Single action in collapse response protocol."""
    action: str
    urgency: Urgency
    responsible: str  # skill category needed
    resources_needed: list[str]
    success_signal: str
    dependencies: list[str] = field(default_factory=list)


# ── Community inventory engine ─────────────────────────────────

class CommunityInventory:
    def __init__(self, community_name: str, population_est: int):
        self.community_name = community_name
        self.population_est = population_est
        self.holders: list[KnowledgeHolder] = []
        self.resources: list[CommunityResource] = []

    def add_holder(self, holder: KnowledgeHolder):
        self.holders.append(holder)

    def add_resource(self, resource: CommunityResource):
        self.resources.append(resource)

    def get_holders_by_category(self, cat: SkillCategory) -> list[KnowledgeHolder]:
        return [h for h in self.holders if cat in h.categories]

    def get_undocumented_holders(self) -> list[KnowledgeHolder]:
        return [h for h in self.holders if not h.knowledge_documented]

    def get_critical_gaps(self) -> list[SkillCategory]:
        """Identify skill categories with zero holders."""
        covered = set()
        for h in self.holders:
            covered.update(h.categories)
        return [cat for cat in SkillCategory if cat not in covered]

    def get_resources_by_type(self, rtype: str) -> list[CommunityResource]:
        return [r for r in self.resources if r.resource_type == rtype]

    def documentation_score(self) -> float:
        """Percentage of knowledge holders whose knowledge is documented."""
        if not self.holders:
            return 0.0
        documented = sum(1 for h in self.holders if h.knowledge_documented)
        return (documented / len(self.holders)) * 100


# ── Collapse decision tree ────────────────────────────────────

def generate_collapse_protocol(inventory: CommunityInventory) -> list[CollapseAction]:
    """
    Generate community-specific collapse response protocol.
    Adapts based on available knowledge holders and resources.
    """
    actions = []

    # ── IMMEDIATE (Week 1-4) ──
    actions.append(CollapseAction(
        "Inventory all existing food stores in community — every household, every store, every warehouse",
        Urgency.IMMEDIATE,
        "community_leadership",
        ["Survey team", "Communication network"],
        "Complete food inventory with calorie estimate and duration",
    ))
    actions.append(CollapseAction(
        "Identify and test ALL water sources — wells, springs, streams, municipal",
        Urgency.IMMEDIATE,
        "water_management",
        ["Basic water testing (at minimum: smell, clarity, taste)", "Map of water infrastructure"],
        "Water source map with safety assessment for each",
    ))
    actions.append(CollapseAction(
        "Map all available growing land — yards, lots, parks, road margins, abandoned fields",
        Urgency.IMMEDIATE,
        "food_production",
        ["Walking survey", "Basic soil assessment (Layer 0 protocol)"],
        "Land map with soil state classification for each plot",
    ))
    actions.append(CollapseAction(
        "Activate all identified knowledge holders — convene emergency skill council",
        Urgency.IMMEDIATE,
        "community_leadership",
        ["Meeting space", "Contact list"],
        "All holders contacted, skills mapped to immediate needs",
    ))

    # Check for water management gap
    water_holders = inventory.get_holders_by_category(SkillCategory.WATER_MANAGEMENT)
    if not water_holders:
        actions.append(CollapseAction(
            "CRITICAL GAP: No identified water management knowledge — begin emergency water safety protocols from written reference",
            Urgency.IMMEDIATE,
            "any_available",
            ["This framework's water recovery module", "Any available water treatment supplies"],
            "Basic water purification operational (boiling at minimum)",
        ))

    # ── SHORT TERM (Month 1-6) ──
    actions.append(CollapseAction(
        "Plant fast-cycle crops: radish (25 days), lettuce (30 days), beans (50 days)",
        Urgency.SHORT_TERM,
        "food_production",
        ["Seeds (any source)", "Any viable soil from Layer 0 assessment", "Water access"],
        "First harvest within 30 days",
        dependencies=["Land mapped", "Water sources identified"],
    ))
    actions.append(CollapseAction(
        "Begin composting ALL organic waste — this is your primary soil amendment",
        Urgency.SHORT_TERM,
        "food_production",
        ["Collection system", "Compost site away from water sources"],
        "Active compost pile generating heat within 2 weeks",
    ))
    actions.append(CollapseAction(
        "Establish seed saving protocol from first harvest",
        Urgency.SHORT_TERM,
        "food_production",
        ["Knowledge of open-pollinated vs hybrid", "Dry storage"],
        "Seed stock for next planting cycle secured",
        dependencies=["First harvest"],
    ))
    actions.append(CollapseAction(
        "Begin water filtration/purification from available materials — sand filter, solar pasteurization, boiling",
        Urgency.SHORT_TERM,
        "water_management",
        ["Sand, gravel, charcoal (or wood to make charcoal)", "Clear containers for solar treatment"],
        "Reliable purification system serving community",
        dependencies=["Water sources identified"],
    ))

    # ── MEDIUM TERM (Month 6-24) ──
    actions.append(CollapseAction(
        "Transition to calorie crops: potatoes, squash, corn (open-pollinated ONLY)",
        Urgency.MEDIUM_TERM,
        "food_production",
        ["Open-pollinated seed stock", "Larger growing area", "Soil improvement from composting"],
        "Calorie production approaching community sustenance level",
        dependencies=["Seed saving operational", "Compost available"],
    ))
    actions.append(CollapseAction(
        "Integrate small livestock if available — chickens are priority (eggs + dung beetles)",
        Urgency.MEDIUM_TERM,
        "food_production",
        ["Any available poultry", "Enclosure materials", "Feed source"],
        "Egg production + manure cycling for Layer 1 insect recovery",
    ))
    actions.append(CollapseAction(
        "Begin Layer 2 pioneer plantings in all available refugia",
        Urgency.MEDIUM_TERM,
        "ecological",
        ["Native seed (see plant_succession.py)", "Identified refugia sites"],
        "Pioneer species establishing in refugia zones",
        dependencies=["Layer 0 assessment complete"],
    ))
    actions.append(CollapseAction(
        "Establish trade/communication network with adjacent communities",
        Urgency.MEDIUM_TERM,
        "communication",
        ["CB radio, LoRa mesh, HAM, runners — any available", "Trade goods inventory"],
        "Regular contact with 2+ neighboring communities",
    ))

    # ── LONG TERM (Year 2+) ──
    actions.append(CollapseAction(
        "Follow full Layer 1-4 restoration sequence from this framework",
        Urgency.LONG_TERM,
        "ecological",
        ["This framework", "Community labor", "Time"],
        "Insect Phase 1 signals appearing",
        dependencies=["Refugia protected", "Chemical input stopped"],
    ))
    actions.append(CollapseAction(
        "Document EVERYTHING — you are now the knowledge holders for the next generation",
        Urgency.LONG_TERM,
        "all",
        ["Writing materials", "Oral tradition protocols", "Apprenticeship structures"],
        "Written + oral knowledge base covering all critical skills",
    ))
    actions.append(CollapseAction(
        "Train next generation explicitly — apprenticeship model, not classroom",
        Urgency.LONG_TERM,
        "all",
        ["Willing learners", "Patient teachers", "Real work to do together"],
        "At least 2 people trained per critical skill category",
    ))
    actions.append(CollapseAction(
        "Connect to wider recovery corridor network (see Urban Resilience Simulator)",
        Urgency.LONG_TERM,
        "communication",
        ["Communication infrastructure", "Shared framework with neighboring communities"],
        "Corridor-level coordination operational",
    ))

    return actions


# ── Traditional knowledge integration ─────────────────────────

TRADITIONAL_PRACTICES = [
    {
        "practice": "Controlled fire — prairie burns",
        "function": "Nutrient cycling, woody encroachment prevention, native grass stimulation",
        "when": "Late fall or early spring, low wind, experienced burns only",
        "modern_equivalent": "Mowing (inferior substitute — doesn't cycle nutrients)",
        "knowledge_source": "Indigenous land management — thousands of years of practice",
    },
    {
        "practice": "Three Sisters polyculture",
        "function": "Corn (structure) + beans (nitrogen) + squash (ground cover/moisture retention)",
        "when": "After last frost, soil temp >60°F",
        "modern_equivalent": "No equivalent — monoculture cannot replicate mutualism",
        "knowledge_source": "Haudenosaunee and widespread indigenous agricultural systems",
    },
    {
        "practice": "Seasonal harvest rotation",
        "function": "Matching harvest pressure to ecosystem carrying capacity",
        "when": "Year-round cycle — different resources each season",
        "modern_equivalent": "Crop rotation (pale imitation — only rotates 2 crops)",
        "knowledge_source": "All indigenous land management traditions in this corridor",
    },
    {
        "practice": "Working with natural hydrology",
        "function": "Using landscape water flow rather than fighting it",
        "when": "Infrastructure planning, planting decisions",
        "modern_equivalent": "Tile drainage (exact opposite — forces water out)",
        "knowledge_source": "Landscape-encoded knowledge traditions",
    },
    {
        "practice": "Observation-based multi-generational adaptation",
        "function": "Reading what the land is telling you, adapting practice over generations",
        "when": "Always — this is the operating system, not a technique",
        "modern_equivalent": "Soil testing (single-variable snapshot vs integrated reading)",
        "knowledge_source": "Living carriers of traditional ecological knowledge",
    },
]


# ── Report ────────────────────────────────────────────────────

def knowledge_report(inventory: CommunityInventory) -> str:
    """Full knowledge bridge report for a community."""
    gaps = inventory.get_critical_gaps()
    undocumented = inventory.get_undocumented_holders()
    doc_score = inventory.documentation_score()
    protocol = generate_collapse_protocol(inventory)

    lines = [
        f"{'='*60}",
        f"KNOWLEDGE BRIDGE REPORT: {inventory.community_name}",
        f"{'='*60}",
        f"Population est:        {inventory.population_est}",
        f"Knowledge holders:     {len(inventory.holders)}",
        f"Documentation score:   {doc_score:.0f}%",
        f"Critical skill gaps:   {len(gaps)}",
        f"",
    ]

    if gaps:
        lines.append("── CRITICAL GAPS (zero holders) ──")
        for g in gaps:
            lines.append(f"  !! {g.value.replace('_', ' ').upper()}")
        lines.append("")

    if undocumented:
        lines.append(f"── UNDOCUMENTED HOLDERS ({len(undocumented)}) ──")
        for h in undocumented:
            lines.append(f"  {h.identifier}: {', '.join(s for s in h.specific_skills[:3])}")
            if h.age_range == "60+":
                lines.append(f"    !! AGE 60+ — DOCUMENT NOW")
        lines.append("")

    lines.append("── KNOWLEDGE HOLDERS ──")
    for cat in SkillCategory:
        holders = inventory.get_holders_by_category(cat)
        if holders:
            lines.append(f"\n  {cat.value.replace('_', ' ').title()} ({len(holders)})")
            for h in holders:
                lines.append(f"    {h.identifier} — {', '.join(h.specific_skills[:3])}")
                lines.append(f"      Documented: {'Yes' if h.knowledge_documented else 'NO'}")

    lines += ["", "── COLLAPSE PROTOCOL ──"]
    for urgency in Urgency:
        phase_actions = [a for a in protocol if a.urgency == urgency]
        if phase_actions:
            labels = {
                Urgency.IMMEDIATE: "IMMEDIATE (Week 1-4)",
                Urgency.SHORT_TERM: "SHORT TERM (Month 1-6)",
                Urgency.MEDIUM_TERM: "MEDIUM TERM (Month 6-24)",
                Urgency.LONG_TERM: "LONG TERM (Year 2+)",
            }
            lines.append(f"\n  {labels[urgency]}")
            for a in phase_actions:
                lines.append(f"    → {a.action}")
                lines.append(f"      Signal: {a.success_signal}")
                if a.dependencies:
                    lines.append(f"      After:  {', '.join(a.dependencies)}")

    lines += ["", "── TRADITIONAL KNOWLEDGE REFERENCE ──"]
    for tp in TRADITIONAL_PRACTICES:
        lines.append(f"\n  {tp['practice']}")
        lines.append(f"    Function: {tp['function']}")
        lines.append(f"    Source:   {tp['knowledge_source']}")

    lines.append(f"{'='*60}")
    return "\n".join(lines)


if __name__ == "__main__":
    # Example: Fairmont with minimal knowledge inventory
    inv = CommunityInventory("Fairmont, MN", population_est=10000)

    # Add example holders (anonymized)
    inv.add_holder(KnowledgeHolder(
        "Holder_01", "Fairmont",
        [SkillCategory.FOOD_PRODUCTION, SkillCategory.ECOLOGICAL],
        ["Garden without chemicals", "Seed saving", "Soil reading"],
        age_range="60+", knowledge_documented=False,
    ))
    inv.add_holder(KnowledgeHolder(
        "Holder_02", "Fairmont",
        [SkillCategory.MECHANICAL, SkillCategory.CONSTRUCTION],
        ["Small engine repair", "Well pump maintenance", "Welding"],
        age_range="40-60", knowledge_documented=False,
    ))

    print(knowledge_report(inv))
