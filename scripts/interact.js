const hre = require("hardhat");

async function main() {
  // 替换为你部署的合约地址
  const contractAddress = process.env.CONTRACT_ADDRESS || "YOUR_CONTRACT_ADDRESS_HERE";
  
  if (contractAddress === "YOUR_CONTRACT_ADDRESS_HERE") {
    console.error("请先设置 CONTRACT_ADDRESS 环境变量或修改脚本中的地址");
    process.exit(1);
  }
  
  console.log("连接到合约:", contractAddress);
  
  // 获取合约实例
  const BillOfLadingNFT = await hre.ethers.getContractFactory("BillOfLadingNFT");
  const contract = BillOfLadingNFT.attach(contractAddress);
  
  // 获取签名者
  const signers = await hre.ethers.getSigners();
  const owner = signers[0];
  const shipper = signers[0]; // 测试网使用同一账户
  const financier = signers[0];
  
  console.log("\n测试账户:");
  console.log("Owner:", owner.address);
  console.log("测试将使用同一账户进行所有操作");
  
  try {
    // 1. 铸造提单NFT
    console.log("\n=== 测试1: 铸造提单NFT ===");
    const billNumber = "BOL-2026-001";
    const ipfsHash = "QmTest123456789"; // 示例IPFS哈希
    const dataHash = "0x" + require('crypto').createHash('sha256').update('test data').digest('hex');
    const tokenURI = `ipfs://${ipfsHash}`;
    
    console.log("铸造提单:", billNumber);
    const mintTx = await contract.mintBill(
      shipper.address,
      billNumber,
      ipfsHash,
      dataHash,
      tokenURI
    );
    await mintTx.wait();
    console.log("✅ 铸造成功! 交易哈希:", mintTx.hash);
    
    // 获取tokenId
    const tokenId = await contract.billNumberToTokenId(billNumber);
    console.log("Token ID:", tokenId.toString());
    
    // 2. 查询提单信息
    console.log("\n=== 测试2: 查询提单信息 ===");
    const billData = await contract.getBillData(tokenId);
    console.log("提单编号:", billData.billNumber);
    console.log("IPFS哈希:", billData.ipfsHash);
    console.log("所有者:", await contract.ownerOf(tokenId));
    console.log("是否已融资:", billData.isFinanced);
    
    // 3. 测试融资功能
    console.log("\n=== 测试3: 抵押融资 ===");
    const financedAmount = hre.ethers.parseEther("100"); // 100 ETH
    
    // 使用shipper账户进行抵押
    const shipperContract = contract.connect(shipper);
    const financeTx = await shipperContract.pledgeForFinancing(
      tokenId,
      financier.address,
      financedAmount
    );
    await financeTx.wait();
    console.log("✅ 抵押成功! 交易哈希:", financeTx.hash);
    
    // 验证融资状态
    const billDataAfterFinance = await contract.getBillData(tokenId);
    console.log("融资方:", billDataAfterFinance.financier);
    console.log("融资金额:", hre.ethers.formatEther(billDataAfterFinance.financedAmount), "ETH");
    console.log("是否可转移:", await contract.isTransferable(tokenId));
    
    // 4. 测试释放货权
    console.log("\n=== 测试4: 释放货权 ===");
    const financierContract = contract.connect(financier);
    const releaseTx = await financierContract.releaseOwnership(tokenId);
    await releaseTx.wait();
    console.log("✅ 货权释放成功! 交易哈希:", releaseTx.hash);
    
    const billDataAfterRelease = await contract.getBillData(tokenId);
    console.log("是否已释放:", billDataAfterRelease.isReleased);
    console.log("是否可转移:", await contract.isTransferable(tokenId));
    
    // 5. 测试转移
    console.log("\n=== 测试5: 转移提单 ===");
    const newOwner = financier.address;
    const transferTx = await shipperContract.transferFrom(shipper.address, newOwner, tokenId);
    await transferTx.wait();
    console.log("✅ 转移成功! 交易哈希:", transferTx.hash);
    console.log("新所有者:", await contract.ownerOf(tokenId));
    
    console.log("\n=== 所有测试完成 ===");
    
  } catch (error) {
    console.error("\n❌ 测试失败:", error.message);
    throw error;
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
