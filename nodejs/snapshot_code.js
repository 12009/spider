var webPage = require('webpage');
var system = require('system');
var fs = require('fs');
var page = webPage.create();
var linesize = 800;
page.settings.loadImages = false;
page.settings.resourceTimeout = 5000;
page.viewportSize = {width: 768, height: 1024};
page.clipRect = {top: 0, left: 0, width: 768, height: 14136};
page.paperSize = {width: '768px', height: '1024px', margin: {bottom: '2px'}};

if (system.args.length < 3) {
    console.log('Usage: snapshot_code.js <codefile> <savefile> <words>');
    phantom.exit();
}

var codefile = system.args[1];
var outputfile = system.args[2];
var wordStr = system.args[3];
page.open('./nodejs/tpl_code.html', function(status) {
    if (status !== 'success') {
        console.log('fail');
        phantom.exit();
    }
    var code = fs.read(codefile);
    code = code.replace(/&/g, '&amp;');
    code = code.replace(/ /g, '&nbsp;');
    code = code.replace(/</g, '&lt;');
    code = code.replace(/>/g, '&gt;');
    code = code.replace(/\n/g, "<br/>\n");
    if(wordStr) {
        words = wordStr.split(',');
        for(var i in words) {
            var reg = new RegExp(words[i], "g");
            code = code.replace(reg, '<span style="color:red;">' + words[i] + '</span>');
        }
    }
    var pages = code.split("\n");
    var total = Math.ceil(pages.length / linesize);
    snapfiles = [];
    for(i = 0; i < total; i++) {
        tmpfile = outputfile.replace('.png', '_' + i + '.png');
        body = pages.slice(i * linesize, (i + 1) * linesize).join("\n");
        height = page.evaluate(function(body) {
            document.body.innerHTML = body;
            window.scrollTo(0, 14136);
            return document.body.scrollHeight;
        }, body);
        page.clipRect = {top: 0, left: 0, width: 768, height: height};
        page.render(tmpfile);
        snapfiles.push(tmpfile);
    }
    console.log(JSON.stringify(snapfiles));
    phantom.exit();
});

