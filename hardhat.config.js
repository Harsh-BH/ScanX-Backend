require("@nomiclabs/hardhat-waffle");
require("@nomiclabs/hardhat-ethers");
require("dotenv").config();


module.exports = {
  solidity: "0.8.0",
  networks: {
    // Existing networks...

    // Add network (e.g., Goerli)
    goerli: {
      url: process.env.QUICKNODE_HTTP_URL,
      accounts: [`0x${process.env.PRIVATE_KEY}`],
    },
  },
};
