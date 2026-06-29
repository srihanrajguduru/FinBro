require("@nomicfoundation/hardhat-toolbox");

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: "0.8.20",
  networks: {
    sepolia: {
      url: process.env.WEB3_RPC_URL || "",
      accounts: process.env.WEB3_PRIVATE_KEY ? [process.env.WEB3_PRIVATE_KEY] : [],
      chainId: 11155111,
    },
  },
};
