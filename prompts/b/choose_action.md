Your task in this step is **decision only**. Do not draft the public letter to the other party.

First explain your reasoning briefly in `reason` (offer justification, opponent position, case facts). Then choose `action`. For `counter`, also set `offer`.

You will receive:
- Your case facts (briefing materials for your side)
- The full public negotiation history including {{party_a}}'s move in the current round
- {{party_a}}'s last negotiated offer this round (`demand` in round 1, or {{party_a}}'s latest counter in later rounds)
- The current round number

You must choose **exactly one** action:

| Action | When to use | Offer field |
|---|---|---|
| `counter` | Respond with a new settlement amount (typical response to {{party_a}}'s demand or counter) | Required: positive integer (whole USD dollars) |
| `accept` | Accept {{party_a}}'s **last negotiated offer this round** | Omit — the settlement amount is taken from that offer automatically |
| `break` | End negotiations and proceed to litigation | Omit or null |

### What `accept` means

`accept` is a deliberate decision to **close the deal** on {{party_a}}'s **last negotiated offer in the current round** (their offer shown for this round in the negotiation history). You are not proposing a new number — you agree to their last stated settlement figure.

Choose `accept` only when you judge that:
- Further counter-offers are unlikely to improve the outcome enough to justify more rounds.
- Litigation would not produce a better result than taking that last offer.
- The last offer is a **meaningful compromise** you are willing to live with, even if it is not your ideal price.

`accept` ends the negotiation in agreement. Do not use it if you still intend to keep bargaining or if you would prefer trial.

Rules:
- You must choose exactly one action.
- **Round 1**: respond to {{party_a}}'s `demand` move shown in the negotiation history.
- **`counter`**: propose a realistic amount informed by your case facts and instructions.
- **`break`**: use when the gap is irreconcilable and trial is preferable to another counter.
- **`reason`**: short analytic justification for your decision (not the formal message).

Return the structured fields for this step: `reason`, `action`, and `offer` when you choose `counter`.
