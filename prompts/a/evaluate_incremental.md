This is an **incremental private evaluation** for round 2 or later.

You will receive:
- Your global agent instructions (role, goals, briefing)
- Your **prior private assessment** (persisted from your last turn)
- **Public negotiation history** only (prior round messages/offers)

Update your assessment based on new public information and your prior private state. Do not choose an action. Do not draft negotiation messages.

Return the structured private-assessment fields defined for this step.

Field meanings for {{party_a}}:
- `reservation_price`: minimum acceptable settlement (whole USD dollars)
- `case_strength`: infringement case strength (0.0–1.0)
- `opponent_argument_risk`: credibility/risk of opponent invalidity arguments (0.0–1.0)
- `litigation_cost_estimate`: expected litigation cost (whole USD dollars)
