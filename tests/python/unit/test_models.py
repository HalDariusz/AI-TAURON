"""Tests for domain models."""

from src.domain.models import (
    ComplianceReport,
    Document,
    DocumentType,
    Finding,
    Severity,
)


def test_document_creation():
    doc = Document(filename="test.pdf", document_type=DocumentType.CONTRACT)
    assert doc.id
    assert doc.filename == "test.pdf"
    assert doc.document_type == DocumentType.CONTRACT
    assert doc.chunks == []
    assert doc.raw_text == ""


def test_compliance_report_counts():
    findings = [
        Finding(
            clause_text="clause1",
            regulation_ref="Art. 1",
            description="desc",
            severity=Severity.CRITICAL,
            recommendation="fix",
        ),
        Finding(
            clause_text="clause2",
            regulation_ref="Art. 2",
            description="desc",
            severity=Severity.HIGH,
            recommendation="fix",
        ),
        Finding(
            clause_text="clause3",
            regulation_ref="Art. 3",
            description="desc",
            severity=Severity.HIGH,
            recommendation="fix",
        ),
        Finding(
            clause_text="clause4",
            regulation_ref="Art. 4",
            description="desc",
            severity=Severity.LOW,
            recommendation="fix",
        ),
    ]
    report = ComplianceReport(
        document_id="doc1",
        document_name="test.pdf",
        findings=findings,
    )

    assert report.total_findings == 4
    assert report.critical_count == 1
    assert report.high_count == 2
    assert report.low_count == 1
    assert report.medium_count == 0


def test_compliance_report_empty():
    report = ComplianceReport(
        document_id="doc1",
        document_name="test.pdf",
    )
    assert report.total_findings == 0
    assert report.critical_count == 0


def test_severity_enum_values():
    assert Severity.CRITICAL == "critical"
    assert Severity.HIGH == "high"
    assert Severity.MEDIUM == "medium"
    assert Severity.LOW == "low"


def test_document_type_enum_values():
    assert DocumentType.LEGAL_ACT == "legal_act"
    assert DocumentType.OWU == "owu"
    assert DocumentType.CONTRACT == "contract"
