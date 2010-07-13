var popup_counter = 0;
var map = Array();
var rx = 0;
var ry = 0;
var move_active = 0;
var zindex = 20;
var show_seqs = 1, show_go = 1;
var userpath = '';
var loader = new Image();
loader.src = "http://"+window.location.hostname+"/loader.gif"
var session_id = '';
var wait = 0;

/* AJAX */
var xmlHttp = false;
/*@cc_on @*/
/*@if (@_jscript_version >= 5)
try {
  xmlHttp = new ActiveXObject("Msxml2.XMLHTTP");
} catch (e) {
  try {
    xmlHttp = new ActiveXObject("Microsoft.XMLHTTP");
  } catch (e2) {
    xmlHttp = false;
  }
}
@end @*/
if (!xmlHttp && typeof XMLHttpRequest != "undefined") {
  xmlHttp = new XMLHttpRequest();
}
function askByAjax(url, egg, isLed) {
    if(wait == 0){
        var workurl = "http://"+window.location.hostname+"/" + url + "&rnd=" + Math.random();
        xmlHttp.open('GET', workurl, true);
        xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        wait = 1;
        xmlHttp.onreadystatechange = function () {
            if (xmlHttp.readyState == 4) {
                var response = xmlHttp.responseText;
                if (response != ''){
                    wait = 0;
                    document.getElementById(egg).innerHTML = response;
                    if (isLed == 1){
                        var newdiv = document.getElementById(egg);
                        led(parseInt(newdiv.style.left), parseInt(newdiv.style.top), parseInt(newdiv.style.left)+newdiv.offsetWidth, parseInt(newdiv.style.top)+newdiv.offsetHeight, "hide('"+newdiv.id+"')");
                    }
                }
            }
        }
        document.getElementById(egg).innerHTML = '';
        document.getElementById(egg).appendChild(loader);
        xmlHttp.send(null);
    }
}

// MAIN

function get_map(id, arg, sid){
    if(wait == 0){
        if (id.src.indexOf('loader') == -1){
            var url = "http://"+window.location.hostname+"/webplugin/getmap?seqid=" + arg + "&sid="+session_id+"&rnd=" + Math.random();
            xmlHttp.open('GET', url, true);
            xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            wait = 1;
            xmlHttp.onreadystatechange = function () { apply_map(arg); };
            xmlHttp.send(null);
        } else {
            session_id = sid;
            ask_for_new_image(arg);
        }
    }
}
function apply_map(arg){
    if (xmlHttp.readyState == 4) {
        var response = xmlHttp.responseText;
        var script = document.createElement("script");
        script.type = "text/javascript";
        script.text = response;
        wait = 0;
        document.getElementById('scriptarea_'+arg).innerHTML = '';
        document.getElementById('scriptarea_'+arg).appendChild(script);
    }
}

function ask_for_new_image(id){
    var newtree = new Image();
    newtree.src = "http://"+window.location.hostname+"/webplugin/rtree?tree=" + id + "&sid="+session_id+"&rnd=" + Math.random();
    newtree.onload = replace_img(id,newtree.src);
}
function replace_img(id, src){
    document.getElementById(id).src = src;
}

// COMPARE MAP AND MOUSE POSITION

function check(x,y,map){
    if (map.length > 0){
        var item = Array();
        for (var i = 0; i < map.length; i++){
            item = map[i];
            if (item[1] <= y && y <= item[3] && x >= item[0] && x <= item[2])
                return item[4];
        } return 0;
    } else return 0;
}

function mapcheck(elem, id){
    getScrollXY();
    var left = 0;
    var top = 0;
    while (elem){
        left += elem.offsetLeft;
        top += elem.offsetTop;
        elem = elem.offsetParent;
    }
    var x = mousex - left;
    var y = mousey - top;

    text = check(x,y,map[id]['texts']);
    if (text == 0){
        node = check(x,y, map[id]['nodes']);
        if (node == 0){
            if(map[id]['faces'] == 'undefined'){
                emptymenu(id);
            } else {
                emptymenu(id);
                face = check(x,y, map[id]['faces']);
                if (face == 0)
                    emptymenu(id);
                else
                    facesmenu(face);
            }
        } else nodemenu(id, node);
    } else get_id_info(text);
}


