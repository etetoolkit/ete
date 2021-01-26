'use strict';


// Global variables related to the current view on the tree.
// Most will be shown on the top-right gui (using dat.gui).
const view = {
  pos: {x: 0, y: 0},  // in-tree current pointer position
  tree_name: "HmuY.aln2",
  tree_id: 0,
  show_tree_info: () => show_tree_info(),
  download_newick: () => download_newick(),
  download_svg: () => download_svg(),
  download_image: () => download_image(),
  upload_tree: () => window.location.href = "upload_tree.html",
  drawer: "Full",
  tl: {x: 0, y: 0},  // in-tree coordinates of the top-left of the view
  zoom: {x: 0, y: 0},  // initially chosen depending on the size of the tree
  min_height: 6,
  update_on_drag: false,
  drag: {x0: 0, y0: 0, element: undefined},  // used when dragging
  select_text: false,
  node_opacity: 0,
  node_color: "#222",
  line_color: "#000",
  line_width: 1,
  rect_color: "#000",
  names_color: "#00A",
  lengths_color: "#888",
  font_family: "sans-serif",
  font_size_auto: true,
  font_size_scroller: undefined,
  font_size: 10,
  font_size_max: 15,
  minimap_show: true,
  minimap_zoom: {x: 1, y: 1},
  datgui: undefined
};


// Run when the page is loaded (the "main" function).
document.addEventListener("DOMContentLoaded", async () => {
  set_query_string_values();
  await reset_zoom(view.zoom.x === 0, view.zoom.y === 0);
  view.datgui = create_datgui();
  draw_minimap();
  update();
});


// Set values that have been given with the query string.
function set_query_string_values() {
  const unknown_params = [];
  const params = new URLSearchParams(location.search);

  for (const [param, value] of params) {
    if (param === "id")
      view.tree_id = Number(value);
    else if (param === "name")
      view.tree_name = value;
    else if (param === "x")
      view.tl.x = Number(value);
    else if (param === "y")
      view.tl.y = Number(value);
    else if (param === "w")
      view.zoom.x = div_tree.offsetWidth / Number(value);
    else if (param === "h")
      view.zoom.y = div_tree.offsetHeight / Number(value);
    else if (param === "drawer")
      view.drawer = value;
    else
      unknown_params.push(param);
  }

  if (unknown_params.length != 0)
    swal("Oops!",
      "There were unkonwn parameters passed: " + unknown_params.join(", "),
      "warning");
}


// Update when the window is resized too.
window.addEventListener("resize", update);  // we could also draw_minimap()


