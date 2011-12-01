/*  it requires jquery loaded */

var ete_webplugin_URL = "http://jaime.phylomedb.org/wsgi/webplugin.py";
var loading_img = '<img border=0 src="/webplugin/loader.gif">';

function draw_tree(treeid, newick, alignment, recipient, extra_params){
    var params = {"tree": newick, "treeid": treeid, "alignment": alignment};
  if ( extra_params != undefined ){
    var params =  $.extend(params, extra_params);
    }

  $(recipient).html(loading_img);
  $(recipient).load(ete_webplugin_URL+'/draw', params);
}

Object.extend = function(destination, source) {
    for (var property in source)
        destination[property] = source[property];
    return destination;
};

function load_model(treeid, model){
    var recipient = "#ETE_tree_"+treeid;
    $(recipient).html(loading_img);
    $(recipient).load(ete_webplugin_URL+'/action', {"treeid": treeid, "nid": 1, "aindex": "2", "loadmodel": model});
}

function run_model(treeid, model, extra_params){
    var recipient = "#ETE_tree_"+treeid;
    var params = {"MODEL": model};
    for (var par in extra_params)
	params[par] = extra_params [par];
    $(recipient).html(loading_img);
    $(recipient).load(ete_webplugin_URL+'/action', {"treeid": treeid, "nid": 1, "aindex": "1", "run_params": params});
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
  $(recipient).html(loading_img);
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


function ncchisqdf(x,f,theta) {
    with (Math) {
	var n=1;
	var lam=theta/2;
	var pois=exp(-lam);
	var v=pois;
	var x2=x/2;
	var f2=f/2;
	var t=pow(x2,f2)*exp(-x2-LogGamma(f2+1));
	var chisq=v*t;
	while (n<=(x-f)/2) {
	    pois=pois*lam/n;
	    v=v+pois;
	    t=t*x/(f+2*n);
	    chisq=chisq+v*t;
	    n=n+1;
	}
	while (t*x/(f+2*n-x)>.000001) {
	    pois=pois*lam/n;
	    v=v+pois;
	    t=t*x/(f+2*n);
	    chisq=chisq+v*t;
	    n=n+1;
	}
	return chisq
	    }
}

function LogGamma(Z) {
    with (Math) {
	var S=1+76.18009173/Z-86.50532033/(Z+1)+24.01409822/(Z+2)-1.231739516/(Z+3)+.00120858003/(Z+4)-.00000536382/(Z+5);
	var LG= (Z-.5)*log(Z+4.5)-(Z+4.5)+log(S*2.50662827465);
    }
    return LG
} 

function calculate(values) {
    var deltalnl = 2*(values [0][0] - values [1][0]);
    Z=eval(deltalnl)
	DF=eval(values [0][1]-values [1][1])
	Theta=0
	with (Math) {
	if (DF<=0) {
	    alert("This is not a null model.")
	} else if (Theta<0) {
	    alert("Noncentrality parameter must be non-negative")
	} else if (Z<=0) {
	    Ncchisq=0
	} else {
	    Ncchisq=ncchisqdf(Z,DF,Theta)
	}
	Ncchisq=round(Ncchisq*100000)/100000;
    }
    values[2].value = 1-Ncchisq;
    values[3].innerHTML = "2 delta lnL: "+Math.round(deltalnl*100)/100+", DF: "+DF;
}


