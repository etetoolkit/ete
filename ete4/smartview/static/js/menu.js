// Functions related to the top-right menus.

import { view, menus, to_opts, on_tree_change, on_shape_change, show_minimap }
    from "./gui.js";
import { draw_minimap } from "./minimap.js";
import { update } from "./draw.js";
import { Pane } from "../external/tweakpane.min.js";

export { init_menus };


// Init the menus on the top with all the options we can see and change.
function init_menus(trees) {
    const pane = new Pane({
        title: "Control panel",
        container: div_menu,
        expanded: true, ///////false,
    });
    menus.pane = pane;

    const tab = pane.addTab({
        pages: [
            {title: "Main"},
            {title: "Selections"},
            {title: "Advanced"}]});
    const [tab_main, tab_selections, tab_advanced] = tab.pages;

    add_tab_main(tab_main, trees);
    add_tab_selections(tab_selections);
    add_tab_advanced(tab_advanced);
}


// === Tab Main ===

function add_tab_main(tab, trees) {
    tab.addBinding(view, "tree", {label: "tree", options: to_opts(trees)})
      .on("change", () => {
        view.subtree = "";
        on_tree_change();
      });

    const folder_download = folder(tab, "download");
    folder_download.addButton({title: "newick"}).on("click", view.download.newick);
    folder_download.addButton({title: "svg"}).on("click", view.download.svg);
    folder_download.addButton({title: "image"}).on("click", view.download.image);

    tab.addButton({title: "upload"}).on("click", view.upload);

    tab.addBinding(view, "shape", {label: "shape",
                                    options: to_opts(["rectangular", "circular"])})
        .on("change", on_shape_change);

    tab.addBinding(view, "min_size", {label: "collapse size", min: 1, max: 200})
        .on("change", update);

    menus.layouts = folder(tab, "layouts", true);  // filled dynamically

    const folder_labels = folder(tab, "extra labels");
    menus.labels = folder_labels;

    const folder_properties = folder(folder_labels, "properties", true);
    menus.node_properties = folder_properties;

    folder_properties.addBinding(view, "current_property",
                                 {label: "properties",
                                  options: to_opts(view.node_properties)});
    folder_properties.addButton({title: "add property"})
        .on("click", view.label_property);

    folder_labels.addButton({title: "add expression"})
        .on("click", view.label_expression);

    tab.addBinding(view, "select_text", {label: "select text"}).on("change", () => {
        style("font").userSelect = (view.select_text ? "text" : "none");
        div_tree.style.cursor = (view.select_text ? "text" : "auto");
        div_aligned.style.cursor = (view.select_text ? "text" : "ew-resize");
        set_boxes_clickable(!view.select_text);
    });

    tab.addBinding(view, "smart_zoom", {label: "smart zoom"});
    tab.addButton({title: "share view"}).on("click", view.share_view);
    tab.addButton({title: "help"}).on("click", view.show_help);
}

function set_boxes_clickable(clickable) {
    const value = clickable ? "auto" : "none";
    Array.from(div_tree.getElementsByClassName("fg_node")).forEach(
        e => e.style.pointerEvents = value);
}


// === Tab Selections ===

function add_tab_selections(tab) {
    menus.collapsed = folder(tab, "manually collapsed");  // filled dynamically

    menus.selections = folder(tab, "tags");  // filled dynamically with tag_node()

    add_folder_searches(tab);
}

function add_folder_searches(menu) {
    const folder_searches = folder(menu, "searches");
    menus.searches = folder_searches;

    folder_searches.addButton({title: "new search"}).on("click", view.search);
}


// === Tab Advanced ===

