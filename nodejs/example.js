var querystring = require('querystring');

var links = [];
var ajaxs = [];
var casper = require('casper').create({
    verbose:false, 
    logLevel:'debug', 
    pageSettings: {
        loadImages:false, 
        loadPlugins:false
    },
    onResourceRequested:function(self, request) {
        var isAjax = 0;
        for(var key in request['headers']) {
            if(request['headers'][key]['name'] == 'X-Requested-With') isAjax = 1;
        }
        if(isAjax) {
            //非GET，则识别的POST
            if(request.method == 'GET') {
                ajaxs.push({'url':request.url, 'method':'GET', 'data': ''});
            } else {
                querys = querystring.parse(request.postData);
                console.log(JSON.stringify(querys));
                postItems = []
                for(var k in querys) {
                    row = {'type': 'text', 'name':k,  'value':querys[k]};
                    postItems.push(row);
                }
                postItems.push({'type':'post_data_type', 'name':'ajax_data_raw', 'value':request.postData});
                //ajaxs.push({'url':request.url, 'method':'POST', 'data': request.postData});
                ajaxs.push({'url':request.url, 'method':'POST', 'data': postItems});
            }
        } else {
            links.push(request.url);
        }
    }
});
function parseForms(formatRelativeUrl) {
    var url = document.location.href;
    var forms = document.querySelectorAll('form');
    return Array.prototype.map.call(forms, function (e) {
        var rows = [];
        //解析input
        var inputs = e.querySelectorAll('input');
        for(var i in inputs) {
            if(typeof(inputs[i]) != 'object') continue;
            rows.push({'type':inputs[i].type, 'name':inputs[i].name, 'value':inputs[i].value});
        }

        //解析select
        var selects = e.querySelectorAll('select');
        for(var i in selects) {
            if(typeof(selects[i]) != 'object') continue;
            rows.push({'type':'select', 'name':inputs[i].name, 'value':inputs[i].value});
        }

        //解析textarea
        var textareas = e.querySelectorAll('textarea');
        for(var i in textareas) {
            if(typeof(textareas[i]) != 'object') continue;
            rows.push({'type':'textarea', 'name':inputs[i].name, 'value':inputs[i].value});
        }
        rows.push({'type':'post_data_type', 'name':'form_data',  'value':'js_parseForms'});
        return {'method':e.method, 'url':formatRelativeUrl(url, e.action), 'fields':rows};
    });
}
function formatRelativeUrl(baseUrl, relativeUrl) {
    if(relativeUrl.slice(0, 4) == 'http') return relativeUrl;
    if(relativeUrl == '') return baseUrl;
    baseUrlParse = baseUrl.split('/');
    basePath = baseUrlParse.slice(3).join('/');
    if(basePath == '' || basePath == '/') basePath = '/';

    baseArr = basePath.split('/');
    if(relativeUrl.slice(0, 3) == '../') {
        var relativeArr = relativeUrl.split('/');
        baseArr = baseArr.slice(0, -1);
        for(var i = 0; i < 20; i++) {
            if(relativeArr[0] != '..' || baseArr.length == 0) break;
            relativeArr = relativeArr.slice(1);
            baseArr = baseArr.slice(0, -1);
        }
        baseArr = baseArr.concat(relativeArr);
    } else if(relativeUrl.slice(0, 2) == './') {
        baseArr = baseArr.slice(0, -1);
        baseArr.push(relativeUrl.slice(2));
    } else if(relativeUrl[0] == '/') {
        baseArr = [relativeUrl.slice(1)];
    } else {
        baseArr = baseArr.slice(0, -1);
        baseArr.push(relativeUrl);
    }
    path = baseArr.join('/');
    for(var i = 0; i < 5; i++) path = path.replace(/\/\//g, '/');
    return [baseUrlParse[0], '', baseUrlParse[2], path].join('/');
}
casper.start("http://www.ifeng.com/");
casper.then(function () {
    var forms = this.evaluate(parseForms, formatRelativeUrl);
    var data = {
        'links': links,
        'ajaxs': ajaxs,
        'results': forms,
    };
    console.log(JSON.stringify(data));
});
casper.run(function () {casper.done();});
