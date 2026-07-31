Round 1 is **not handled by this agent**. {{party_a}}'s opening `demand` move is set programmatically from `party_a.opening_demand.json`. You only act in round 2 and later.

Your task in this step is **decision only**. Do not draft the public letter to the other party.

First explain your reasoning briefly in `reason` (offer justification, opponent position, case facts). Then choose `action`. For `counter`, also set `offer`.

You will receive:
- Your case facts (briefing materials for your side)
- The full public negotiation history
- The opponent's most recent negotiated offer (if any)
- The current round number

You must choose **exactly one** action:

| Action | When to use | Offer field |
|---|---|---|
| `counter` | Propose a revised settlement amount in response to the opponent | Required: positive integer (whole USD dollars) |
| `accept` | Accept the opponent's **last negotiated offer** shown in context | Omit — the settlement amount is taken from that last offer automatically |
| `break` | End negotiations and proceed to litigation | Omit or null |

### What `accept` means

`accept` is a deliberate decision to **close the deal** on the opponent's **last negotiated offer** (the amount shown as the opponent's most recent offer in your context). You are not proposing a new number — you agree to their last stated settlement figure.

Choose `accept` only when you judge that:
- Further counter-offers are unlikely to improve the outcome enough to justify more rounds.
- Litigation would not produce a better result than taking that last offer.
- The last offer is a **meaningful compromise** you are willing to live with, even if it is not your ideal price.

`accept` ends the negotiation in agreement. Do not use it if you still intend to keep bargaining or if you would prefer trial.

Rules:
- You must choose exactly one action.
- **Round 2+ only** — round 1 `demand` is programmatic, not chosen by this agent.
- **`counter`**: propose a realistic amount informed by your case facts and instructions.
- **`break`**: use when the gap is irreconcilable and trial is preferable to another counter.
- **`reason`**: short analytic justification for your decision (not the formal message).

Return the structured fields for this step: `reason`, `action`, and `offer` when you choose `counter`.
