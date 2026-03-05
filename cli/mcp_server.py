"""MCP server for agent-cli — exposes trading tools via Model Context Protocol."""
from __future__ import annotations

import subprocess
import sys
from typing import Optional


def _run_hl(*args: str, timeout: int = 30) -> str:
    """Run an hl CLI command and return stdout."""
    cmd = [sys.executable, "-m", "cli.main", *args]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    output = result.stdout.strip()
    if result.returncode != 0 and result.stderr:
        output = output + "\n" + result.stderr.strip() if output else result.stderr.strip()
    return output or "(no output)"


def create_mcp_server():
    """Create and configure the FastMCP server."""
    from mcp.server.fastmcp import FastMCP

    mcp = FastMCP("yex-trader", instructions="Autonomous Hyperliquid trading CLI — 14 strategies, WOLF orchestrator, HOWL reviews.")

    @mcp.tool()
    def account(mainnet: bool = False) -> str:
        """Get Hyperliquid account state (balances, positions)."""
        args = ["account"]
        if mainnet:
            args.append("--mainnet")
        return _run_hl(*args)

    @mcp.tool()
    def status() -> str:
        """Show current positions, PnL, and risk state."""
        return _run_hl("status")

    @mcp.tool()
    def trade(instrument: str, side: str, size: float) -> str:
        """Place a single manual order.

        Args:
            instrument: Trading pair (e.g., ETH-PERP, BTC-PERP, VXX-USDYP)
            side: Order side — "buy" or "sell"
            size: Order size in contracts
        """
        return _run_hl("trade", instrument, side, str(size))

    @mcp.tool()
    def run_strategy(
        strategy: str,
        instrument: str = "ETH-PERP",
        tick: int = 10,
        max_ticks: Optional[int] = None,
        mock: bool = False,
        dry_run: bool = False,
        mainnet: bool = False,
    ) -> str:
        """Start autonomous trading with a strategy.

        Args:
            strategy: Strategy name (e.g., engine_mm, avellaneda_mm, momentum_breakout)
            instrument: Trading instrument (default: ETH-PERP)
            tick: Seconds between ticks (default: 10)
            max_ticks: Stop after N ticks (None = run forever)
            mock: Use mock data instead of real API
            dry_run: Log decisions without placing orders
            mainnet: Use mainnet instead of testnet
        """
        args = ["run", strategy, "-i", instrument, "-t", str(tick)]
        if max_ticks is not None:
            args.extend(["--max-ticks", str(max_ticks)])
        if mock:
            args.append("--mock")
        if dry_run:
            args.append("--dry-run")
        if mainnet:
            args.append("--mainnet")
        return _run_hl(*args, timeout=max(60, (max_ticks or 10) * tick + 30))

    @mcp.tool()
    def strategies() -> str:
        """List all available trading strategies."""
        return _run_hl("strategies")

    @mcp.tool()
    def scanner_run(mock: bool = False) -> str:
        """Run opportunity scanner — screen HL perps for trading setups."""
        args = ["scanner", "once"]
        if mock:
            args.append("--mock")
        return _run_hl(*args, timeout=60)

    @mcp.tool()
    def wolf_status() -> str:
        """Get WOLF orchestrator status (slots, positions, daily PnL)."""
        return _run_hl("wolf", "status")

    @mcp.tool()
    def wolf_run(
        mock: bool = False,
        max_ticks: Optional[int] = None,
        preset: str = "default",
        mainnet: bool = False,
    ) -> str:
        """Start WOLF multi-slot orchestrator.

        Args:
            mock: Use mock data
            max_ticks: Stop after N ticks
            preset: Strategy preset (default, conservative, aggressive)
            mainnet: Use mainnet
        """
        args = ["wolf", "run", "--preset", preset]
        if mock:
            args.append("--mock")
        if max_ticks is not None:
            args.extend(["--max-ticks", str(max_ticks)])
        if mainnet:
            args.append("--mainnet")
        return _run_hl(*args, timeout=max(120, (max_ticks or 10) * 60 + 30))

    @mcp.tool()
    def howl_run(since: Optional[str] = None) -> str:
        """Run HOWL performance review — analyze trades and generate report.

        Args:
            since: Start date for analysis (YYYY-MM-DD). Default: since last report.
        """
        args = ["howl", "run"]
        if since:
            args.extend(["--since", since])
        return _run_hl(*args)

    @mcp.tool()
    def setup_check() -> str:
        """Validate environment — SDK, keys, network, builder fee."""
        return _run_hl("setup", "check")

    @mcp.tool()
    def builder_status() -> str:
        """Get builder fee configuration status."""
        return _run_hl("builder", "status")

    @mcp.tool()
    def wallet_list() -> str:
        """List saved encrypted keystores."""
        return _run_hl("wallet", "list")

    @mcp.tool()
    def wallet_auto() -> str:
        """Create a new wallet non-interactively (agent-friendly)."""
        return _run_hl("wallet", "auto")

    return mcp