function add_tab_advanced(tab) {
    tab.addBinding(view, "subtree").on("change", on_tree_change);

    const folder_sort = folder(tab, "sort");
    folder_sort.addBinding(view.sorting, "key");
    folder_sort.addBinding(view.sorting, "reverse");
    folder_sort.addButton({title: "apply"}).on("click", view.sorting.sort)

    const folder_circ = folder(tab, "circular");

    function update_with_minimap() {
        draw_minimap();
        update();
    }
    folder_circ.addBinding(view, "rmin", {label: "radius min"})
        .on("change", update_with_minimap);
    folder_circ.addBinding(view.angle, "min", {label: "angle min", min: -180, max: 180})
        .on("change", update_with_minimap);
    folder_circ.addBinding(view.angle, "max", {label: "angle max", min: -180, max: 180})
        .on("change", update_with_minimap);

    add_folder_info(tab);
    add_folder_viewport(tab);
    add_folder_style(tab);
    add_folder_minimap(tab);
}


// Functions to populate the tab advanced.

function add_folder_info(menu) {
    const folder_info = folder(menu, "info");

    const folder_nodes = folder(folder_info, "nodes", true);
    folder_nodes.addBinding(view, "nnodes_visible",
        {readonly: true, label: "visible", format: x => x.toFixed(0)});
    folder_nodes.addBinding(view, "nnodes",
        {readonly: true, label: "total", format: x => x.toFixed(0)});
    folder_nodes.addBinding(view, "nleaves",
        {readonly: true, label: "leaves", format: x => x.toFixed(0)});

    const folder_position = folder(folder_info, "pointer position", true);
    folder_position.addBinding(view.pos, "cx", {readonly: true, label: "x"});
    folder_position.addBinding(view.pos, "cy", {readonly: true, label: "y"});

    folder_info.addButton({title: "show details"}).on("click", view.show_tree_info);
}


function add_folder_viewport(menu) {
    const folder_viewport = folder(menu, "viewport");

    folder_viewport.addButton({title: "reset view"}).on("click", view.reset_view);

    // FIXME: Commented out for the moment, since we cannot initialize the menus
    // if  view.tl.x == null  (and so on) otherwise.

    // const folder_tl = folder(folder_viewport, "top-left");
    // folder_tl.addBinding(view.tl, "x", {readonly: true});
    // folder_tl.addBinding(view.tl, "y", {readonly: true});

    // const folder_zoom = folder(folder_viewport, "zoom");
    // folder_zoom.addBinding(view.zoom, "x", {readonly: true});
    // folder_zoom.addBinding(view.zoom, "y", {readonly: true});

    const folder_aligned = folder(folder_viewport, "aligned bar");
    folder_aligned.addBinding(view, "align_bar",
        {readonly: true, label: "current position"});
    folder_aligned.addBinding(view, "align_bar",
        {readonly: true, min: 0, max: 100, label: "set position"})
        .on("change", (ev) => div_aligned.style.width = `${100 - ev.value}%`);
}