// Create the top-right box ("gui") with all the options we can see and change.
function create_datgui() {
  // Shortcut for getting the styles.
  const [style_line, style_rect, style_font, style_names, style_lengths,
    style_node] =
    [1, 2, 3, 4, 5, 6].map(i => document.styleSheets[1].cssRules[i].style);

  const dgui = new dat.GUI({autoPlace: false});
  div_datgui.appendChild(dgui.domElement);

  dgui.add(view.pos, "x").step(0.001).listen();
  dgui.add(view.pos, "y").step(0.001).listen();

  const dgui_tree = dgui.addFolder("tree");

  add_trees(dgui_tree).then(() => {
    dgui_tree.add(view, "show_tree_info").name("info");
    const dgui_download = dgui_tree.addFolder("download");
    dgui_download.add(view, "download_newick").name("newick");
    dgui_download.add(view, "download_svg").name("svg");
    dgui_download.add(view, "download_image").name("image");
    dgui_tree.add(view, "upload_tree").name("upload");
    add_drawers(dgui_tree);  // so they will be added in order
  });

  const dgui_ctl = dgui.addFolder("control");

  dgui_ctl.add(view.tl, "x").name("top-left x").onChange(update);
  dgui_ctl.add(view.tl, "y").name("top-left y").onChange(update);
  dgui_ctl.add(view.zoom, "x").name("zoom x").onChange(update);
  dgui_ctl.add(view.zoom, "y").name("zoom y").onChange(update);
  dgui_ctl.add(view, "min_height", 1, 100).name("collapse at").onChange(update);
  dgui_ctl.add(view, "update_on_drag").name("update on drag");
  dgui_ctl.add(view, "select_text").name("select text").onChange(() => {
    style_font.userSelect = (view.select_text ? "text" : "none");
    div_tree.style.cursor = (view.select_text ? "text" : "auto");
    Array.from(div_tree.getElementsByClassName("rect")).forEach(
      e => e.style.pointerEvents = (view.select_text ? "none" : "auto"));
  });

  const dgui_style = dgui.addFolder("style");

  const dgui_style_node = dgui_style.addFolder("node");

  dgui_style_node.add(view, "node_opacity", 0, 1).name("opacity").onChange(() =>
    style_node.opacity = view.node_opacity);
  dgui_style_node.addColor(view, "node_color").name("color").onChange(() =>
    style_node.fill = view.node_color);

  const dgui_style_line = dgui_style.addFolder("line");

  dgui_style_line.addColor(view, "line_color").name("color").onChange(() =>
    style_line.stroke = view.line_color);
  dgui_style_line.add(view, "line_width", 0.1, 10).name("width").onChange(() =>
    style_line.strokeWidth = view.line_width);

  const dgui_style_text = dgui_style.addFolder("text");

  dgui_style_text.addColor(view, "names_color").name("names").onChange(() =>
    style_names.fill = view.names_color);
  dgui_style_text.addColor(view, "lengths_color").name("lengths").onChange(() =>
    style_lengths.fill = view.lengths_color);
  dgui_style_text.add(view, "font_family", ["sans-serif", "serif", "monospace"])
    .name("font").onChange(() => style_font.fontFamily = view.font_family);
  dgui_style_text.add(view, "font_size_auto").name("automatic size").onChange(() => {
    style_font.fontSize = (view.font_size_auto ? "" : `${view.font_size}px`);
    if (view.font_size_auto && view.font_size_scroller)
      view.font_size_scroller.remove();
    else
      view.font_size_scroller = create_font_size_scroller();
  });
  dgui_style_text.add(view, "font_size_max", 1, 100).name("max size auto")
    .onChange(update);

  function create_font_size_scroller() {
    return dgui_style_text.add(view, "font_size", 0.1, 50).name("font size")
      .onChange(() => style_font.fontSize = `${view.font_size}px`);
  }

  const dgui_style_collapsed = dgui_style.addFolder("collapsed");

  dgui_style_collapsed.addColor(view, "rect_color").name("color").onChange(() =>
    style_rect.stroke = view.rect_color);

  dgui.add(view, "minimap_show").name("minimap").onChange(() => {
      const status = (view.minimap_show ? "visible" : "hidden");
      div_minimap.style.visibility = div_visible_rect.style.visibility = status;
      if (view.minimap_show)
        update_minimap_visible_rect();
    });

  return dgui;
}


// Return the data coming from an api endpoint (like "/trees/<id>/size").
async function api(endpoint) {
  const response = await fetch(endpoint);
  return await response.json();
}


// Populate the trees option in dat.gui with the trees available in the server.
async function add_trees(dgui_tree) {
  const data = await api("/trees");
  const trees = {};
  data.map(t => trees[t.name] = t.id);
  dgui_tree.add(view, "tree_name", Object.keys(trees)).name("name")
    .onChange(async () => {
      div_tree.style.cursor = "wait";
      view.tree_id = trees[view.tree_name];
      view.tl.x = 0;
      view.tl.y = 0;
      await reset_zoom();
      draw_minimap();
      update();
    });
}


// Set the zoom so the full tree fits comfortably on the screen.
async function reset_zoom(reset_zx=true, reset_zy=true) {
  if (reset_zx || reset_zy) {
    const size = await api(`/trees/${view.tree_id}/size`);
    if (reset_zx)
      view.zoom.x = 0.5 * div_tree.offsetWidth / size.width;
    if (reset_zy)
      view.zoom.y = div_tree.offsetHeight / size.height;
  }
}


async function add_drawers(dgui_tree) {
  const drawers = await api("/trees/drawers");
  dgui_tree.add(view, "drawer", drawers).onChange(update);
}


// Return an url with the view of the given rectangle of the tree.
function get_url_view(x, y, w, h) {
  const qs = new URLSearchParams({x: x, y: y, w: w, h: h,
    id: view.tree_id, name: view.tree_name, drawer: view.drawer});
  return window.location.href.split('?')[0] + "?" + qs.toString();
}


