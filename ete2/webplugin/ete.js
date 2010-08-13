/*  it requires jquery loaded */

var ete_webplugin_URL = "http://jaime.phylomedb.org/wsgi/webplugin.py"
  var tree2recipient = new Array();
function draw_tree(newick, recipient, treeid){
  tree2recipient[treeid]=recipient;
  $(recipient).load(ete_webplugin_URL+'/draw', {"tree": newick, "treeid": treeid});
}
function show_context_menu(treeid, atype, nodeid, textface, e){
  $('#popup').load(ete_webplugin_URL+'/get_menu', {"treeid": treeid, "atype": atype, "nid": nodeid, "textface": textface});
}
function run_action(treeid, atype, nodeid, aindex){
  var recipient = tree2recipient[treeid];
  $(recipient).load(ete_webplugin_URL+'/action', {"treeid": treeid, "atype": atype, "nid": nodeid, "aindex": aindex} );
}

function random_tid(){
  var date = new Date;
  return date.getTime();
}

function bind_popup(){
  $(".ete_tree_img").bind('click',function(e){ 
      $("#popup").css('left',e.pageX-5 );
      $("#popup").css('top',e.pageY-5 );
      $("#popup").css('position',"absolute" );
      $("#popup").css('background-color',"#fff" );
      $("#popup").show();
    });
}

$(document).ready(function(){  
    $('#popup').hide();
    $('#popup').click(function() {
        $('#popup').hide();
      });
  });
