from __future__ import annotations

from unittest.mock import MagicMock, patch

from src.models import Negotiation, OpeningOfferOutput
from src.opening_offer import build_opening_offer_user_context, generate_opening_offer


def test_build_opening_offer_user_context():
    text = build_opening_offer_user_context()
    assert "before any public negotiation history exists" in text
    assert "Current round number: 1" in text


@patch("src.opening_offer.structured_llm")
def test_generate_opening_offer_invokes_structured_llm(mock_structured_llm: MagicMock):
    mock_runnable = MagicMock()
    mock_structured_llm.return_value = mock_runnable
    mock_runnable.invoke.return_value = OpeningOfferOutput(offer=18_000_000)

    negotiation = Negotiation(
        case_id="TEST",
        party_a="Summit VI LLC",
        party_b="Samsung Electronics Co., Ltd.",
    )

    with patch("src.opening_offer.load_party_instructions", return_value="Instructions."):
        with patch("src.opening_offer.load_case_facts", return_value="Case facts."):
            with patch(
                "src.opening_offer.build_system_prompt",
                return_value="system",
            ) as mock_build_system_prompt:
                offer = generate_opening_offer(
                    negotiation_path="/tmp/negotiation.json",
                    negotiation=negotiation,
                )

    assert offer == 18_000_000
    mock_build_system_prompt.assert_called_once()
    mock_structured_llm.assert_called_once_with(OpeningOfferOutput)
    messages = mock_runnable.invoke.call_args[0][0]
    assert messages[0].content == "system"
    assert "opening move" in messages[1].content