// Show an alert with information about the current tree and view.
async function show_tree_info() {
  const info = await api(`/trees/${view.tree_id}`);
  const url = get_url_view(view.tl.x, view.tl.y,
    div_tree.offsetWidth / view.zoom.x, div_tree.offsetHeight / view.zoom.y);

  swal("Tree Information",
    `Id: ${info.id}\n` +
    `Name: ${info.name}\n` +
    (info.description ? `Description: ${info.description}\n` : "") + "\n\n" +
    `URL of the current view:\n\n${url}`);
}


// Download a file with the newick representation of the tree.
async function download_newick() {
  const newick = await api(`/trees/${view.tree_id}/newick`);
  download(view.tree_name + ".tree", "data:text/plain;charset=utf-8," + newick);
}


// Download a file with the current view of the tree as a svg.
function download_svg() {
  const svg = div_tree.children[0].cloneNode(true);
  Array.from(svg.getElementsByClassName("noderect")).forEach(e => e.remove());
  const svg_xml = (new XMLSerializer()).serializeToString(svg);
  const content = "data:image/svg+xml;base64," + btoa(svg_xml);
  download(view.tree_name + ".svg", content);
}


// Download a file with the current view of the tree as a png.
function download_image() {
  const canvas = document.createElement("canvas");
  canvas.width = div_tree.offsetWidth;
  canvas.height = div_tree.offsetHeight;
  const svg = div_tree.children[0].cloneNode(true);
  Array.from(svg.getElementsByClassName("noderect")).forEach(e => e.remove());
  const svg_xml = (new XMLSerializer()).serializeToString(svg);
  const ctx = canvas.getContext("2d");
  const img = new Image();
  img.src = "data:image/svg+xml;base64," + btoa(svg_xml);
  img.addEventListener("load", () => {
    ctx.drawImage(img, 0, 0);
    download(view.tree_name + ".png", canvas.toDataURL("image/png"));
  });
}


// Make the browser download a file.
function download(fname, content) {
  const element = document.createElement("a");
  element.setAttribute("href", encodeURI(content));
  element.setAttribute("download", fname);
  element.style.display = "none";
  document.body.appendChild(element);
  element.click();
  document.body.removeChild(element);
}


// Use the mouse wheel to zoom in/out (instead of scrolling).
document.body.addEventListener("wheel", event => {
  event.preventDefault();
  const zr = (event.deltaY < 0 ? 1.25 : 0.8);  // zoom change (ratio)

  const [do_zoom_x, do_zoom_y] = [!event.altKey, !event.ctrlKey];

  if (do_zoom_x) {
    const zoom_new = zr * view.zoom.x;
    view.tl.x += (1 / view.zoom.x - 1 / zoom_new) * event.pageX;
    view.zoom.x = zoom_new;
  }

  if (do_zoom_y) {
    const zoom_new = zr * view.zoom.y;
    view.tl.y += (1 / view.zoom.y - 1 / zoom_new) * event.pageY;
    view.zoom.y = zoom_new;
  }

  if (do_zoom_x || do_zoom_y)
    update();
}, {passive: false});  // chrome now uses passive=true otherwise


// Mouse down -- select text, or move in minimap, or start dragging.
document.addEventListener("mousedown", event => {
  if (view.select_text) {
    ;  // if by clicking we can select text, don't do anything else
  }
  else if (div_visible_rect.contains(event.target)) {
    view.drag.element = div_visible_rect;
    drag_start(event);
  }
  else if (div_minimap.contains(event.target)) {
    move_minimap_view(event);
  }
  else if (div_tree.contains(event.target)) {
    view.drag.element = div_tree;
    drag_start(event);
  }
});


document.addEventListener("mouseup", event => {
  if (view.drag.element) {
    drag_stop(event);
    update_tree();
  }

  view.drag.element = undefined;
});


document.addEventListener("mousemove", event => {
  update_pointer_pos(event);

  if (view.drag.element) {
    drag_stop(event);

    if (view.update_on_drag)
      update_tree();

    const g = div_tree.children[0].children[0];
    g.setAttribute("transform",
      `translate(${-view.zoom.x * view.tl.x} ${-view.zoom.y * view.tl.y})`);

    view.datgui.updateDisplay();  // update the info box on the top-right
    if (view.minimap_show)
      update_minimap_visible_rect();

    drag_start(event);
  }
});


function drag_start(event) {
  div_tree.style.cursor = div_visible_rect.style.cursor = "grabbing";

  view.drag.x0 = event.pageX;
  view.drag.y0 = event.pageY;
}


