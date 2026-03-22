# Urban Resilience Simulator

A systems-dynamics model for community resilience under infrastructure stress.
Bridges hyper-local ecological recovery (see [Fairmont Ecological Recovery](https://github.com/JinnZ2/fairmont-ecological-recovery))
with urban/town-scale resource planning.

## What This Does

Simulates how a small community (1,000–50,000 people) responds to cascading
infrastructure failures — supply chain disruption, energy grid instability,
water system compromise — and models recovery pathways using local ecological
and human resources.

**Core question**: If the trucks stop coming, how long can your community feed itself,
and what does the transition path look like?

## Architecture

```
urban-resilience-sim/
├── community.py       — Community model: population, resources, infrastructure
├── supply_chain.py    — Supply chain stress model and disruption scenarios
├── food_system.py     — Local food production capacity modeling
├── energy_model.py    — Energy independence and transition modeling
├── water_system.py    — Water infrastructure resilience
├── network.py         — Inter-community corridor networking
├── simulator.py       — Interactive CLI simulator
└── README.md
```

## Running

```bash
python simulator.py        # Interactive mode
python community.py        # Example community assessment
python supply_chain.py     # Supply chain stress scenarios
```

## Zero Dependencies

Pure Python 3 standard library. No internet required. Designed for the same
conditions as the ecological recovery framework — if you need this tool,
you may not have package managers available.

## Integration with Ecological Recovery Framework

This simulator consumes Layer 0-4 outputs from the Fairmont framework:
- **Layer 0 (Substrate)** → local food production potential
- **Layer 1-2 (Insects/Plants)** → ecosystem service timeline
- **Layer 3 (Water)** → water system resilience scoring
- **Layer 4 (Knowledge)** → community capacity modeling

## License

CC0 1.0 Universal — no rights reserved.
