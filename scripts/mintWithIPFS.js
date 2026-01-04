const hre = require("hardhat");
const { uploadBillToIPFS } = require('./uploadToIPFS');

/**
 * 完整流程：上传IPFS + 铸造NFT
 * 这个脚本演示如何将提单数据上传到IPFS后铸造NFT
 */

async function main() {
  // 1. 合约地址（需要先部署合约）
  const contractAddress = process.env.CONTRACT_ADDRESS || "YOUR_CONTRACT_ADDRESS_HERE";
  
  if (contractAddress === "YOUR_CONTRACT_ADDRESS_HERE") {
    console.error("❌ 请先设置 CONTRACT_ADDRESS 环境变量");
    console.log("提示: 先运行 npm run deploy:mumbai 部署合约");
    process.exit(1);
  }
  
  console.log("=== 提单NFT铸造流程 ===\n");
  
  // 2. 准备提单数据（从OCR系统获取）
  const billData = {
    billNumber: "BOL-2026-" + Date.now(),
    shipper: "ABC Trading Co., Ltd.",
    consignee: "XYZ Import Export Inc.",
    vessel: "COSCO SHIPPING GEMINI",
    portOfLoading: "Shanghai, China",
    portOfDischarge: "Los Angeles, USA",
    cargoDescription: "Electronics and Components - 100 Cartons",
    issueDate: new Date().toISOString().split('T')[0],
    weight: "2000 KG",
    volume: "50 CBM"
  };
  
  console.log("步骤1: 准备提单数据");
  console.log("提单编号:", billData.billNumber);
  
  // 3. 上传到IPFS
  console.log("\n步骤2: 上传到IPFS");
  const ipfsResult = await uploadBillToIPFS(billData);
  console.log("IPFS哈希:", ipfsResult.ipfsHash);
  console.log("数据哈希:", ipfsResult.dataHash);
  
  // 4. 连接智能合约
  console.log("\n步骤3: 连接智能合约");
  const BillOfLadingNFT = await hre.ethers.getContractFactory("BillOfLadingNFT");
  const contract = BillOfLadingNFT.attach(contractAddress);
  console.log("合约地址:", contractAddress);
  
  // 5. 获取签名者（托运人地址）
  const signers = await hre.ethers.getSigners();
  const owner = signers[0];
  const shipper = signers[0]; // 使用同一账户
  console.log("合约所有者:", owner.address);
  console.log("托运人地址:", shipper.address);
  
  // 6. 铸造NFT
  console.log("\n步骤4: 铸造NFT");
  const tokenURI = `ipfs://${ipfsResult.ipfsHash}`;
  
  const mintTx = await contract.mintBill(
    shipper.address,
    billData.billNumber,
    ipfsResult.ipfsHash,
    "0x" + ipfsResult.dataHash,
    tokenURI
  );
  
  console.log("交易已发送，等待确认...");
  const receipt = await mintTx.wait();
  
  console.log("✅ NFT铸造成功!");
  console.log("交易哈希:", receipt.hash);
  console.log("Gas使用量:", receipt.gasUsed.toString());
  
  // 7. 从交易receipt获取事件来得到Token ID
  const events = receipt.logs;
  let tokenId;
  
  // 查找 Transfer 事件来获取 tokenId
  for (const log of events) {
    try {
      const parsed = contract.interface.parseLog(log);
      if (parsed && parsed.name === 'Transfer') {
        tokenId = parsed.args[2]; // tokenId is the 3rd argument
        break;
      }
    } catch (e) {
      // 忽略无法解析的日志
    }
  }
  
  console.log("Token ID:", tokenId ? tokenId.toString() : "未找到");
  
  // 8. 验证NFT信息
  if (tokenId) {
    console.log("\n步骤5: 验证NFT信息");
    const nftData = await contract.getBillData(tokenId);
    console.log("链上提单编号:", nftData.billNumber);
    console.log("链上IPFS哈希:", nftData.ipfsHash);
    console.log("NFT所有者:", await contract.ownerOf(tokenId));
    console.log("Token URI:", await contract.tokenURI(tokenId));
    
    // 9. 验证数据完整性
    const isValid = await contract.verifyBillData(tokenId, "0x" + ipfsResult.dataHash);
    console.log("数据完整性:", isValid ? "✅ 验证通过" : "❌ 验证失败");
  }
  
  console.log("\n=== 完整流程执行完毕 ===");
  
  if (tokenId) {
    console.log("\n你可以在区块链浏览器查看NFT:");
    console.log(`https://sepolia.etherscan.io/token/${contractAddress}?a=${tokenId}`);
  }
  
  console.log("\n你可以在IPFS网关查看元数据:");
  console.log(ipfsResult.gatewayUrl);
  
  return {
    tokenId: tokenId ? tokenId.toString() : null,
    ipfsHash: ipfsResult.ipfsHash,
    contractAddress,
    transactionHash: receipt.hash
  };
}

main()
  .then((result) => {
    console.log("\n=== 铸造结果 ===");
    console.log(JSON.stringify(result, null, 2));
    process.exit(0);
  })
  .catch((error) => {
    console.error("\n❌ 执行失败:", error);
    process.exit(1);
  });
