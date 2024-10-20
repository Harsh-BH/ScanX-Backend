// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DeepfakeDetection {

    // User profile structure
    struct UserProfile {
        address userAddress;
        string username;
        string email;
        uint256 registrationDate;
    }

    // Content structure
    struct Content {
        bytes32 contentHash;       // Hash of the content
        ContentType contentType;   // Type of content
        bool isAI;                 // Detection result
        uint256 timestamp;         // Time of upload
    }

    // Enum for content types
    enum ContentType { Video, Image, Text, Code }

    // Mapping from user address to profile
    mapping(address => UserProfile) public userProfiles;

    // Mapping from user address to array of their content
    mapping(address => Content[]) public userContents;

    // Events
    event UserProfileCreated(address indexed userAddress, string username, string email, uint256 registrationDate);
    event ContentUploaded(address indexed userAddress, bytes32 contentHash, ContentType contentType, bool isAI, uint256 timestamp);

    // Modifier to check if user profile exists
    modifier profileExists() {
        require(userProfiles[msg.sender].userAddress != address(0), "User profile does not exist.");
        _;
    }

    // Function to create or update user profile
    function setUserProfile(string memory _username, string memory _email) public {
        UserProfile storage profile = userProfiles[msg.sender];
        profile.userAddress = msg.sender;
        profile.username = _username;
        profile.email = _email;
        if (profile.registrationDate == 0) {
            profile.registrationDate = block.timestamp;
        }
        emit UserProfileCreated(msg.sender, _username, _email, profile.registrationDate);
    }

    // Function to upload content hash and detection result
    function uploadContent(bytes32 _contentHash, ContentType _contentType, bool _isAI) public profileExists {
        Content memory newContent = Content({
            contentHash: _contentHash,
            contentType: _contentType,
            isAI: _isAI,
            timestamp: block.timestamp
        });
        userContents[msg.sender].push(newContent);
        emit ContentUploaded(msg.sender, _contentHash, _contentType, _isAI, block.timestamp);
    }

    // Function to get user profile
    function getUserProfile(address _userAddress) public view returns (UserProfile memory) {
        return userProfiles[_userAddress];
    }

    // Function to get content count of a user
    function getContentCount(address _userAddress) public view returns (uint256) {
        return userContents[_userAddress].length;
    }

    // Function to get content details of a user by index
    function getContentByIndex(address _userAddress, uint256 _index) public view returns (Content memory) {
        require(_index < userContents[_userAddress].length, "Invalid index.");
        return userContents[_userAddress][_index];
    }

    // Function to get all contents of a user
    function getAllContents(address _userAddress) public view returns (Content[] memory) {
        return userContents[_userAddress];
    }
}
