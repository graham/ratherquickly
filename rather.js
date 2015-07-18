#! /usr/bin/env node

var fs = require('fs');

function main() {
    console.log("RatherQuickly 0.1");
    var args = process.argv.slice(2);

    if (args.length == 0) {
        console.log("Usage: rather.js <command> <options>");
        console.log("\tinit: initialize the local folder structure.");
        console.log("\tcreate: create the stub of a new module.")
        console.log("\n")
    } else {
        var command = args[0];
        if (command == 'init') {
            console.log("Initializing a new RatherQuickly project...");
        } else if (command == 'create') {
            console.log("Creating a new module for your project...");
        }
    }
}

// Lets start!
main();
    
