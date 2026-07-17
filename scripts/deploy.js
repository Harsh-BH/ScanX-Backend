// scripts/deploy.js

async function main() {
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contracts with the account:", deployer.address);
  
    const VideoService = await ethers.getContractFactory("VideoService");
    const contract = await VideoService.deploy();
    await contract.deployed();

    console.log("VideoService deployed to:", contract.address);
  }
  
  main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error(error);
      process.exit(1);
    });
  