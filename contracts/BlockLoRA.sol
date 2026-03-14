// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title BlockLoRA
 * @notice Blockchain-Enabled Federated Fine-Tuning of Large Language Models
 * @dev Coordinates Proof-of-Validation for LoRA adapter updates
 */
contract BlockLoRA {
    
    // ============ Enums ============
    
    enum UpdateStatus { Pending, Accepted, Rejected }
    
    // ============ Structs ============
    
    struct Update {
        uint256 id;
        uint256 round;
        address client;
        string ipfsCID;
        bytes32 fileHash;
        uint256 timestamp;
        UpdateStatus status;
        uint256 acceptVotes;
        uint256 rejectVotes;
    }
    
    struct ValidationVote {
        address validator;
        bool accept;
        uint256 accuracyScore;    // scaled by 1000 (e.g., 95.5% = 955)
        uint256 divergenceScore;  // scaled by 1000
        uint256 timestamp;
    }
    
    struct TrustScore {
        uint256 score;              // 0-1000, starts at 500
        uint256 acceptedUpdates;
        uint256 rejectedUpdates;
        uint256 totalSubmissions;
    }
    
    // ============ State Variables ============
    
    uint256 public currentRound;
    uint256 public updateCounter;
    
    // Thresholds
    uint256 public constant MIN_ACCURACY = 700;      // 70%
    uint256 public constant MAX_DIVERGENCE = 500;    // 50%
    uint256 public constant MIN_VOTES_REQUIRED = 2;
    uint256 public constant ACCEPTANCE_THRESHOLD = 51; // 51% of votes
    
    // Mappings
    mapping(uint256 => Update) public updates;
    mapping(uint256 => ValidationVote[]) public votes;
    mapping(uint256 => uint256[]) public roundUpdates;
    mapping(address => TrustScore) public trustScores;
    mapping(uint256 => address[]) public roundValidators;
    mapping(uint256 => mapping(address => bool)) public hasVoted;
    
    // ============ Events ============
    
    event RoundStarted(uint256 round, uint256 timestamp);
    event UpdateSubmitted(uint256 updateId, uint256 round, address client, string ipfsCID, bytes32 fileHash);
    event ValidatorsSelected(uint256 round, address[] validators);
    event VoteSubmitted(uint256 updateId, address validator, bool accept, uint256 accuracyScore, uint256 divergenceScore);
    event UpdateFinalized(uint256 updateId, UpdateStatus status, uint256 acceptVotes, uint256 rejectVotes);
    event RoundFinalized(uint256 round, uint256 acceptedCount, uint256 rejectedCount);
    event TrustScoreUpdated(address client, uint256 newScore);
    
    // ============ Constructor ============
    
    constructor() {
        currentRound = 0;
    }
    
    // ============ Core Functions ============
    
    /**
     * @notice Start a new training round
     */
    function startRound() external {
        currentRound++;
        emit RoundStarted(currentRound, block.timestamp);
    }
    
    /**
     * @notice Submit a LoRA adapter update
     * @param ipfsCID IPFS content identifier
     * @param fileHash SHA256 hash of the adapter file
     */
    function submitUpdate(string memory ipfsCID, bytes32 fileHash) external {
        require(currentRound > 0, "No active round");
        
        updateCounter++;
        
        updates[updateCounter] = Update({
            id: updateCounter,
            round: currentRound,
            client: msg.sender,
            ipfsCID: ipfsCID,
            fileHash: fileHash,
            timestamp: block.timestamp,
            status: UpdateStatus.Pending,
            acceptVotes: 0,
            rejectVotes: 0
        });
        
        roundUpdates[currentRound].push(updateCounter);
        
        // Initialize trust score if first submission
        if (trustScores[msg.sender].totalSubmissions == 0) {
            trustScores[msg.sender].score = 500; // Start at 50%
        }
        trustScores[msg.sender].totalSubmissions++;
        
        emit UpdateSubmitted(updateCounter, currentRound, msg.sender, ipfsCID, fileHash);
    }
    
    /**
     * @notice Register validators for current round
     * @param validators Array of validator addresses
     */
    function selectValidators(address[] memory validators) external {
        require(currentRound > 0, "No active round");
        roundValidators[currentRound] = validators;
        emit ValidatorsSelected(currentRound, validators);
    }
    
    /**
     * @notice Submit validation vote for an update
     * @param updateId ID of the update being validated
     * @param accept True to accept, false to reject
     * @param accuracyScore Accuracy score (0-1000)
     * @param divergenceScore Divergence score (0-1000)
     */
    function submitVote(
        uint256 updateId,
        bool accept,
        uint256 accuracyScore,
        uint256 divergenceScore
    ) external {
        Update storage update = updates[updateId];
        require(update.id != 0, "Update does not exist");
        require(update.status == UpdateStatus.Pending, "Update already finalized");
        require(!hasVoted[updateId][msg.sender], "Already voted");
        require(isValidator(msg.sender, update.round), "Not a validator");
        
        // Record vote
        votes[updateId].push(ValidationVote({
            validator: msg.sender,
            accept: accept,
            accuracyScore: accuracyScore,
            divergenceScore: divergenceScore,
            timestamp: block.timestamp
        }));
        
        hasVoted[updateId][msg.sender] = true;
        
        if (accept) {
            update.acceptVotes++;
        } else {
            update.rejectVotes++;
        }
        
        emit VoteSubmitted(updateId, msg.sender, accept, accuracyScore, divergenceScore);
        
        // Auto-finalize if enough votes
        uint256 totalVotes = update.acceptVotes + update.rejectVotes;
        if (totalVotes >= MIN_VOTES_REQUIRED) {
            finalizeUpdate(updateId);
        }
    }
    
    /**
     * @notice Finalize an update based on votes
     * @param updateId ID of the update to finalize
     */
    function finalizeUpdate(uint256 updateId) internal {
        Update storage update = updates[updateId];
        require(update.status == UpdateStatus.Pending, "Already finalized");
        
        uint256 totalVotes = update.acceptVotes + update.rejectVotes;
        require(totalVotes >= MIN_VOTES_REQUIRED, "Not enough votes");
        
        // Calculate acceptance percentage
        uint256 acceptanceRate = (update.acceptVotes * 100) / totalVotes;
        
        if (acceptanceRate >= ACCEPTANCE_THRESHOLD) {
            update.status = UpdateStatus.Accepted;
            trustScores[update.client].acceptedUpdates++;
            trustScores[update.client].score = min(1000, trustScores[update.client].score + 50);
        } else {
            update.status = UpdateStatus.Rejected;
            trustScores[update.client].rejectedUpdates++;
            trustScores[update.client].score = max(0, trustScores[update.client].score - 100);
        }
        
        emit UpdateFinalized(updateId, update.status, update.acceptVotes, update.rejectVotes);
        emit TrustScoreUpdated(update.client, trustScores[update.client].score);
    }
    
    /**
     * @notice Finalize the current round
     */
    function finalizeRound() external {
        require(currentRound > 0, "No active round");
        
        uint256[] memory updateIds = roundUpdates[currentRound];
        uint256 acceptedCount = 0;
        uint256 rejectedCount = 0;
        
        for (uint256 i = 0; i < updateIds.length; i++) {
            Update storage update = updates[updateIds[i]];
            
            // Force finalize pending updates
            if (update.status == UpdateStatus.Pending) {
                uint256 totalVotes = update.acceptVotes + update.rejectVotes;
                if (totalVotes > 0) {
                    finalizeUpdate(updateIds[i]);
                }
            }
            
            if (update.status == UpdateStatus.Accepted) {
                acceptedCount++;
            } else if (update.status == UpdateStatus.Rejected) {
                rejectedCount++;
            }
        }
        
        emit RoundFinalized(currentRound, acceptedCount, rejectedCount);
    }
    
    // ============ View Functions ============
    
    function getUpdate(uint256 updateId) external view returns (Update memory) {
        return updates[updateId];
    }
    
    function getAcceptedUpdates(uint256 round) external view returns (uint256[] memory) {
        uint256[] memory allUpdates = roundUpdates[round];
        uint256 acceptedCount = 0;
        
        // Count accepted
        for (uint256 i = 0; i < allUpdates.length; i++) {
            if (updates[allUpdates[i]].status == UpdateStatus.Accepted) {
                acceptedCount++;
            }
        }
        
        // Build result array
        uint256[] memory accepted = new uint256[](acceptedCount);
        uint256 index = 0;
        for (uint256 i = 0; i < allUpdates.length; i++) {
            if (updates[allUpdates[i]].status == UpdateStatus.Accepted) {
                accepted[index] = allUpdates[i];
                index++;
            }
        }
        
        return accepted;
    }
    
    function getRoundUpdates(uint256 round) external view returns (uint256[] memory) {
        return roundUpdates[round];
    }
    
    function getVotes(uint256 updateId) external view returns (ValidationVote[] memory) {
        return votes[updateId];
    }
    
    function getTrustScore(address client) external view returns (TrustScore memory) {
        return trustScores[client];
    }
    
    function isValidator(address addr, uint256 round) public view returns (bool) {
        address[] memory validators = roundValidators[round];
        for (uint256 i = 0; i < validators.length; i++) {
            if (validators[i] == addr) {
                return true;
            }
        }
        return false;
    }
    
    // ============ Helper Functions ============
    
    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }
    
    function max(uint256 a, uint256 b) internal pure returns (uint256) {
        return a > b ? a : b;
    }
}
