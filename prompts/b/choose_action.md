Your task in this step is **decision only**. Do not draft the public letter to the other party.

In `reason`, give your analytical justification by working through:
1. Opponent's previous offers and what their messages signal about their position.
2. Your case's strengths and weaknesses and your side's negotiating position.
3. What happens if you do not settle: your litigation costs, the probability of an injunction and what it would cost, and how well the opponent's arguments would hold up in court. Use that to work out the worst settlement you would still prefer to litigating.
4. Which action follows from steps 1-3, addressing the question specific to it:
   - `counter` — why the amount you propose is more likely to be accepted than your previous offer, and why it is still an outcome your side would be satisfied with.
   - `accept` — why their last offer is a meaningful compromise, and why further rounds are unlikely to improve on it.
   - `break` — why their last offer is not a meaningful compromise, and why no further round is likely to close the gap.

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
- **`counter`**: propose an amount that could plausibly close the gap, grounded in your case facts and instructions.
- **`break`**: use when the gap is irreconcilable and trial is preferable to another counter.
- **`reason`**: analytical justification following the steps above (not the formal message; not shown in public negotiation history).

Return the structured fields for this step: `reason`, `action`, and `offer` when you choose `counter`.
