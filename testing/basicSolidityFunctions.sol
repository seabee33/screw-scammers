// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;


contract test1 {

    // Vars
    uint256 public pubNumber;

    // View Item
    function showNumber() public view returns(uint256){
        return pubNumber;
    }

    // Change Item
    function changeNumber(uint256 _newNumber) public{
        pubNumber = _newNumber;
    }

    // Add to item
    function addToItem() public {
        pubNumber = pubNumber + 1;
    }
}