function drag_stop(event) {
  div_tree.style.cursor = "auto";
  div_visible_rect.style.cursor = "grab";

  const dx = event.pageX - view.drag.x0,  // mouse position increment
        dy = event.pageY - view.drag.y0;

  if (dx != 0 || dy != 0) {
    const [scale_x, scale_y] = get_drag_scale();
    view.tl.x += scale_x * dx;
    view.tl.y += scale_y * dy;
  }
}


function get_drag_scale() {
  if (view.drag.element === div_tree)
    return [-1 / view.zoom.x, -1 / view.zoom.y];
  else if (view.drag.element === div_visible_rect)
    return [1 / view.minimap_zoom.x, 1 / view.minimap_zoom.y];
  else
    console.log(`Cannot find dragging scale for ${view.drag.element}.`);
}


// Move the current tree view to the given mouse position in the minimap.
function move_minimap_view(event) {
  // Top-left pixel coordinates of the tree (0, 0) position in the minimap.
  const [x0, y0] = [div_minimap.offsetLeft + 6, div_minimap.offsetTop + 6];

  // Size of the visible rectangle.
  const [w, h] = [div_visible_rect.offsetWidth, div_visible_rect.offsetHeight];

  view.tl.x = (event.pageX - w/2 - x0) / view.minimap_zoom.x;
  view.tl.y = (event.pageY - h/2 - y0) / view.minimap_zoom.y;
  // So the center of the visible rectangle will be where the mouse is.

  update();
}


// Update the coordinates of the pointer, as shown in the top-right gui.
function update_pointer_pos(event) {
  view.pos.x = view.tl.x + event.pageX / view.zoom.x;
  view.pos.y = view.tl.y + event.pageY / view.zoom.y;
}


// Update the view of all elements (gui, tree, minimap).
function update() {
  view.datgui.updateDisplay();  // update the info box on the top-right

  update_tree();

  if (view.minimap_show)
    update_minimap_visible_rect();
}


// Ask the server for a tree in the new defined region, and draw it.
async function update_tree() {
  const [zx, zy] = [view.zoom.x, view.zoom.y];
  const [x, y] = [view.tl.x, view.tl.y];
  const [w, h] = [div_tree.offsetWidth / zx, div_tree.offsetHeight / zy];

  div_tree.style.cursor = "wait";

  const qs = `drawer=${view.drawer}&min_height=${view.min_height}&` +
    `zx=${zx}&zy=${zy}&x=${x}&y=${y}&w=${w}&h=${h}`;
  const items = await api(`/trees/${view.tree_id}/draw?${qs}`);

  draw(div_tree, items, view.tl, view.zoom);

  div_tree.style.cursor = "auto";
}


function create_svg_element(name, attrs) {
  const element = document.createElementNS("http://www.w3.org/2000/svg", name);
  for (const [attr, value] of Object.entries(attrs))
    element.setAttributeNS(null, attr, value);
  return element;
}


// Append a svg to the given element, with all the items in the list drawn.
function draw(element, items, tl, zoom) {
  const svg = create_svg_element("svg", {
    "width": element.offsetWidth, "height": element.offsetHeight});

  if (element.children.length > 0)
    element.children[0].replaceWith(svg);
  else
    element.appendChild(svg);

  const g = create_svg_element("g", {
    "transform": `translate(${-zoom.x * tl.x} ${-zoom.y * tl.y})`});

  svg.appendChild(g);

  items.forEach(item => g.appendChild(item2svg(item, zoom)));
}


// Return svg to draw the element, taking into account if it is aligned.
function item2svg(item, zoom) {
  if (item[0] === 'a') {  // aligned
    const dx = zoom.x * view.tl.x + div_tree.offsetWidth - 200;
    const g = create_svg_element("g", { "transform": `translate(${dx} 0)`});
    g.appendChild(item2svgelement(item.slice(1), zoom));
    return g;
    // TODO: put the content in a different panel instead, maybe creating it
    //   with <iframe srcdoc=...>.
  }
  else {
    return item2svgelement(item, zoom);
  }
}


