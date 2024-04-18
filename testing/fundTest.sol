// SPDX-License-Identifier: MIT
pragma solidity  ^0.8.8;

contract fundMe{

    uint256 public minUSD = 10;

    function fund() public payable{
        require(msg.value >= minUSD, "Send more funds");
    }

    // function ownerWithdraw(){

    // }
}
