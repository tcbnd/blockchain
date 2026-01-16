const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

/**
 * Script to generate contract configuration for frontend
 * Extracts deployed contract address and ABI
 */
async function main() {
    const network = hre.network.name;
    console.log(`\n🔍 Getting contract info for network: ${network}`);
    
    try {
        // Get the contract factory
        const BillOfLadingNFT = await hre.ethers.getContractFactory("BillOfLadingNFT");
        
        // Read deployed address from deployment file
        const deploymentFile = path.join(__dirname, `../deployments/${network}.json`);
        
        if (!fs.existsSync(deploymentFile)) {
            console.log("❌ No deployment found for this network.");
            console.log(`   Please deploy first using: npm run deploy:${network}`);
            return;
        }
        
        const deployment = JSON.parse(fs.readFileSync(deploymentFile, 'utf8'));
        const contractAddress = deployment.address;
        
        console.log(`\n📍 Contract Address: ${contractAddress}`);
        
        // Get contract ABI
        const artifact = await hre.artifacts.readArtifact("BillOfLadingNFT");
        const abi = artifact.abi;
        
        // Generate frontend config
        const frontendConfig = {
            contractAddress: contractAddress,
            network: network,
            chainId: hre.network.config.chainId,
            abi: abi
        };
        
        // Save to frontend directory
        const frontendDir = path.join(__dirname, "../frontend");
        if (!fs.existsSync(frontendDir)) {
            fs.mkdirSync(frontendDir, { recursive: true });
        }
        
        const configPath = path.join(frontendDir, "contract-info.json");
        fs.writeFileSync(configPath, JSON.stringify(frontendConfig, null, 2));
        
        console.log(`\n✅ Contract info saved to: ${configPath}`);
        
        // Generate simplified ABI for frontend (human-readable format)
        const humanReadableAbi = abi
            .filter(item => item.type === 'function' || item.type === 'event')
            .map(item => {
                if (item.type === 'function') {
                    const inputs = item.inputs.map(i => `${i.type} ${i.name}`).join(', ');
                    const outputs = item.outputs ? item.outputs.map(o => o.type).join(', ') : '';
                    const stateMutability = item.stateMutability === 'view' || item.stateMutability === 'pure' ? ' view' : '';
                    return `function ${item.name}(${inputs})${stateMutability}${outputs ? ' returns (' + outputs + ')' : ''}`;
                } else if (item.type === 'event') {
                    const inputs = item.inputs
                        .map(i => `${i.indexed ? 'indexed ' : ''}${i.type} ${i.name}`)
                        .join(', ');
                    return `event ${item.name}(${inputs})`;
                }
            });
        
        console.log("\n📝 Human-Readable ABI:");
        console.log(JSON.stringify(humanReadableAbi, null, 2));
        
        // Display setup instructions
        console.log("\n" + "=".repeat(60));
        console.log("📋 FRONTEND SETUP INSTRUCTIONS");
        console.log("=".repeat(60));
        console.log("\n1. Update frontend/config.js with:");
        console.log(`   CONTRACT_ADDRESS: "${contractAddress}"`);
        console.log("\n2. Start a local server:");
        console.log("   cd frontend");
        console.log("   python3 -m http.server 8000");
        console.log("\n3. Open in browser:");
        console.log("   http://localhost:8000");
        console.log("\n4. Connect your MetaMask to:");
        console.log(`   Network: ${network}`);
        console.log(`   Chain ID: ${hre.network.config.chainId}`);
        console.log("\n" + "=".repeat(60));
        
    } catch (error) {
        console.error("❌ Error:", error);
    }
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
