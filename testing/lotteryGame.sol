// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;


contract test1 {

    uint256 public testValue = 0;
    uint256 public lastUsedBlock;
    bool public runBefore = false;
    bool public timeRunOut = false;

    function firstRun() public{
        require(!runBefore, "Already started!");
        lastUsedBlock = block.number;
        runBefore = true;
    }

    function startGame() public {
        require(runBefore, "Game not started");
        uint256 currentBlock = block.number;
        uint256 difference = currentBlock - lastUsedBlock;
        if(difference >= 10){
            timeRunOut = true;
        } else {
            lastUsedBlock = currentBlock;
        }
    }

    function setTestValue(uint256 _newValue) public {
        testValue = _newValue;
    }

}
