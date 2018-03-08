/*
 * @Function: spider for web2  原生JS功能函数，用于辅助无界面浏览器解析页面
 * @Author:   jingwu
 * @Date:     2017-03-24
 * @History:  2017-03-24 init
 *            2017-03-24 Add parseHrefByTags parseSrcByTags parseEventByTags
 *            
 *            使用无界面浏览器执行页面解析时，要根据需求生成解析用的临时文件，再单独执行临时文件
 *            两个 //--function_name-- 包裹的是函数体，用于python中正则匹配函数内容，动态组合解析代码
 */

//a link
//--parseHrefByTags--
function parseHrefByTags(tags) {
    var rows = [];
    var href = '';
    if(typeof(tags) == 'string') tags = [tags];
    for(var t in tags) {
        tag = tags[t];
        var elements = document.querySelectorAll(tag);
        for(var e in elements) {
            if(!elements[e].href) continue;
            rows.push(elements[e].href);
        }
    }
    return rows;
}
//--parseHrefByTags--

//iframe frame img script
//--parseSrcByTags--
function parseSrcByTags(tags) {
    var rows = [];
    var src = '';
    if(typeof(tags) == 'string') tags = [tags];
    for(var t in tags) {
        tag = tags[t];
        var elements = document.querySelectorAll(tag);
        for(var e in elements) {
            if(!elements[e].src) continue;
            rows.push(elements[e].src);
        }
    }
    return rows;
}
//--parseSrcByTags--

//a div span table tr td th button
//onclick ondbclick onmousedown onmousemove onmouseout onmouseover onmouseup onkeydown onkeypress onkeyup
//--parseEventByTags--
function parseEventByTags(tags, events) {
    var rows = [];
    if(typeof(tags) == 'string') tags = [tags];
    if(typeof(events) == 'string') events = [events];
    for(var t in tags) {
        var objs = document.querySelectorAll(tags[t]);
        for(var i in objs) {
            for(var e in events) {
                if(objs[i][events[e]]) rows.push({'tag':tags[t], 'index':i, 'event':events[e]});
            }
        }
    }
    return rows;
}
//--parseEventByTags--

//参数 formatRelativeUrl 是已经定义好的函数，因在 casperjs 不可以使用多个函数，因此这样做
//--parseForms--
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
//--parseForms--

//--unique--
Array.prototype.unique = function() {
    var res = [];
    var json = {};
    for(var i = 0; i < this.length; i++) {
        if(!json[this[i]]) {
            res.push(this[i]);
            json[this[i]] = 1;
        }
    }
    return res;
}
//--unique--

//--formatRelativeUrl--
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
//--formatRelativeUrl--

//在浏览器中执行事件代码
//--execEvent--
function execEvent(tag, index, eventName) {
    var objs = document.querySelectorAll(tag);
    if(eventName = "onclick") { objs[index].onclick(); }
    if(eventName = "ondbclick") { objs[index].ondbclick(); }
    if(eventName = "onmousedown") { objs[index].onmousedown(); }
    if(eventName = "onmousemve") { objs[index].onmousemove(); }
    if(eventName = "onmouseout") { objs[index].onmouseout(); }
    if(eventName = "onmouseover") { objs[index].onmouseover(); }
    if(eventName = "onmouseup") { objs[index].onmouseup(); }
    if(eventName = "onkeydown") { objs[index].onkeydown(); }
    if(eventName = "onkeypress") { objs[index].onkeypress(); }
    if(eventName = "onkeyup") { objs[index].onkeyup(); }
}
//--execEvent--
