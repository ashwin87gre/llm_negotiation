Your task in this step is **decision only**. Do not draft the public letter to the other party.

In `reason`, give your analytical justification by working through:
1. Opponent's previous offers and what their messages signal about their position.
2. Your case's strengths and weaknesses and your side's negotiating position.
3. Why your chosen action (and offer, if countering) is the best response.

Then set `action` (and `offer` for `counter`).

You will receive:
- The full public negotiation history including {{party_a}}'s move in the current round
- {{party_a}}'s last negotiated offer this round (`demand` in round 1, or {{party_a}}'s latest counter in later rounds)
- The current round number

Your case facts and negotiating instructions are in the system message.

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
- **`reason`**: analytical justification following the steps above (not the formal message; not shown in public negotiation history).

Return the structured fields for this step: `reason`, `action`, and `offer` when you choose `counter`.
