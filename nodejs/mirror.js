var page = require('webpage').create();
var system = require('system');
var address;

//系统配置
page.settings.javascriptEnabled = true;
page.settings.resourceTimeout = 3000;
page.onResourceError = function(resourceError) {};
page.onError = function(msg, trace) {};

if (system.args.length === 1) {
    console.log('Usage: mirror.js <some URL>');
    phantom.exit();
}

address = system.args[1];
console.log('start  ' + address);
page.open(address, function(status) {
    console.log(status + " " +  page.url);
    phantom.exit();
});

