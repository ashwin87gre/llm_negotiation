Your task in this step is **message drafting only**. The action, offer, and reason have already been decided — do not change them.

You will receive:
- The decision rationale from the action step
- The chosen action (`counter`, `accept`, or `break`) and offer amount (if applicable)
- The negotiation history including {{party_a}}'s move this round

Your case facts and negotiating instructions are in the system message.

Write a professional message **to {{party_a}}** that reflects the chosen action. Draw on the decision rationale and case facts to justify your position, but do not restate the rationale verbatim.

- **`counter`**: State your counter-offer clearly and explain briefly why it is reasonable.
- **`accept`**: Explicitly accept {{party_a}}'s last negotiated offer this round and indicate the matter is settled. State that you agree to close on their last offer — the settlement amount is already fixed by that offer.
- **`break`**: State that negotiations have failed and you are proceeding to litigation.

Do not use the labels "Party A" or "Party B".

Return the structured field for this step: `message`.
