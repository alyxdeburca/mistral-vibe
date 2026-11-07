from __future__ import annotations

from unittest.mock import MagicMock

from vibe.acp.agent import VibeAcpAgent, _usage_since
from vibe.app_server.models import TokenUsage


def _tokens(
    input_tokens: int, output_tokens: int, cached_input_tokens: int = 0
) -> TokenUsage:
    return TokenUsage(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        cached_input_tokens=cached_input_tokens,
    )


class TestUsageSince:
    def test_subtracts_cumulative_baseline(self) -> None:
        cumulative = _tokens(1_000, 500, cached_input_tokens=200)
        baseline = _tokens(800, 300, cached_input_tokens=150)

        delta = _usage_since(cumulative, baseline)

        assert delta.input_tokens == 200
        assert delta.output_tokens == 200
        assert delta.cached_read_tokens == 50
        assert delta.total_tokens == 400

    def test_clamps_counters_that_shed_to_zero(self) -> None:
        baseline = _tokens(900, 400, cached_input_tokens=800)
        reloaded = _tokens(100, 10, cached_input_tokens=50)

        delta = _usage_since(reloaded, baseline)

        assert delta.input_tokens == 0
        assert delta.output_tokens == 0


def test_turn_usage_reports_delta_not_cumulative() -> None:
    agent = object.__new__(VibeAcpAgent)
    session = MagicMock()
    session.app_server.resources.runtime.stats.token_usage = _tokens(2_000, 1_000)
    baseline = _tokens(1_500, 700)

    usage = agent._turn_usage(session, baseline)

    assert usage.input_tokens == 500
    assert usage.output_tokens == 300
