"""Nory x402 Payment Tools for SuperAGI.

Tools for AI agents to make payments using the x402 HTTP protocol.
Supports Solana and 7 EVM chains with sub-400ms settlement.
"""

import json
import requests
from typing import Type, Optional, Literal

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool


NORY_API_BASE = "https://noryx402.com"


class NoryGetPaymentRequirementsSchema(BaseModel):
    """Schema for NoryGetPaymentRequirementsTool."""

    resource: str = Field(
        ...,
        description="The resource path requiring payment (e.g., /api/premium/data).",
    )
    amount: str = Field(
        ...,
        description="Amount in human-readable format (e.g., '0.10' for $0.10 USDC).",
    )
    network: Optional[str] = Field(
        None,
        description="Preferred blockchain network. Options: solana-mainnet, solana-devnet, base-mainnet, polygon-mainnet, arbitrum-mainnet, optimism-mainnet, avalanche-mainnet, sei-mainnet, iotex-mainnet.",
    )


class NoryGetPaymentRequirementsTool(BaseTool):
    """
    Tool to get x402 payment requirements for accessing a paid resource.

    Use this when you encounter an HTTP 402 Payment Required response
    and need to know how much to pay and where to send payment.
    """

    name = "NoryGetPaymentRequirements"
    description = (
        "Get x402 payment requirements for accessing a paid resource. "
        "Returns payment requirements including amount, supported networks, and wallet address. "
        "Supports Solana and 7 EVM chains (Base, Polygon, Arbitrum, Optimism, Avalanche, Sei, IoTeX) "
        "with sub-400ms settlement."
    )
    args_schema: Type[NoryGetPaymentRequirementsSchema] = NoryGetPaymentRequirementsSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, resource: str, amount: str, network: Optional[str] = None) -> str:
        """Execute the tool to get payment requirements.

        Args:
            resource: The resource path requiring payment.
            amount: Amount in human-readable format.
            network: Preferred blockchain network (optional).

        Returns:
            JSON string with payment requirements.
        """
        params = {"resource": resource, "amount": amount}
        if network:
            params["network"] = network

        api_key = self.get_tool_config("NORY_API_KEY")
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        response = requests.get(
            f"{NORY_API_BASE}/api/x402/requirements",
            params=params,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)


class NoryVerifyPaymentSchema(BaseModel):
    """Schema for NoryVerifyPaymentTool."""

    payload: str = Field(
        ...,
        description="Base64-encoded payment payload containing signed transaction.",
    )


class NoryVerifyPaymentTool(BaseTool):
    """
    Tool to verify a signed payment transaction before settlement.

    Use this to validate that a payment transaction is correct
    before submitting it to the blockchain.
    """

    name = "NoryVerifyPayment"
    description = (
        "Verify a signed payment transaction before submitting to the blockchain. "
        "Returns verification result including validity and payer info."
    )
    args_schema: Type[NoryVerifyPaymentSchema] = NoryVerifyPaymentSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, payload: str) -> str:
        """Execute the tool to verify a payment.

        Args:
            payload: Base64-encoded payment payload.

        Returns:
            JSON string with verification result.
        """
        api_key = self.get_tool_config("NORY_API_KEY")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        response = requests.post(
            f"{NORY_API_BASE}/api/x402/verify",
            json={"payload": payload},
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)


class NorySettlePaymentSchema(BaseModel):
    """Schema for NorySettlePaymentTool."""

    payload: str = Field(
        ...,
        description="Base64-encoded payment payload.",
    )


class NorySettlePaymentTool(BaseTool):
    """
    Tool to settle a payment on-chain.

    Use this to submit a verified payment transaction to the blockchain.
    Settlement typically completes in under 400ms.
    """

    name = "NorySettlePayment"
    description = (
        "Settle a payment on-chain with ~400ms settlement time. "
        "Returns settlement result including transaction ID."
    )
    args_schema: Type[NorySettlePaymentSchema] = NorySettlePaymentSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, payload: str) -> str:
        """Execute the tool to settle a payment.

        Args:
            payload: Base64-encoded payment payload.

        Returns:
            JSON string with settlement result.
        """
        api_key = self.get_tool_config("NORY_API_KEY")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        response = requests.post(
            f"{NORY_API_BASE}/api/x402/settle",
            json={"payload": payload},
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)


class NoryLookupTransactionSchema(BaseModel):
    """Schema for NoryLookupTransactionTool."""

    transaction_id: str = Field(
        ...,
        description="Transaction ID or signature.",
    )
    network: str = Field(
        ...,
        description="Network where the transaction was submitted. Options: solana-mainnet, solana-devnet, base-mainnet, polygon-mainnet, arbitrum-mainnet, optimism-mainnet, avalanche-mainnet, sei-mainnet, iotex-mainnet.",
    )


class NoryLookupTransactionTool(BaseTool):
    """
    Tool to look up transaction status.

    Use this to check the status of a previously submitted payment
    including confirmations and current state.
    """

    name = "NoryLookupTransaction"
    description = (
        "Look up the status of a previously submitted payment transaction. "
        "Returns transaction status (pending, confirmed, failed) and confirmations."
    )
    args_schema: Type[NoryLookupTransactionSchema] = NoryLookupTransactionSchema

    class Config:
        arbitrary_types_allowed = True

    def _execute(self, transaction_id: str, network: str) -> str:
        """Execute the tool to look up a transaction.

        Args:
            transaction_id: Transaction ID or signature.
            network: Network where the transaction was submitted.

        Returns:
            JSON string with transaction status.
        """
        api_key = self.get_tool_config("NORY_API_KEY")
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        response = requests.get(
            f"{NORY_API_BASE}/api/x402/transactions/{transaction_id}",
            params={"network": network},
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)


class NoryHealthCheckSchema(BaseModel):
    """Schema for NoryHealthCheckTool - no inputs required."""

    pass


class NoryHealthCheckTool(BaseTool):
    """
    Tool to check Nory service health.

    Use this to verify the payment service is operational
    before attempting payments.
    """

    name = "NoryHealthCheck"
    description = (
        "Check Nory service health and see supported blockchain networks. "
        "Returns health status and list of available networks."
    )
    args_schema: Type[NoryHealthCheckSchema] = NoryHealthCheckSchema
    permission_required: bool = False

    class Config:
        arbitrary_types_allowed = True

    def _execute(self) -> str:
        """Execute the tool to check service health.

        Returns:
            JSON string with health status and supported networks.
        """
        response = requests.get(
            f"{NORY_API_BASE}/api/x402/health",
            timeout=30,
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)
