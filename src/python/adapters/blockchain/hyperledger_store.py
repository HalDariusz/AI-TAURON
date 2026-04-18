"""Hyperledger Fabric adapter for compliance report registry.

Each compliance report is registered on-chain with:
- report_id: unique report identifier
- document_id: analyzed document identifier
- report_hash: SHA-256 hash of the full report JSON
- verdict: "compliant" or "non_compliant"
- findings_count: number of findings
- timestamp: ISO 8601 timestamp of analysis

The full report stays off-chain (PostgreSQL). On-chain record serves as
tamper-evident proof of existence — once recorded, cannot be modified.
"""

from __future__ import annotations

import hashlib
import logging

import httpx

from ...domain.models import ComplianceReport

logger = logging.getLogger(__name__)


def compute_report_hash(report: ComplianceReport) -> str:
    """Compute SHA-256 hash of a compliance report."""
    report_json = report.model_dump_json(indent=None)
    return hashlib.sha256(report_json.encode("utf-8")).hexdigest()


class HyperledgerStore:
    """Hyperledger Fabric blockchain adapter via Fabric Gateway REST proxy.

    Communicates with Hyperledger Fabric network through a REST API proxy
    that wraps the Fabric Gateway SDK. The proxy handles peer connection,
    identity management, and transaction submission.

    For MVP: uses a simple REST API contract. In production, switch to
    the native hfc (Hyperledger Fabric Client) Python SDK or gRPC gateway.
    """

    def __init__(
        self,
        gateway_url: str = "http://localhost:3001",
        channel: str = "compliance-channel",
        chaincode: str = "compliance-registry",
    ) -> None:
        self._gateway_url = gateway_url.rstrip("/")
        self._channel = channel
        self._chaincode = chaincode
        self._client = httpx.AsyncClient(timeout=30.0)
        logger.info(
            "HyperledgerStore: gateway=%s, channel=%s, chaincode=%s",
            gateway_url,
            channel,
            chaincode,
        )

    async def register_report(
        self,
        report_id: str,
        document_id: str,
        report_hash: str,
        verdict: str,
        findings_count: int,
        timestamp: str,
    ) -> str:
        """Submit a compliance report record to the blockchain."""
        payload = {
            "function": "RegisterReport",
            "args": [
                report_id,
                document_id,
                report_hash,
                verdict,
                str(findings_count),
                timestamp,
            ],
        }

        try:
            response = await self._client.post(
                f"{self._gateway_url}/api/invoke",
                json={
                    "channel": self._channel,
                    "chaincode": self._chaincode,
                    **payload,
                },
            )
            response.raise_for_status()
            result = response.json()
            tx_id = result.get("transactionId", "unknown")
            logger.info(
                "Report %s registered on blockchain (tx=%s, hash=%s)",
                report_id,
                tx_id,
                report_hash[:16] + "...",
            )
            return tx_id
        except httpx.HTTPError as e:
            logger.error("Blockchain registration failed for report %s: %s", report_id, e)
            raise

    async def verify_report(self, report_id: str, report_hash: str) -> bool:
        """Verify a report hash against the on-chain record."""
        record = await self.get_record(report_id)
        if not record:
            return False
        return record.get("reportHash") == report_hash

    async def get_record(self, report_id: str) -> dict | None:
        """Query the blockchain for a report record."""
        try:
            response = await self._client.post(
                f"{self._gateway_url}/api/query",
                json={
                    "channel": self._channel,
                    "chaincode": self._chaincode,
                    "function": "GetReport",
                    "args": [report_id],
                },
            )
            response.raise_for_status()
            return response.json().get("result")
        except httpx.HTTPError as e:
            logger.error("Blockchain query failed for report %s: %s", report_id, e)
            return None

    async def register_compliance_report(self, report: ComplianceReport) -> str:
        """Convenience: compute hash and register a ComplianceReport."""
        report_hash = compute_report_hash(report)
        verdict = "compliant" if report.total_findings == 0 else "non_compliant"
        timestamp = report.created_at.isoformat()

        return await self.register_report(
            report_id=report.id,
            document_id=report.document_id,
            report_hash=report_hash,
            verdict=verdict,
            findings_count=report.total_findings,
            timestamp=timestamp,
        )

    async def close(self) -> None:
        await self._client.aclose()
