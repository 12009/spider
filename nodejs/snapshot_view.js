var webPage = require('webpage');
var system = require('system');
var page = webPage.create();
var address;
var filename;
var wordStr;
page.settings.resourceTimeout = 10000;
//page.clipRect = {top:0, left:0, width:800, height:800};

if (system.args.length < 3) {
    console.log('Usage: mirror.js <some URL> <filename>');
    phantom.exit();
}
address = system.args[1];
filename = system.args[2];
wordStr = system.args[3];

function replaceWord(wordStr) {
    words = wordStr.split(',');
    replaceWords = function(raw) {
        for(var i in words) {
            raw = raw.replace(words[i],'<span style="color:red;">' + words[i] + '</span>');
        }
        return raw;
    }
    body = document.body.innerHTML;
    body = body.replace(/>(.*?)</g, replaceWords);
    document.body.innerHTML = body;
    //for(var t in ['a', 'p', 'small']){
    //    as = document.querySelectorAll(tags[t]);
    //    for(var i in as) {
    //        if(as[i].tagName != 'A') continue;
    //        innerHtml = as[i].innerHTML;
    //        innerHtml = innerHtml.replace(/>(.*?)</g, replaceWords);
    //        as[i].innerHTML = innerHtml;
    //    }
    //}
}

page.open(address, function(status) {
    if (status === 'success') {
        page.evaluate(function() {
            body = document.getElementsByTagName('body')[0];
            if(!body.style.backgroundColor) body.style.backgroundColor= "white";
        });
        if(wordStr) page.evaluate(replaceWord, wordStr);
        page.render(filename);
    } else {
        console.log(status);
    }
    phantom.exit();
});

