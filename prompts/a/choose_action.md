Round 1 is **not handled by this agent**. {{party_a}}'s opening `demand` uses a message template from `party_a.opening_demand.json` and an LLM-generated offer substituted as `{{offer}}`. You only act in round 2 and later.

Your task in this step is **decision only**. Do not draft the public letter to the other party.

In `reason`, give your analytical justification by working through:
1. Opponent's previous offers and what their messages signal about their position.
2. Your case's strengths and weaknesses and your side's negotiating position.
3. Why your chosen action (and offer, if countering) is the best response.

Then set `action` (and `offer` for `counter`).

You will receive:
- The full public negotiation history
- The opponent's most recent negotiated offer (if any)
- The current round number

Your case facts and negotiating instructions are in the system message.

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
- **`reason`**: analytical justification following the steps above (not the formal message; not shown in public negotiation history).

Return the structured fields for this step: `reason`, `action`, and `offer` when you choose `counter`.
