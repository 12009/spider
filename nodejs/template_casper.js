/*
 * @Function: spider for web2
 * @Author:   jingwu
 * @Date:     2017-03-24
 * @History:  2017-03-24 init
 *            2017-03-24 Add parseHrefByTags parseSrcByTags parseEventByTags
 */

//--casper_create--
var querystring = require('querystring');
var links = [];
var ajaxs = [];
var output = [];
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
                postItems = []
                for(var k in querys) {
                    row = {'type': 'text', 'name':k,  'value':querys[k]};
                    postItems.push(row);
                }
                postItems.push({'type':'post_data_type', 'name':'ajax_data_raw', 'value':request.postData});
                ajaxs.push({'url':request.url, 'method':'POST', 'data': postItems});
                //ajaxs.push({'url':request.url, 'method':'POST', 'data': request.postData});
            }
        } else {
            links.push(request.url);
        }
    }
});
//--casper_create--

//--casper_then--
casper.then(function () {
    var output = this.evaluate(###jsfunc###, ###params###);
    var data = {
        'links': links,
        'ajaxs': ajaxs,
        'results': output,
    };
    console.log(JSON.stringify(data));
});
//--casper_then--

//--casper_output--
casper.then(function () {
    var data = {
        'links': links,
        'ajaxs': ajaxs,
        'results': [],
    };
    console.log(JSON.stringify(data));
});
//--casper_output--

//--casper_parseform--
casper.then(function () {
    var forms = this.evaluate(parseForms, formatRelativeUrl);
    var data = {
        'links': links,
        'ajaxs': ajaxs,
        'results': forms,
    };
    console.log(JSON.stringify(data));
});
//--casper_parseform--

//--casper_parseform_frame--
casper.then(function () {
    var forms = [];
    formsTmp = this.evaluate(parseForms, formatRelativeUrl);
    if(formsTmp) {
        for(var j in formsTmp) {
            forms.push(formsTmp[j]);
        }
    }
    iframesTmp = this.evaluate(parseSrcByTags, ['iframe', 'frame']);
    for(var i in iframesTmp) {
        var url = iframes[i];
        this.thenOpen(url, function () {
            formsTmp = this.evaluate(parseForms, formatRelativeUrl);
            if(formsTmp) {
                for(var j in formsTmp) {
                    forms.push(formsTmp[j]);
                }
            }
        });
    }
    var data = {
        'links': links,
        'ajaxs': ajaxs,
        'results': forms,
    };
    console.log(JSON.stringify(data));
});
//--casper_parseform_frame--

//--casper_start--
var startUrl = '###startUrl###';
casper.start(startUrl);
//--casper_start--

//--casper_wait--
casper.wait(1000, function(){});
//--casper_wait--

//--casper_run--
//casper.run(function () {casper.done();});
casper.run();
//--casper_run--

//--casper_event--
casper.then(function() {
    if (this.getCurrentUrl() != startUrl) { this.back(); }
});
casper.then(function() {
    this.evaluate(execEvent, '###tag###', '###index###', '###eventName###');
});
casper.wait(1000, function(){});
//--casper_event--


/*
if event == 'onclick':
'click', '%s[%s]'
if event == 'ondbclick':
'doublelclick', '%s[%s]'
if event == 'onmousedown':
'mousedown', '%s[%s]'
if event == 'onmousemove':
'mousemove', '%s[%s]'
if event == 'onmouseout':
'mouseout', '%s[%s]'
if event == 'onmouseover':
'mouseover', '%s[%s]'
if event == 'onmouseup':
'mouseup', '%s[%s]'
*/
