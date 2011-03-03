/*  it requires jquery loaded */

var ete_webplugin_URL = "http://jaime.phylomedb.org/wsgi/tol/tol_example.py";
var loading_img = '<img border=0 src="/loader.gif">';

function draw_tree(treeid, newick, recipient, extra_params){
  var params = {"tree": newick, "treeid": treeid};
  if ( extra_params != undefined ){
    var params =  $.extend(params, extra_params);
    }

  $(recipient).html(loading_img);
  //$(recipient).fadeTo(500, 0.2);
  $(recipient).load(ete_webplugin_URL+'/draw', params,  function() {
          $(recipient).fadeTo(100, 1);
  });
}

function show_context_menu(treeid, nodeid, actions, textface){
  if ( textface==undefined ){
    var textface = "";
    }

  $("#popup").html(loading_img);
  $('#popup').load(ete_webplugin_URL+'/get_menu', {"treeid": treeid, "show_actions": actions, "nid": nodeid, "textface": textface}
                  );}

function run_action(treeid, nodeid, aindex, search_term){
  var recipient = "#ETE_tree_"+treeid;
  //$(recipient).html(loading_img);
  $(recipient).fadeTo(500, 0.3);
  $(recipient).load(ete_webplugin_URL+'/action', {"treeid": treeid, "nid": nodeid, "aindex": aindex, "search_term": search_term}, function() {
          $(recipient).fadeTo(250, 1);
      });
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
                          $("#popup").draggable({ cancel: 'span,li' });
                          $("#popup").show();
                            });
}
function hide_popup(){
  $('#popup').hide();
}


function search_in_tree(treeid, search_index_action, search_term, term_target){
  var term = term_target + "::" + search_term;
  run_action(treeid, "", search_index_action, term);
}

function show_box(e, box) {
  box.draggable({ handle: '.text_header_box' });
  box.css('left',e.pageX+5 );
  box.css('top',e.pageY+5 );
  box.css('position',"absolute" );
  box.show();
}

$(document).ready(function(){
  hide_popup();
});
