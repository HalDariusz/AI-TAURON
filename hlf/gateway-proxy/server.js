/**
 * AI-TAURON: Hyperledger Fabric REST Gateway Proxy
 *
 * Wraps the Fabric Gateway SDK in a simple REST API that the Python
 * HyperledgerStore adapter can call. Runs on port 3001.
 *
 * Endpoints:
 *   POST /api/invoke  — submit a transaction (write)
 *   POST /api/query   — evaluate a transaction (read)
 *   GET  /api/health   — health check
 */

const { Gateway, Wallets } = require('fabric-network');
const FabricCAServices = require('fabric-ca-client');
const path = require('path');
const fs = require('fs');
const express = require('express');

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 3001;
const TEST_NETWORK_PATH = path.resolve(__dirname, '../fabric-samples/test-network');
const CHANNEL = process.env.CHANNEL || 'compliance-channel';
const WALLET_PATH = path.join(__dirname, 'wallet');

let gateway;
let contract;

async function initGateway() {
    // Load connection profile
    const ccpPath = path.resolve(
        TEST_NETWORK_PATH,
        'organizations/peerOrganizations/org1.example.com/connection-org1.json'
    );
    const ccp = JSON.parse(fs.readFileSync(ccpPath, 'utf8'));

    // Create wallet
    const wallet = await Wallets.newFileSystemWallet(WALLET_PATH);

    // Check if admin identity exists
    const identity = await wallet.get('admin');
    if (!identity) {
        console.log('Enrolling admin...');
        const caInfo = ccp.certificateAuthorities['ca.org1.example.com'];
        const ca = new FabricCAServices(caInfo.url);
        const enrollment = await ca.enroll({
            enrollmentID: 'admin',
            enrollmentSecret: 'adminpw'
        });
        const x509Identity = {
            credentials: {
                certificate: enrollment.certificate,
                privateKey: enrollment.key.toBytes(),
            },
            mspId: 'Org1MSP',
            type: 'X.509',
        };
        await wallet.put('admin', x509Identity);
        console.log('Admin enrolled');
    }

    // Connect gateway
    gateway = new Gateway();
    await gateway.connect(ccp, {
        wallet,
        identity: 'admin',
        discovery: { enabled: true, asLocalhost: true }
    });

    console.log('Gateway connected');
}

async function getContract(chaincodeName) {
    const network = await gateway.getNetwork(CHANNEL);
    return network.getContract(chaincodeName);
}

// --- Health ---
app.get('/api/health', (req, res) => {
    res.json({ status: 'ok', channel: CHANNEL, gateway: !!gateway });
});

// --- Invoke (write) ---
app.post('/api/invoke', async (req, res) => {
    try {
        const { chaincode, function: fn, args } = req.body;
        const contract = await getContract(chaincode);
        const result = await contract.submitTransaction(fn, ...args);
        const txId = contract.gateway
            ? 'submitted'
            : 'submitted';

        res.json({
            status: 'ok',
            transactionId: txId,
            result: result.toString() || null
        });
    } catch (err) {
        console.error('Invoke error:', err.message);
        res.status(500).json({ error: err.message });
    }
});

// --- Query (read) ---
app.post('/api/query', async (req, res) => {
    try {
        const { chaincode, function: fn, args } = req.body;
        const contract = await getContract(chaincode);
        const result = await contract.evaluateTransaction(fn, ...args);

        let parsed;
        try {
            parsed = JSON.parse(result.toString());
        } catch {
            parsed = result.toString();
        }

        res.json({ status: 'ok', result: parsed });
    } catch (err) {
        console.error('Query error:', err.message);
        res.status(500).json({ error: err.message });
    }
});

// --- Start ---
async function main() {
    try {
        await initGateway();
        app.listen(PORT, () => {
            console.log(`Fabric REST proxy listening on port ${PORT}`);
        });
    } catch (err) {
        console.error('Failed to start:', err);
        process.exit(1);
    }
}

main();
