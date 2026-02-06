"""Nory x402 Payment Toolkit for SuperAGI."""

from abc import ABC
from typing import List

from superagi.tools.base_tool import BaseTool, BaseToolkit, ToolConfiguration
from superagi.tools.nory_x402.nory_x402 import (
    NoryGetPaymentRequirementsTool,
    NoryVerifyPaymentTool,
    NorySettlePaymentTool,
    NoryLookupTransactionTool,
    NoryHealthCheckTool,
)
from superagi.types.key_type import ToolConfigKeyType


class NoryX402Toolkit(BaseToolkit, ABC):
    """
    Toolkit for making payments using the x402 HTTP protocol via Nory.

    Supports Solana and 7 EVM chains (Base, Polygon, Arbitrum, Optimism,
    Avalanche, Sei, IoTeX) with sub-400ms settlement times.
    """

    name: str = "Nory x402 Payment Toolkit"
    description: str = (
        "Toolkit for AI agents to make payments using the x402 HTTP protocol. "
        "Supports Solana and 7 EVM chains with sub-400ms settlement. "
        "Use when encountering HTTP 402 Payment Required responses."
    )

    def get_tools(self) -> List[BaseTool]:
        """Get all tools in this toolkit.

        Returns:
            List of Nory x402 payment tools.
        """
        return [
            NoryGetPaymentRequirementsTool(),
            NoryVerifyPaymentTool(),
            NorySettlePaymentTool(),
            NoryLookupTransactionTool(),
            NoryHealthCheckTool(),
        ]

    def get_env_keys(self) -> List[ToolConfiguration]:
        """Get configuration keys for this toolkit.

        Returns:
            List of configuration keys.
        """
        return [
            ToolConfiguration(
                key="NORY_API_KEY",
                key_type=ToolConfigKeyType.STRING,
                is_required=False,
                is_secret=True,
            ),
        ]
