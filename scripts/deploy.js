const hre = require("hardhat");

async function main() {
  console.log("开始部署 BillOfLadingNFT 合约...");
  
  // 获取部署账户
  const [deployer] = await hre.ethers.getSigners();
  console.log("部署账户:", deployer.address);
  
  // 检查账户余额
  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("账户余额:", hre.ethers.formatEther(balance), "ETH");
  
  // 部署合约
  const BillOfLadingNFT = await hre.ethers.getContractFactory("BillOfLadingNFT");
  const contract = await BillOfLadingNFT.deploy();
  
  await contract.waitForDeployment();
  
  const contractAddress = await contract.getAddress();
  console.log("✅ 合约部署成功!");
  console.log("合约地址:", contractAddress);
  console.log("区块链网络:", hre.network.name);
  
  // 保存部署信息
  const deployInfo = {
    network: hre.network.name,
    contractAddress: contractAddress,
    deployer: deployer.address,
    timestamp: new Date().toISOString(),
    blockNumber: await hre.ethers.provider.getBlockNumber()
  };
  
  console.log("\n部署信息:");
  console.log(JSON.stringify(deployInfo, null, 2));
  
  // 如果是测试网或主网，等待区块确认后验证合约
  if (hre.network.name !== "localhost" && hre.network.name !== "hardhat") {
    console.log("\n等待区块确认...");
    await contract.deploymentTransaction().wait(6); // 等待6个区块确认
    
    console.log("\n要验证合约，请运行:");
    console.log(`npx hardhat verify --network ${hre.network.name} ${contractAddress}`);
  }
  
  return contractAddress;
}

// 执行部署
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
