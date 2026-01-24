const hre = require("hardhat");

/**
 * 从OCR数据铸造NFT
 * 这个脚本由Python调用，通过环境变量接收参数
 */

async function main() {
  // 从环境变量获取参数
  const contractAddress = process.env.CONTRACT_ADDRESS;
  const billNumber = process.env.BILL_NUMBER;
  const ipfsHash = process.env.IPFS_HASH;
  const dataHash = process.env.DATA_HASH;
  const shipperAddress = process.env.SHIPPER_ADDRESS;

  // 验证参数
  if (!contractAddress) {
    console.error("❌ 缺少 CONTRACT_ADDRESS 环境变量");
    process.exit(1);
  }

  if (!billNumber || !ipfsHash || !dataHash) {
    console.error("❌ 缺少必需参数: BILL_NUMBER, IPFS_HASH, DATA_HASH");
    process.exit(1);
  }

  console.log("=== 从OCR数据铸造NFT ===\n");

  // 连接合约 - 使用v2版本（18位Token ID）
  const BillOfLadingNFT = await hre.ethers.getContractFactory("contracts/BillOfLadingNFT_v2.sol:BillOfLadingNFT");
  const contract = BillOfLadingNFT.attach(contractAddress);
  
  // 获取签名者
  const [signer] = await hre.ethers.getSigners();
  const targetShipper = shipperAddress || signer.address;

  console.log("合约地址:", contractAddress);
  console.log("铸造人地址:", signer.address);
  console.log("托运人地址:", targetShipper);
  console.log("提单编号:", billNumber);
  console.log("IPFS哈希:", ipfsHash);
  console.log("数据哈希:", dataHash);

  // 构建tokenURI
  const tokenURI = `ipfs://${ipfsHash}`;

  try {
    // 铸造NFT
    console.log("\n正在铸造NFT...");
    const tx = await contract.mintBill(
      targetShipper,
      billNumber,
      ipfsHash,
      dataHash,
      tokenURI
    );

    console.log("交易已发送，哈希:", tx.hash);
    console.log("等待确认...");

    const receipt = await tx.wait();
    console.log("✅ 交易已确认!");
    console.log("Gas使用量:", receipt.gasUsed.toString());

    // 从事件中获取Token ID
    let tokenId;
    for (const log of receipt.logs) {
      try {
        const parsed = contract.interface.parseLog(log);
        if (parsed && parsed.name === 'Transfer') {
          tokenId = parsed.args[2].toString();
          break;
        }
      } catch (e) {
        // 忽略无法解析的日志
      }
    }

    if (tokenId) {
      console.log("Token ID:", tokenId);
      
      // 验证NFT数据
      const billData = await contract.getBillData(tokenId);
      console.log("\n验证链上数据:");
      console.log("- 提单编号:", billData.billNumber);
      console.log("- IPFS哈希:", billData.ipfsHash);
      console.log("- 数据哈希:", billData.dataHash);
      console.log("- 托运人:", billData.shipper);
    }

    console.log("\n🎉 NFT铸造成功!");
    
    // 返回JSON格式结果供Python解析
    const result = {
      success: true,
      transactionHash: receipt.hash,
      tokenId: tokenId,
      gasUsed: receipt.gasUsed.toString(),
      blockNumber: receipt.blockNumber
    };
    
    console.log("\n" + JSON.stringify(result, null, 2));

  } catch (error) {
    console.error("❌ 铸造失败:", error.message);
    
    // 返回错误信息
    const errorResult = {
      success: false,
      error: error.message
    };
    
    console.log("\n" + JSON.stringify(errorResult, null, 2));
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