// Return the graphical (svg) element corresponding to a drawer item.
function item2svgelement(item, zoom) {
  // items look like ['r', ...] for a rectangle, etc.
  if (item[0].startsWith('r')) {       // rectangle
    const [rect_type, x, y, w, h, name, properties] = item;

    const r = create_svg_element("rect",
      {"class": "rect " + get_class(rect_type),
       "x": zoom.x * x, "y": zoom.y * y,
       "width": zoom.x * w, "height": zoom.y * h,
       "stroke": view.rect_color});

    r.addEventListener("click", event => {
      if (event.detail === 2 || event.ctrlKey) {  // double-click or ctrl-click
        view.tl.x = x;
        view.tl.y = y;
        view.zoom.x = div_tree.offsetWidth / w;
        view.zoom.y = div_tree.offsetHeight / h;
        update();
      }
    });

    if (name.length > 0 || Object.entries(properties).length > 0) {
      const title = create_svg_element("title", {});
      const text = name + "\n" +
        Object.entries(properties).map(x => x[0] + ": " + x[1]).join("\n");
      title.appendChild(document.createTextNode(text));
      r.appendChild(title);
    }

    return r;
  }
  else if (item[0] === 'l') {  // line
    const [ , x1, y1, x2, y2] = item;

    return create_svg_element("line", {
      "class": "line",
      "x1": zoom.x * x1, "y1": zoom.y * y1,
      "x2": zoom.x * x2, "y2": zoom.y * y2,
      "stroke": view.line_color});
  }
  else if (item[0].startsWith('t')) {  // text
    const [text_type, x, y, w, h, txt] = item;

    const [zw, zh] = [zoom.x * w, zoom.y * h];
    const fs = Math.min(view.font_size_max, zh, 1.5 * zw / txt.length);

    const t = create_svg_element("text", {
      "class": "text " + get_class(text_type),
      "x": zoom.x * x, "y": zoom.y * y,
      "font-size": `${w >= 0 ? fs : zh}px`});
    t.appendChild(document.createTextNode(txt));
    return t;
    // NOTE: If we wanted to use the exact width of the item, we could add:
    //   textLength="${w}px"
  }
}


function get_class(element_type) {
  if (element_type === "tn")
    return "names";
  else if (element_type === "tl")
    return "lengths";
    else if (element_type === "tt")
    return "tooltip";
  else if (element_type === "rn")
    return "noderect";
  else if (element_type === "ro")
    return "outlinerect";
  else
    return "";
}


// Draw the full tree on a small div on the bottom-right ("minimap").
async function draw_minimap() {
  const size = await api(`/trees/${view.tree_id}/size`);
  const zx = div_minimap.offsetWidth / size.width,
        zy = div_minimap.offsetHeight / size.height;

  view.minimap_zoom = {x: zx, y: zy};

  const qs = `drawer=Simple&zx=${zx}&zy=${zy}`;
  const items = await api(`/trees/${view.tree_id}/draw?${qs}`);

  draw(div_minimap, items, {x: 0, y: 0}, view.minimap_zoom);

  Array.from(div_minimap.getElementsByClassName("noderect")).forEach(
    e => e.remove());

  update_minimap_visible_rect();
}


// Update the minimap's rectangle that represents the current view of the tree.
function update_minimap_visible_rect() {
  const [w_min, h_min] = [5, 5];  // minimum size of the rectangle
  const [round, min, max] = [Math.round, Math.min, Math.max];  // shortcuts

  // Transform all measures into "minimap units" (scaling accordingly).
  const mbw = 3, rbw = 1;  // border-width from .minimap and .visible_rect css
  const mw = div_minimap.offsetWidth - 2 * (mbw + rbw),    // minimap size
        mh = div_minimap.offsetHeight - 2 * (mbw + rbw);
  const wz = view.zoom, mz = view.minimap_zoom;
  const ww = round(mz.x / wz.x * div_tree.offsetWidth),  // viewport size (scaled)
        wh = round(mz.y / wz.y * div_tree.offsetHeight);
  const tx = round(mz.x * view.tl.x),  // top-left corner of visible area
        ty = round(mz.y * view.tl.y);  //   in tree coordinates (scaled)

  const x = max(0, min(tx, mw)),  // clip tx to the interval [0, mw]
        y = max(0, min(ty, mh)),
        w = max(w_min, ww) + min(tx, 0),
        h = max(h_min, wh) + min(ty, 0);

  const rs = div_visible_rect.style;
  rs.left = `${div_minimap.offsetLeft + mbw + x}px`;
  rs.top = `${div_minimap.offsetTop + mbw + y}px`;
  rs.width = `${max(1, min(w, mw - x))}px`;
  rs.height = `${max(1, min(h, mh - y))}px`;
}
