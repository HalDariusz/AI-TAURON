// Chaincode: compliance-registry
// Hyperledger Fabric smart contract for AI-TAURON compliance report registry.
//
// Each record stores a tamper-evident fingerprint of a compliance report:
//   - reportId:      unique report identifier
//   - documentId:    analyzed document identifier
//   - reportHash:    SHA-256 hash of the full report JSON
//   - verdict:       "compliant" or "non_compliant"
//   - findingsCount: number of compliance findings
//   - timestamp:     ISO 8601 analysis timestamp
//   - registeredAt:  ledger timestamp (set by chaincode)

package main

import (
	"encoding/json"
	"fmt"
	"strconv"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// ComplianceReport represents an on-chain compliance report record.
type ComplianceReport struct {
	ReportID      string `json:"reportId"`
	DocumentID    string `json:"documentId"`
	ReportHash    string `json:"reportHash"`
	Verdict       string `json:"verdict"`
	FindingsCount int    `json:"findingsCount"`
	Timestamp     string `json:"timestamp"`
	RegisteredAt  string `json:"registeredAt"`
}

// ComplianceRegistryContract implements the compliance report registry.
type ComplianceRegistryContract struct {
	contractapi.Contract
}

// RegisterReport stores a new compliance report record on the ledger.
func (c *ComplianceRegistryContract) RegisterReport(
	ctx contractapi.TransactionContextInterface,
	reportID string,
	documentID string,
	reportHash string,
	verdict string,
	findingsCountStr string,
	timestamp string,
) error {
	// Check if report already exists (immutability)
	existing, err := ctx.GetStub().GetState(reportID)
	if err != nil {
		return fmt.Errorf("failed to read state: %v", err)
	}
	if existing != nil {
		return fmt.Errorf("report %s already registered — records are immutable", reportID)
	}

	// Validate inputs
	if reportID == "" || documentID == "" || reportHash == "" {
		return fmt.Errorf("reportId, documentId, and reportHash are required")
	}
	if verdict != "compliant" && verdict != "non_compliant" {
		return fmt.Errorf("verdict must be 'compliant' or 'non_compliant'")
	}
	findingsCount, err := strconv.Atoi(findingsCountStr)
	if err != nil {
		return fmt.Errorf("findingsCount must be an integer: %v", err)
	}

	report := ComplianceReport{
		ReportID:      reportID,
		DocumentID:    documentID,
		ReportHash:    reportHash,
		Verdict:       verdict,
		FindingsCount: findingsCount,
		Timestamp:     timestamp,
		RegisteredAt:  time.Now().UTC().Format(time.RFC3339),
	}

	reportJSON, err := json.Marshal(report)
	if err != nil {
		return fmt.Errorf("failed to marshal report: %v", err)
	}

	return ctx.GetStub().PutState(reportID, reportJSON)
}

// GetReport retrieves a compliance report record from the ledger.
func (c *ComplianceRegistryContract) GetReport(
	ctx contractapi.TransactionContextInterface,
	reportID string,
) (*ComplianceReport, error) {
	reportJSON, err := ctx.GetStub().GetState(reportID)
	if err != nil {
		return nil, fmt.Errorf("failed to read state: %v", err)
	}
	if reportJSON == nil {
		return nil, fmt.Errorf("report %s not found", reportID)
	}

	var report ComplianceReport
	if err := json.Unmarshal(reportJSON, &report); err != nil {
		return nil, fmt.Errorf("failed to unmarshal report: %v", err)
	}
	return &report, nil
}

// VerifyReport checks if a report hash matches the on-chain record.
func (c *ComplianceRegistryContract) VerifyReport(
	ctx contractapi.TransactionContextInterface,
	reportID string,
	reportHash string,
) (bool, error) {
	report, err := c.GetReport(ctx, reportID)
	if err != nil {
		return false, err
	}
	return report.ReportHash == reportHash, nil
}

// GetAllReports returns all compliance report records (for audit).
func (c *ComplianceRegistryContract) GetAllReports(
	ctx contractapi.TransactionContextInterface,
) ([]*ComplianceReport, error) {
	iterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, fmt.Errorf("failed to get state range: %v", err)
	}
	defer iterator.Close()

	var reports []*ComplianceReport
	for iterator.HasNext() {
		result, err := iterator.Next()
		if err != nil {
			return nil, err
		}
		var report ComplianceReport
		if err := json.Unmarshal(result.Value, &report); err != nil {
			continue
		}
		reports = append(reports, &report)
	}
	return reports, nil
}

func main() {
	chaincode, err := contractapi.NewChaincode(&ComplianceRegistryContract{})
	if err != nil {
		panic(fmt.Sprintf("Error creating chaincode: %v", err))
	}
	if err := chaincode.Start(); err != nil {
		panic(fmt.Sprintf("Error starting chaincode: %v", err))
	}
}
