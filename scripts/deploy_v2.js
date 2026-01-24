const hre = require("hardhat");

async function main() {
  console.log("正在部署 BillOfLadingNFT v2 (18位Token ID)...\n");

  const [deployer] = await hre.ethers.getSigners();
  console.log("部署账户:", deployer.address);
  console.log("账户余额:", (await hre.ethers.provider.getBalance(deployer.address)).toString(), "wei\n");

  // 部署合约 - 使用完整限定名称指定v2版本
  const BillOfLadingNFT = await hre.ethers.getContractFactory("contracts/BillOfLadingNFT_v2.sol:BillOfLadingNFT");
  const contract = await BillOfLadingNFT.deploy();

  await contract.waitForDeployment();
  const contractAddress = await contract.getAddress();

  console.log("✅ 合约部署成功!");
  console.log("合约地址:", contractAddress);
  console.log("\n⚠️  重要: 请将此地址更新到 .env 文件中的 CONTRACT_ADDRESS");
  console.log("\n网络:", hre.network.name);
  console.log("查看合约:", `https://sepolia.etherscan.io/address/${contractAddress}`);
  
  // 测试铸造一个NFT以验证Token ID格式
  console.log("\n正在测试铸造NFT以验证Token ID...");
  const testBillNumber = `TEST${Date.now()}`;
  const testIpfsHash = "QmTest123456789";
  const testDataHash = "0xtest123";
  const testTokenURI = `ipfs://${testIpfsHash}`;
  
  const mintTx = await contract.mintBill(
    deployer.address,
    testBillNumber,
    testIpfsHash,
    testDataHash,
    testTokenURI
  );
  
  const receipt = await mintTx.wait();
  
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
      // 忽略
    }
  }
  
  console.log("✅ 测试NFT已铸造!");
  console.log("Token ID:", tokenId);
  console.log("Token ID长度:", tokenId.length, "位数字");
  
  if (tokenId.length === 18) {
    console.log("✅ Token ID格式正确 (18位)");
  } else {
    console.log("⚠️  Token ID格式不符合预期");
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
