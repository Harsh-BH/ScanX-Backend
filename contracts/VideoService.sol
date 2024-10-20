// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract VideoService {
    struct Video {
        string fileHash; // IPFS hash or any identifier of the video
        string result;   // Result of the analysis
        uint256 timestamp;
    }

    mapping(address => Video[]) public userVideos;

    event VideoUploaded(address indexed user, string fileHash, uint256 timestamp);

    // Price per service tier
    uint256 public basicTierPrice = 0.001 ether;
    uint256 public standardTierPrice = 0.002 ether;
    uint256 public premiumTierPrice = 0.003 ether;

    // Owner of the contract
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    // Modifier to restrict access
    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }

    // Function to set tier prices (only owner)
    function setTierPrices(uint256 _basic, uint256 _standard, uint256 _premium) external onlyOwner {
        basicTierPrice = _basic;
        standardTierPrice = _standard;
        premiumTierPrice = _premium;
    }

    // Function to purchase a service and store video details
    function purchaseService(string memory _fileHash, string memory _result, uint8 _tier) external payable {
        uint256 price = getTierPrice(_tier);
        require(msg.value >= price, "Insufficient payment");

        // Store the video details
        Video memory newVideo = Video({
            fileHash: _fileHash,
            result: _result,
            timestamp: block.timestamp
        });

        userVideos[msg.sender].push(newVideo);

        emit VideoUploaded(msg.sender, _fileHash, block.timestamp);

        // Transfer funds to the owner
        payable(owner).transfer(msg.value);
    }

    // Function to get the price of a tier
    function getTierPrice(uint8 _tier) public view returns (uint256) {
        if (_tier == 1) {
            return basicTierPrice;
        } else if (_tier == 2) {
            return standardTierPrice;
        } else if (_tier == 3) {
            return premiumTierPrice;
        } else {
            revert("Invalid tier");
        }
    }

    // Function to retrieve videos of a user
    function getUserVideos(address _user) external view returns (Video[] memory) {
        return userVideos[_user];
    }
}
