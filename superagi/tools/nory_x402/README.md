# Nory x402 Payment Tools

Tools for AI agents to make payments using the x402 HTTP protocol.

## Features

- **Multi-chain Support**: Solana and 7 EVM chains (Base, Polygon, Arbitrum, Optimism, Avalanche, Sei, IoTeX)
- **Fast Settlement**: Sub-400ms payment settlement
- **x402 Protocol**: Native HTTP payment protocol for AI agents

## Tools

### NoryGetPaymentRequirementsTool
Get x402 payment requirements for accessing a paid resource. Use when you encounter HTTP 402 Payment Required responses.

### NoryVerifyPaymentTool
Verify a signed payment transaction before submitting to the blockchain.

### NorySettlePaymentTool
Settle a payment on-chain with ~400ms settlement time.

### NoryLookupTransactionTool
Look up the status of a previously submitted payment transaction.

### NoryHealthCheckTool
Check Nory service health and see supported networks.

## Configuration

Optional configuration key:
- `NORY_API_KEY`: API key for authenticated endpoints (optional for public endpoints)

## Links

- Website: https://noryx402.com
- x402 Protocol: https://www.x402.org/
