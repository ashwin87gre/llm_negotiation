from __future__ import annotations

from unittest.mock import MagicMock, patch

from pydantic import BaseModel

from src.llm import structured_llm


class _SampleSchema(BaseModel):
    value: int


@patch("src.llm.get_llm")
def test_structured_llm_uses_json_schema_strict(mock_get_llm: MagicMock):
    mock_base = MagicMock()
    mock_get_llm.return_value = mock_base
    mock_runnable = MagicMock()
    mock_base.with_structured_output.return_value = mock_runnable

    result = structured_llm(_SampleSchema)

    mock_base.with_structured_output.assert_called_once_with(
        _SampleSchema,
        method="json_schema",
        strict=True,
    )
    assert result is mock_runnable
