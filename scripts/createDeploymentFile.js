const fs = require("fs");
const path = require("path");

/**
 * Helper script to create deployment file structure
 * Run after deploying a contract
 */

// Usage: node scripts/createDeploymentFile.js <network> <address> <txHash>
const network = process.argv[2];
const address = process.argv[3];
const txHash = process.argv[4];

if (!network || !address) {
    console.log("Usage: node createDeploymentFile.js <network> <address> [txHash]");
    console.log("Example: node createDeploymentFile.js amoy 0x123... 0xabc...");
    process.exit(1);
}

const deploymentData = {
    address: address,
    network: network,
    deployedAt: new Date().toISOString(),
    transactionHash: txHash || "N/A"
};

const deploymentsDir = path.join(__dirname, "../deployments");
if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
}

const filePath = path.join(deploymentsDir, `${network}.json`);
fs.writeFileSync(filePath, JSON.stringify(deploymentData, null, 2));

console.log(`✅ Deployment file created: ${filePath}`);
console.log(JSON.stringify(deploymentData, null, 2));
