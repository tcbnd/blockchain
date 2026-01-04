const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("BillOfLadingNFT", function () {
  let contract;
  let owner;
  let shipper;
  let financier;
  let other;

  beforeEach(async function () {
    // 获取测试账户
    [owner, shipper, financier, other] = await ethers.getSigners();

    // 部署合约
    const BillOfLadingNFT = await ethers.getContractFactory("BillOfLadingNFT");
    contract = await BillOfLadingNFT.deploy();
    await contract.waitForDeployment();
  });

  describe("部署", function () {
    it("应该设置正确的名称和符号", async function () {
      expect(await contract.name()).to.equal("BillOfLading");
      expect(await contract.symbol()).to.equal("BOL");
    });

    it("应该设置正确的所有者", async function () {
      expect(await contract.owner()).to.equal(owner.address);
    });
  });

  describe("铸造提单", function () {
    it("应该成功铸造新的提单NFT", async function () {
      const billNumber = "BOL-2026-001";
      const ipfsHash = "QmTest123";
      const dataHash = "0x1234567890abcdef";
      const tokenURI = `ipfs://${ipfsHash}`;

      await expect(
        contract.mintBill(shipper.address, billNumber, ipfsHash, dataHash, tokenURI)
      )
        .to.emit(contract, "BillMinted")
        .withArgs(0, shipper.address, billNumber, ipfsHash);

      expect(await contract.ownerOf(0)).to.equal(shipper.address);
      const billData = await contract.getBillData(0);
      expect(billData.billNumber).to.equal(billNumber);
      expect(billData.ipfsHash).to.equal(ipfsHash);
      expect(billData.isFinanced).to.equal(false);
    });

    it("不应该允许重复的提单编号", async function () {
      const billNumber = "BOL-2026-001";
      const ipfsHash = "QmTest123";
      const dataHash = "0x1234567890abcdef";
      const tokenURI = `ipfs://${ipfsHash}`;

      await contract.mintBill(shipper.address, billNumber, ipfsHash, dataHash, tokenURI);

      await expect(
        contract.mintBill(shipper.address, billNumber, ipfsHash, dataHash, tokenURI)
      ).to.be.revertedWith("Bill number already exists");
    });

    it("只有所有者可以铸造", async function () {
      const billNumber = "BOL-2026-001";
      const ipfsHash = "QmTest123";
      const dataHash = "0x1234567890abcdef";
      const tokenURI = `ipfs://${ipfsHash}`;

      await expect(
        contract.connect(other).mintBill(shipper.address, billNumber, ipfsHash, dataHash, tokenURI)
      ).to.be.reverted;
    });
  });

  describe("融资功能", function () {
    let tokenId;

    beforeEach(async function () {
      const billNumber = "BOL-2026-001";
      const ipfsHash = "QmTest123";
      const dataHash = "0x1234567890abcdef";
      const tokenURI = `ipfs://${ipfsHash}`;

      await contract.mintBill(shipper.address, billNumber, ipfsHash, dataHash, tokenURI);
      tokenId = 0;
    });

    it("应该允许所有者抵押提单", async function () {
      const amount = ethers.parseEther("100");

      await expect(
        contract.connect(shipper).pledgeForFinancing(tokenId, financier.address, amount)
      )
        .to.emit(contract, "BillFinanced")
        .withArgs(tokenId, financier.address, amount);

      const billData = await contract.getBillData(tokenId);
      expect(billData.isFinanced).to.equal(true);
      expect(billData.financier).to.equal(financier.address);
      expect(billData.financedAmount).to.equal(amount);
    });

    it("非所有者不能抵押提单", async function () {
      const amount = ethers.parseEther("100");

      await expect(
        contract.connect(other).pledgeForFinancing(tokenId, financier.address, amount)
      ).to.be.revertedWith("Not the owner");
    });

    it("已融资的提单不能再次融资", async function () {
      const amount = ethers.parseEther("100");

      await contract.connect(shipper).pledgeForFinancing(tokenId, financier.address, amount);

      await expect(
        contract.connect(shipper).pledgeForFinancing(tokenId, financier.address, amount)
      ).to.be.revertedWith("Already financed");
    });

    it("融资方可以释放货权", async function () {
      const amount = ethers.parseEther("100");

      await contract.connect(shipper).pledgeForFinancing(tokenId, financier.address, amount);

      await expect(
        contract.connect(financier).releaseOwnership(tokenId)
      )
        .to.emit(contract, "BillReleased")
        .withArgs(tokenId, shipper.address);

      const billData = await contract.getBillData(tokenId);
      expect(billData.isReleased).to.equal(true);
    });

    it("非融资方不能释放货权", async function () {
      const amount = ethers.parseEther("100");

      await contract.connect(shipper).pledgeForFinancing(tokenId, financier.address, amount);

      await expect(
        contract.connect(other).releaseOwnership(tokenId)
      ).to.be.revertedWith("Not the financier");
    });
  });

  describe("转移功能", function () {
    let tokenId;

    beforeEach(async function () {
      const billNumber = "BOL-2026-001";
      const ipfsHash = "QmTest123";
      const dataHash = "0x1234567890abcdef";
      const tokenURI = `ipfs://${ipfsHash}`;

      await contract.mintBill(shipper.address, billNumber, ipfsHash, dataHash, tokenURI);
      tokenId = 0;
    });

    it("应该允许转移未融资的提单", async function () {
      await expect(
        contract.connect(shipper).transferFrom(shipper.address, other.address, tokenId)
      )
        .to.emit(contract, "BillTransferred")
        .withArgs(tokenId, shipper.address, other.address);

      expect(await contract.ownerOf(tokenId)).to.equal(other.address);
    });

    it("不应该允许转移已融资但未释放的提单", async function () {
      const amount = ethers.parseEther("100");
      await contract.connect(shipper).pledgeForFinancing(tokenId, financier.address, amount);

      await expect(
        contract.connect(shipper).transferFrom(shipper.address, other.address, tokenId)
      ).to.be.revertedWith("Bill is financed and not released");
    });

    it("应该允许转移已释放的提单", async function () {
      const amount = ethers.parseEther("100");
      await contract.connect(shipper).pledgeForFinancing(tokenId, financier.address, amount);
      await contract.connect(financier).releaseOwnership(tokenId);

      await contract.connect(shipper).transferFrom(shipper.address, other.address, tokenId);

      expect(await contract.ownerOf(tokenId)).to.equal(other.address);
    });
  });

  describe("销毁功能", function () {
    let tokenId;

    beforeEach(async function () {
      const billNumber = "BOL-2026-001";
      const ipfsHash = "QmTest123";
      const dataHash = "0x1234567890abcdef";
      const tokenURI = `ipfs://${ipfsHash}`;

      await contract.mintBill(shipper.address, billNumber, ipfsHash, dataHash, tokenURI);
      tokenId = 0;
    });

    it("应该允许销毁未融资的提单", async function () {
      await expect(contract.connect(shipper).burn(tokenId))
        .to.emit(contract, "BillBurned")
        .withArgs(tokenId, shipper.address);

      await expect(contract.ownerOf(tokenId)).to.be.reverted;
    });

    it("不应该允许销毁已融资但未释放的提单", async function () {
      const amount = ethers.parseEther("100");
      await contract.connect(shipper).pledgeForFinancing(tokenId, financier.address, amount);

      await expect(
        contract.connect(shipper).burn(tokenId)
      ).to.be.revertedWith("Cannot burn financed bill");
    });

    it("应该允许销毁已释放的提单", async function () {
      const amount = ethers.parseEther("100");
      await contract.connect(shipper).pledgeForFinancing(tokenId, financier.address, amount);
      await contract.connect(financier).releaseOwnership(tokenId);

      await contract.connect(shipper).burn(tokenId);

      await expect(contract.ownerOf(tokenId)).to.be.reverted;
    });
  });

  describe("查询功能", function () {
    it("应该通过提单编号查询信息", async function () {
      const billNumber = "BOL-2026-001";
      const ipfsHash = "QmTest123";
      const dataHash = "0x1234567890abcdef";
      const tokenURI = `ipfs://${ipfsHash}`;

      await contract.mintBill(shipper.address, billNumber, ipfsHash, dataHash, tokenURI);

      const billData = await contract.getBillByNumber(billNumber);
      expect(billData.billNumber).to.equal(billNumber);
      expect(billData.ipfsHash).to.equal(ipfsHash);
    });

    it("应该验证数据完整性", async function () {
      const billNumber = "BOL-2026-001";
      const ipfsHash = "QmTest123";
      const dataHash = "0x1234567890abcdef";
      const tokenURI = `ipfs://${ipfsHash}`;

      await contract.mintBill(shipper.address, billNumber, ipfsHash, dataHash, tokenURI);

      expect(await contract.verifyBillData(0, dataHash)).to.equal(true);
      expect(await contract.verifyBillData(0, "0xwronghash")).to.equal(false);
    });
  });
});
