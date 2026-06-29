// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract FinBroTokens is ERC20, Ownable {
    uint256 public constant GOAL_REWARD = 100 ether;
    uint256 public constant MONTHLY_SAVINGS_REWARD = 50 ether;
    uint256 public constant DEBT_MILESTONE_REWARD = 75 ether;

    mapping(address => bool) public minters;

    event MinterAdded(address indexed minter);
    event RewardMinted(address indexed to, uint256 amount, string rewardType);

    constructor() ERC20("FinBro Token", "FBT") Ownable(msg.sender) {
        minters[msg.sender] = true;
    }

    function addMinter(address minter) external onlyOwner {
        minters[minter] = true;
        emit MinterAdded(minter);
    }

    function mintReward(address to, uint256 amount, string calldata rewardType) external {
        require(minters[msg.sender], "Not authorized minter");
        _mint(to, amount);
        emit RewardMinted(to, amount, rewardType);
    }

    function mintGoalReward(address to) external {
        require(minters[msg.sender], "Not authorized minter");
        _mint(to, GOAL_REWARD);
        emit RewardMinted(to, GOAL_REWARD, "goal");
    }

    function mintMonthlySavingsReward(address to) external {
        require(minters[msg.sender], "Not authorized minter");
        _mint(to, MONTHLY_SAVINGS_REWARD);
        emit RewardMinted(to, MONTHLY_SAVINGS_REWARD, "monthly_savings");
    }

    function mintDebtMilestoneReward(address to) external {
        require(minters[msg.sender], "Not authorized minter");
        _mint(to, DEBT_MILESTONE_REWARD);
        emit RewardMinted(to, DEBT_MILESTONE_REWARD, "debt_milestone");
    }
}
