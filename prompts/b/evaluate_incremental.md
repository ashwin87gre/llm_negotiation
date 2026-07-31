This is an **incremental private evaluation** for round 2 or later.

You will receive:
- Your global agent instructions (role, goals, briefing)
- Your **prior private assessment** (persisted from your last turn)
- **Public negotiation history** only

Update your assessment based on new public information and your prior private state. Do not choose an action. Do not draft negotiation messages.

Return the structured private-assessment fields defined for this step.

Field meanings for {{party_b}}:
- `reservation_price`: maximum acceptable settlement (whole USD dollars)
- `case_strength`: strength of non-infringement/invalidity defenses (0.0–1.0)
- `opponent_argument_risk`: risk that opponent infringement arguments prevail (0.0–1.0)
- `litigation_cost_estimate`: expected litigation cost (whole USD dollars)
