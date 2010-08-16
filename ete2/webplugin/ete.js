/*  it requires jquery loaded */

var ete_webplugin_URL = "http://jaime.phylomedb.org/wsgi/webplugin.py";

var tree2recipient = new Array();
function draw_tree(newick, recipient, treeid){
  tree2recipient[treeid]=recipient;
  $(recipient).html('<img src="loader.gif">');
  $(recipient).load(ete_webplugin_URL+'/draw', {"tree": newick, "treeid": treeid});
    }
function show_context_menu(treeid, atype, nodeid, textface, e){
  $("#popup").html('<img src="loader.gif">');
  $('#popup').load(ete_webplugin_URL+'/get_menu', {"treeid": treeid, "atype": atype, "nid": nodeid, "textface": textface}
                  );}
function run_action(treeid, atype, nodeid, aindex, search_term){
  var recipient = tree2recipient[treeid];
  $(recipient).html('<img src="loader.gif">');
  $(recipient).load(ete_webplugin_URL+'/action', {"treeid": treeid, "atype": atype, "nid": nodeid, "aindex": aindex, "search_term": search_term}
                   );
}

function random_tid(){
  var date = new Date;
  return date.getTime();
}

function bind_popup(){
$(".ete_tree_img").bind('click',function(e){
                          $("#popup").css('left',e.pageX-2 );
                          $("#popup").css('top',e.pageY-2 );
                          $("#popup").css('position',"absolute" );
                          $("#popup").css('background-color',"#fff" );
                          $("#popup").show();
                            });
}
function hide_popup(){
  $('#popup').hide();
}

$(document).ready(function(){
  hide_popup();
});
