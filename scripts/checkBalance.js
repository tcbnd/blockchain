const hre = require("hardhat");
require("dotenv").config();

async function main() {
  try {
    const [signer] = await hre.ethers.getSigners();
    const address = await signer.getAddress();
    const balance = await hre.ethers.provider.getBalance(address);
    
    console.log("=====================================");
    console.log("网络:", hre.network.name);
    console.log("钱包地址:", address);
    console.log("余额:", hre.ethers.formatEther(balance), "ETH");
    console.log("=====================================");
    
    if (balance === 0n) {
      console.log("\n⚠️  余额为0，需要获取测试币！");
      console.log("\n请访问以下水龙头获取 Sepolia 测试币：");
      console.log("1. https://www.alchemy.com/faucets/ethereum-sepolia");
      console.log("2. https://faucet.quicknode.com/ethereum/sepolia");
      console.log("3. https://www.infura.io/faucet/sepolia");
      console.log("\n输入你的地址:", address);
    } else {
      console.log("\n✅ 余额充足，可以部署合约了！");
    }
    
  } catch (error) {
    console.error("❌ 错误:", error.message);
    
    if (error.message.includes("invalid private key")) {
      console.log("\n请检查 .env 文件中的 PRIVATE_KEY 是否正确");
    }
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