function add_folder_style(menu) {
    const folder_style = folder(menu, "style");

    const folder_node = folder(folder_style, "node");

    const folder_box = folder(folder_node, "box", true);

    folder_box.addBinding(view.node.box, "opacity", {min: 0, max: 0.2, step: 0.001})
      .on("change", () => style("node").opacity = view.node.box.opacity);
    folder_box.addBinding(view.node.box, "color").on("change",
        () => style("node").fill = view.node.box.color);

    const folder_dot = folder(folder_node, "dot", true);

    folder_dot.addBinding(view.node.dot, "radius", {min: 0, max: 10, step: 0.1})
      .on("change", () => {
        Array.from(div_tree.getElementsByClassName("nodedot")).forEach(
            e => e.setAttribute("r", view.node.dot.radius));
        update();
      });

    folder_dot.addBinding(view.node.dot, "opacity", {min: 0, max: 1, step: 0.01})
        .on("change", () => style("nodedot").opacity = view.node.dot.opacity);
    folder_dot.addBinding(view.node.dot, "color")
        .on("change", () => style("nodedot").fill = view.node.dot.color);

    const folder_outline = folder(folder_style, "outline");

    folder_outline.addBinding(view.outline, "opacity", {min: 0, max: 1, step: 0.1})
        .on("change", () => style("outline").fillOpacity = view.outline.opacity);
    folder_outline.addBinding(view.outline, "color")
        .on("change", () => style("outline").fill = view.outline.color);
    folder_outline.addBinding(view.outline, "width", {min: 0.1, max: 10})
        .on("change", () => style("outline").strokeWidth = view.outline.width);

    const folder_lines = folder(folder_style, "lines");

    const folder_length = folder(folder_lines, "length", true);

    folder_length.addBinding(view.line.length, "color")
        .on("change", () => style("distline").stroke = view.line.length.color);
    folder_length.addBinding(view.line.length, "width", {min: 0.1, max: 10})
        .on("change",
            () => style("distline").strokeWidth = view.line.length.width);

    const folder_children = folder(folder_lines, "children", true);

    folder_children.addBinding(view.line.children, "color")
        .on("change", () => style("childrenline").stroke = view.line.children.color);
    folder_children.addBinding(view.line.children, "width", {min: 0.1, max: 10})
        .on("change",
            () => style("childrenline").strokeWidth = view.line.children.width);
    folder_children.addBinding(view.line.children, "pattern",
          {options: to_opts(["solid", "dotted", "dotted - 2", "dotted - 4"])})
        .on("change", () => {
            const pattern = view.line.children.pattern;
            if (pattern === "solid")
                style("childrenline").strokeDasharray = "";
            else if (pattern === "dotted")
                style("childrenline").strokeDasharray = "1";
            else if (pattern === "dotted - 2")
                style("childrenline").strokeDasharray = "2";
            else if (pattern === "dotted - 4")
                style("childrenline").strokeDasharray = "4";
        });

    const folder_text = folder(folder_style, "text");

    folder_text.addBinding(view.font_sizes, "auto", {label: "automatic size"})
      .on("change",
        () => {
            style("font").fontSize =
                view.font_sizes.auto ? "" : `${view.font_sizes.fixed}px`;

            if (view.font_sizes.auto && view.font_sizes.scroller)
                view.font_sizes.scroller.dispose();
            else
                view.font_sizes.scroller = create_font_size_scroller();
      });

    function create_font_size_scroller() {
        return folder_text.addBinding(view.font_sizes, "fixed", {min: 0.1, max: 50})
            .on("change",
                () => style("font").fontSize = `${view.font_sizes.fixed}px`);
    }

    const folder_array = folder(folder_style, "array");

    folder_array.addBinding(view.array, "padding", {min: 0, max: 1, step: 0.01})
        .on("change", update);
}


function add_folder_minimap(menu) {
    const folder_minimap = folder(menu, "minimap");

    folder_minimap.addBinding(view.minimap, "width", {min: 1, max: 100})
      .on("change", () => {
        if (view.shape === "circular") {
            view.minimap.height = view.minimap.width * div_tree.offsetWidth
                                                     / div_tree.offsetHeight;
        }
        draw_minimap();
      });
    folder_minimap.addBinding(view.minimap, "height", {min: 1, max: 100})
      .on("change", () => {
        if (view.shape === "circular") {
            view.minimap.width = view.minimap.height * div_tree.offsetHeight
                                                     / div_tree.offsetWidth;
        }
        draw_minimap();
      });
    folder_minimap.addBinding(view.minimap, "show")
        .on("change", () => show_minimap(view.minimap.show));
}


// Helper functions.

function style(name) {
    // Based on the order in which they appear in gui.css.
    const pos = {
        "line": 1,
        "distline": 2,
        "childrenline": 3,
        "nodedot": 4,
        "font": 6,
        "node": 7,
        "outline": 8,
    };
    return document.styleSheets[0].cssRules[pos[name]].style;
}


// Return a new folder on element, collapsed and with the given name.
function folder(element, name, expanded=false) {
    return element.addFolder({title: name, expanded: expanded});
}
