Round 1 `demand` is set programmatically from `party_a.opening_demand.json`. You only draft messages for round 2 and later moves.

Your task in this step is **message drafting only**. The action, offer, and reason have already been decided — do not change them.

You will receive:
- Your full case facts (briefing materials for your side)
- The decision rationale from the action step
- The chosen action (`counter`, `accept`, or `break`) and offer amount (if applicable)
- The negotiation history and current round number

Write a professional message **to {{party_b}}** that reflects the chosen action and offer. Use the decision rationale and case facts to justify the number, but do not copy the rationale verbatim or expose confidential material beyond what supports the public offer.

- **`counter`**: State your counter-offer clearly and explain briefly why it is reasonable.
- **`accept`**: Explicitly accept the opponent's last negotiated offer and indicate the matter is settled. State that you agree to close on their last offer — the settlement amount is already fixed by that offer.
- **`break`**: State that negotiations have failed and you are proceeding to litigation.

Do not use the labels "Party A" or "Party B".

Return the structured field for this step: `message`.
