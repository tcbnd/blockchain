const hre = require("hardhat");

/**
 * Check if a bill number already exists and get its Token ID
 * Called by Python when "Bill already exists" error occurs
 */

async function main() {
  const contractAddress = process.env.CONTRACT_ADDRESS;
  const billNumber = process.env.BILL_NUMBER;

  if (!contractAddress || !billNumber) {
    console.error("❌ Missing required parameters");
    process.exit(1);
  }

  try {
    // Connect to contract - use v2 version (18 digit Token ID)
    const BillOfLadingNFT = await hre.ethers.getContractFactory("contracts/BillOfLadingNFT_v2.sol:BillOfLadingNFT");
    const contract = BillOfLadingNFT.attach(contractAddress);

    // Check if bill exists
    const tokenId = await contract.billNumberToTokenId(billNumber);
    
    if (tokenId.toString() !== "0") {
      // Bill exists, get its data
      const billData = await contract.getBillData(tokenId);
      const owner = await contract.ownerOf(tokenId);
      
      console.log("\n✅ 提單已存在");
      console.log("Token ID:", tokenId.toString());
      console.log("Owner:", owner);
      console.log("IPFS Hash:", billData.ipfsHash);
      console.log("Is Financed:", billData.isFinanced);
      console.log("Timestamp:", billData.timestamp.toString());
      
      // Output in format Python can parse
      console.log("\n=== EXISTING_BILL_DATA ===");
      console.log(JSON.stringify({
        tokenId: tokenId.toString(),
        billNumber: billNumber,
        ipfsHash: billData.ipfsHash,
        owner: owner,
        isFinanced: billData.isFinanced,
        timestamp: billData.timestamp.toString()
      }));
      console.log("=== END_DATA ===");
      
    } else {
      console.log("❌ 提單不存在 (Token ID = 0)");
      process.exit(1);
    }
    
  } catch (error) {
    console.error("❌ 查詢失敗:", error.message);
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
