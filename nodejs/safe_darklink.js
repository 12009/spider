var webPage = require('webpage');
var system = require('system');
var fs = require('fs');
var page = webPage.create();
page.resourceTimeout = 5000
//page.onResourceRequested = function(requestData, networkRequest) {console.log(JSON.stringify(requestData));};
//var darklinks = [];

var startUrl = system.args[1];
function check_darklink() {
    as = document.querySelectorAll('a');
    var darklinks = [];
    var domain = document.domain;
    var parser = document.createElement('a');
    for(var i in as) {
        if(as[i].tagName != 'A') continue;
        parser.href = as[i].href;
        if(parser.hostname == domain) continue
        if(as[i].parentNode.style.display == 'none') darklinks.push(as[i].href);
        if(as[i].parentNode.style.visibility == 'hidden') darklinks.push(as[i].href);
        if(as[i].parentNode.tagName == 'MARQUEE') darklinks.push(as[i].href);
        if(parseInt(as[i].parentNode.offsetTop)<0 || 
            parseInt(as[i].parentNode.offsetLeft)<0) 
            darklinks.push(as[i].href);
        if(parseInt(as[i].parentNode.style.textIndent)<0) darklinks.push(as[i].href);
        if(as[i].style.color == 'rgb(255, 255, 255)') darklinks.push(as[i].href);
        if(as[i].style.fontSize == '1px') darklinks.push(as[i].href);
        if(as[i].style.lineHeight == '1px') darklinks.push(as[i].href);
    }
    return darklinks;
}

page.open(startUrl, function(status) {
    //console.log('start');
    if(status === 'fail') {
        console.log('fail');
        phantom.exit();
    }
    darklinks = page.evaluate(check_darklink);
    console.log(JSON.stringify(darklinks));
    phantom.exit();
});

//此node.js代码解析页面中符合条件的暗链解析模块
//暗链解析部分主要是查看有没有display、hidden、MARQUEE、
//暗链解析的部分出现的问题主要是什么

// page.open(startUrl, function(status) {
//     //console.log('start');
//     if(status === 'fail') {
//         console.log('fail');
//         phantom.exit();
//     }
//     darklinks = page.evaluate(check_darklink);
//     console.log(JSON.stringify(darklinks));
//     phantom.exit();
// });
