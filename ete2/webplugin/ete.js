/*  it requires jquery loaded */

var ete_webplugin_URL = "http://jaime.phylomedb.org/wsgi/webplugin.py";

var tree2recipient = new Array();
function draw_tree(newick, recipient, treeid){
  tree2recipient[treeid]=recipient;
  $(recipient).html('<img src="loader.gif">');
  $(recipient).load(ete_webplugin_URL+'/draw', {"tree": newick, "treeid": treeid});
    }
function show_context_menu(treeid, nodeid, actions, textface){
  if ( textface==undefined ){
    var textface = "";
    }

  $("#popup").html('<img src="loader.gif">');
  $('#popup').load(ete_webplugin_URL+'/get_menu', {"treeid": treeid, "show_actions": actions, "nid": nodeid, "textface": textface}
                  );}
function run_action(treeid, nodeid, aindex, search_term){
  var recipient = tree2recipient[treeid];
  $(recipient).html('<img src="loader.gif">');
  $(recipient).load(ete_webplugin_URL+'/action', {"treeid": treeid, "nid": nodeid, "aindex": aindex, "search_term": search_term}
                   );
}

function random_tid(){
    return Math.ceil(Math.random()*10000000);
}

function bind_popup(){
$(".ete_tree_img").bind('click',function(e){
                          $("#popup").css('left',e.pageX-2 );
                          $("#popup").css('top',e.pageY-2 );
                          $("#popup").css('position',"absolute" );
                          $("#popup").css('background-color',"#fff" );
                          //  $("#popup").draggable({ handle: '#ete_draggable_header' });
                          $("#popup").draggable({ cancel: 'span,li' });

                          $("#popup").show();
                            });
}
function hide_popup(){
  $('#popup').hide();
}

$(document).ready(function(){
  hide_popup();
});