function get_id_info(arg) {
    popup("",arg);
    askByAjax('webplugin/info?dbid=' + arg, 'p_content_'+popup_counter, 0);
}
function facesmenu(id, face) {
    menu_popup("");
    askByAjax('webplugin/facesmenu?id='+id+'&face='+face, 'p_'+popup_counter, 1);
}
function nodemenu(id, node) {
    menu_popup("");
    askByAjax('webplugin/nodemenu?id='+id+'&node='+node, 'p_'+popup_counter, 1);
}
function emptymenu(id) {
    menu_popup("");
    askByAjax('webplugin/emptymenu?id='+id, 'p_'+popup_counter, 1);
}


// RULES SYSTEM

function set_rule(rule, seqid, itemid) {
    var url = 'http://'+window.location.hostname+'/webplugin/addrule?sid='+session_id+'&seqid=' + seqid + "&itemid=" + itemid + "&rule="+rule;
    xmlHttp.open('GET', url, true);
    xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xmlHttp.onreadystatechange = function () { ask_with_new_rules(seqid); };
    xmlHttp.send(null);
}

function rem_rule(rule, seqid, itemid) {
    var url = 'http://'+window.location.hostname+'/webplugin/addrule?sid='+session_id+'&seqid=' + seqid + "&itemid=" + itemid + "&rule=" + rule + "&remove=1";;
    xmlHttp.open('GET', url, true);
    xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xmlHttp.onreadystatechange = function () { ask_with_new_rules(seqid); };
    xmlHttp.send(null);
}

function unic_rule(rule, seqid, itemid) {
    var url = 'http://'+window.location.hostname+'/webplugin/addrule?sid='+session_id+'&seqid=' + seqid + "&itemid=" + itemid + "&rule="+rule+"&unic=1";
    xmlHttp.open('GET', url, true);
    xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xmlHttp.onreadystatechange = function () { ask_with_new_rules(seqid); };
    xmlHttp.send(null);
}

function clear_rules(seqid) {
    var url = 'http://'+window.location.hostname+'/webplugin/addrule?sid='+session_id+'&seqid=' + seqid + "&clear=1";
    xmlHttp.open('GET', url, true);
    xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    xmlHttp.onreadystatechange = function () { ask_with_new_rules(seqid); };
    xmlHttp.send(null);
}

function ask_with_new_rules(arg){
    if (xmlHttp.readyState == 4) {
        var response = xmlHttp.responseText;
        if (response == '1')
            ask_for_new_image(arg);
        else
            alert(response);
    }
}

// POPUP MENU FUNCTIONS

function addHandler(object, event, handler, useCapture) {
    if (object.addEventListener)
        object.addEventListener(event, handler, useCapture);
    else if (object.attachEvent)
        object.attachEvent('on' + event, handler);
    else object['on' + event] = handler;
}
function hide(id){
    document.getElementById(id).style.display = 'none';
}
function move_start(id){
    if (move_active == 0){
        rx = mousex - parseInt(document.getElementById(id).style.left);
        ry = mousey - parseInt(document.getElementById(id).style.top);
        move_active = 1;
        move(id);
    }
}
function move_stop(id){
    if (move_active == 1) move_active = 0;
}
function move(id){
    if (move_active == 1){
        document.getElementById(id).style.top  = (mousey - ry) + 'px';
        document.getElementById(id).style.left = (mousex - rx) + 'px';
        setTimeout("move('"+id+"');", 50);
    }
}
function top(id){
    zindex += 1; document.getElementById(id).style.zIndex = zindex;
}
function led(x1,y1,x2,y2,action){
    if (y1 > mousey || mousey > y2 || x1 > mousex || mousex > x2 )
        setTimeout(action, 50);
    else
        setTimeout('led('+x1+','+y1+','+x2+','+y2+',"'+action+'")', 200);
}
function popup(arg, title){
    popup_counter += 1;
    var newdiv = document.createElement("div");
    newdiv.innerHTML = "<div class='popup popup_bg' id='p_"+popup_counter+"' style='width: 350px; position: absolute; top: " + mousey + "px; left: " + mousex + "px; z-index: 100'><table class='popup_title' width='100%' cellpadding=0 cellspacing=0><tr><td style='cursor: text'>"+title+"</td><td onMouseDown=\"move_start('p_"+popup_counter+"')\" onMouseUp=\"move_stop('p_"+popup_counter+"')\" onMouseOver=\"top('p_"+popup_counter+"')\" width=100%></td><td class='popup_interactor' style='float: right' onClick=\"hide('p_"+popup_counter+"')\">[x]</td></tr></table><div style='overflow: auto'><div style='padding: 4px' id='p_content_"+popup_counter+"'>"+arg+"</div></div></div>";
    document.body.appendChild(newdiv);
    if (arg == '') document.getElementById('p_content_'+popup_counter).appendChild(loader);
}
function menu_popup(arg){
    popup_counter += 1;
    var newdiv = document.createElement("div");
    newdiv.innerHTML = "<div class='popup popup_bg' id='p_"+popup_counter+"' style='position: absolute; top: " + mousey + "px; left: " + mousex + "px; z-index: 100; padding: 4px'>"+arg+"</div>";
    document.body.appendChild(newdiv);
    if (arg == '') document.getElementById('p_'+popup_counter).appendChild(loader);
}


// CHECK THE BROWSER TYPE
isDOM=document.getElementById //DOM1 browser (MSIE 5+, Netscape 6, Opera 5+)
isOpera=isOpera5=window.opera && isDOM //Opera 5+
isOpera6=isOpera && window.print //Opera 6+
isOpera7=isOpera && document.readyState //Opera 7+
isMSIE=document.all && document.all.item && !isOpera //Microsoft Internet Explorer 4+
isMSIE5=isDOM && isMSIE //MSIE 5+
isNetscape4=document.layers //Netscape 4.*isMozilla=isDOM && navigator.appName=="Netscape" //Mozilla,  Netscape 6.*

var scrOfX = 0, scrOfY = 0, mousex = 0, mousey = 0;
// LOOK FOR THE ABSOLUTE MOUSE POSITION
function getScrollXY() {
  if( typeof( window.pageYOffset ) == 'number' ) {
    //Netscape compliant
    scrOfY = window.pageYOffset;
    scrOfX = window.pageXOffset;
  } else if( document.body && ( document.body.scrollLeft || document.body.scrollTop ) ) {
    //DOM compliant
    scrOfY = document.body.scrollTop;
    scrOfX = document.body.scrollLeft;
  } else if( document.documentElement && ( document.documentElement.scrollLeft || document.documentElement.scrollTop ) ) {
    //IE6 standards compliant mode
    scrOfY = document.documentElement.scrollTop;
    scrOfX = document.documentElement.scrollLeft;
  } else {
    scrOfX = 0; scrOfY = 0;
  }
}

if(isNetscape4) document.captureEvents(Event.MOUSEMOVE)
if(isMSIE || isOpera7){
  document.onmousemove=function(){
    getScrollXY();    mousex=event.clientX + scrOfX;
    mousey=event.clientY + scrOfY;
    return true
  }} else if(isOpera){
      document.onmousemove=function(){
    mousex=event.clientX;
    mousey=event.clientY;
    return true
  }
} else if(isNetscape4 || isMozilla){
  document.onmousemove=function(e){
    mousex = e.pageX
    mousey = e.pageY
    return true
  }
}
