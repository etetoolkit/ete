// Functions related to the top-right menus.

import { api } from "./api.js";
import { view, menus, on_tree_change,
         on_drawer_change, show_minimap, get_tid } from "./gui.js";
import { draw_minimap } from "./minimap.js";
import { update, draw_tree_scale, draw_aligned, update_aligned_panel_display } from "./draw.js";
import { add_folder_active } from "./active.js";

export { init_menus, update_folder_layouts };


// Init the menus on the top with all the options we can see and change.
function init_menus(trees) {
    menus.pane = new Tweakpane.Pane({
        container: div_tweakpane,
    }).addFolder({ 
        title: "Control panel", expanded: view.control_panel.show
    });

    const tab = menus.pane.addTab({ pages: [
        { title: "Layout" },
        { title: "Selections" },
        { title: "Advanced" },
    ]});
    create_menu_basic(tab.pages[0], trees);
    create_menu_selection(tab.pages[1]);
    create_menu_advanced(tab.pages[2])


    //const tab = menus.pane.addTab({ pages: [
        //{ title: "Tree view" },
        //{ title: "Representation" },
        //{ title: "Selection" },
    //]});
    //create_menu_main(tab.pages[0], trees);
    //create_menu_representation(tab.pages[1]);
    //create_menu_selection(tab.pages[2]);
}


function create_menu_basic(menu, trees) {
    
    // trees
    if (trees.length > 1) {
        const options = trees.reduce((opt, t) => ({ ...opt, [t]: t }), {});
        menu.addInput(view, "tree", {options: options}).on("change", () => {
            view.subtree = "";
            on_tree_change();
        });
    } else
        menu.addMonitor(view, "tree",
            { label: "tree" })


    // drawer
    const options = { "Rectangular": "RectFaces", "Circular": "CircFaces" };
    menu.addInput(view.drawer, "name", { label: "drawer", options: options })
        .on("change", on_drawer_change);

    // min collapse size
    menu.addInput(view, "min_size", { label: "collapse", 
        min: 1, max: 100, step: 1 }).on("change", update);

    // ultrametric
    menu.addInput(view, "ultrametric", { label: "ultrametric" }).on("change", 
        async () => {
            await api(`/trees/${get_tid()}/ultrametric`);
            update();
    })

    // topology only


    // layouts
    add_folder_layouts(menu, true);

    // minimap
    menus.minimap = menu.addInput(view.minimap, "show", { label: "show minimap" })
        .on("change", () => show_minimap(view.minimap.show));

    // tree scale legend
    menu.addInput(view.tree_scale, "show", { label: "show tree scale legend" })
        .on("change", draw_tree_scale);

    // zooms
    menu.addInput(view, "smart_zoom", { label: "zoom around node" });

    menu.addInput(view.aligned, "zoom", { label: "zoom in aligned panel" });

    // text select
    menu.addInput(view, "select_text", { label: "select text", position: 'left' })
      .on("change", () => {
        style("font").userSelect = (view.select_text ? "text" : "none");
        div_tree.style.cursor = (view.select_text ? "text" : "auto");
        div_aligned.style.cursor = (view.select_text ? "text" : "ew-resize");
        set_boxes_clickable(!view.select_text);
    });

    // upload 
    if (view.upload)
        menu.addButton({ title: "upload" }).on("click", view.upload);

    // download
    const folder_download = menu.addFolder({ title: "Download",
                                                    expanded: false });
    folder_download.addButton({ title: "newick" }).on("click", view.download.newick);
    folder_download.addButton({ title: "svg" }).on("click", view.download.svg);

    menu.addButton({ title: "share view" }).on("click", view.share_view);
    menu.addButton({ title: "Help" }).on("click", view.show_help);
}


function create_menu_advanced(menu) {
    add_folder_info(menu);

    add_folder_sort(menu);

    add_folder_view(menu);

    add_folder_zoom(menu);

    add_folder_circular(menu)

    add_folder_minimap(menu);

    add_folder_tree_scale(menu);

    add_folder_aligned(menu);
}


function add_folder_circular(menu) {
    const folder_circ = menu.addFolder({ title: "Circular mode", expanded: false });

    function update_with_minimap() {
        draw_minimap();
        update();
    }
    folder_circ.addInput(view, "rmin", { label: "min radius",
        format: v => v.toFixed(4) }).on("change", update_with_minimap);
    folder_circ.addInput(view.angle, "min", { label: "min angle", 
        min: -180, max: 180, step: 1 }).on("change", update_with_minimap);
    folder_circ.addInput(view.angle, "max", { label: "max angle", 
        min: -180, max: 180, step: 1 }).on("change", update_with_minimap);

    //add_folder_style(menu);

    //add_folder_layouts(menu);
}


function create_menu_selection(menu) {
    // filled dynamically in collapsed.js and select.js
    view.active.folder = menu.addFolder({ title: `Active ${view.active.nodes.length}` });
    add_folder_active();

    menus.selected = menu.addFolder({ title: "Selected", expanded: false });

    add_folder_searches(menu);
}


function add_folder_sort(menu) {
    const folder_sort = menu.addFolder({ title: "Sort",
                                                expanded: false });
    folder_sort.addButton({ title: "sort" }).on("click", view.sorting.sort);
    folder_sort.addInput(view.sorting, "key");
    folder_sort.addInput(view.sorting, "reverse");
}


function update_folder_layouts (){
    // Remove previous layout folders
    menus.layouts.children.forEach(ch => ch.dispose());

    // Place default layouts as first element
    const sorted_layouts = [...Object.keys(view.layouts)].sort();
    sorted_layouts.splice(sorted_layouts.indexOf("default"), 1);
    sorted_layouts.unshift("default");

    sorted_layouts.forEach(name => {
        const layout_folder = menus.layouts.addFolder({ title: name, expanded: true })
        const layouts = view.layouts[name];
        Object.keys(layouts).sort().forEach(layout =>
            layout_folder.addInput(view.layouts[name], layout).on("change", update))
    });
}


function add_folder_layouts(menu, expanded=true) {
    menus.layouts = menu.addFolder({ title: "Layouts", expanded: expanded });
    update_folder_layouts();
}


function add_folder_searches(menu) {
    menus.searches = menu.addFolder({ title: "Searched" });

    menus.searches.addButton({ title: "new search" }).on("click", view.search);
}


function add_folder_info(menu) {
    const folder_info = menu.addFolder({ title: "Info", expanded: false });
    
    menus.subtree = folder_info.addInput(view, "subtree", 
        { value: view.subtree }).on("change", on_tree_change);
    
    const folder_nodes = folder_info.addFolder({ title: "Nodes", expanded: true });
    folder_nodes.addMonitor(view, "nnodes", 
        { label: "visible", format: v => v.toFixed(0) });
    folder_nodes.addMonitor(view, "tnodes", 
        { label: "total", view: "text" });
    folder_nodes.addMonitor(view, "tleaves", 
        { label: "leaves", format: v => v.toFixed(0) });

    folder_info.addButton({ title: "show details" })
        .on("click", view.show_tree_info);
}


function add_folder_view(menu) {
    const folder_view = menu.addFolder({ title: "View", expanded: false });

    folder_view.addButton({ title: "reset view" }).on("click", view.reset_view)
    const folder_tl = folder_view.addFolder({ title: "Top-left corner" });
    folder_tl.addMonitor(view.tl, "x", { format: v => v.toFixed(3) });
    folder_tl.addMonitor(view.tl, "y", { format: v => v.toFixed(3) });
}


function add_folder_zoom(menu) {
    const folder_zoom = menu.addFolder({ title: "Zoom", expanded: false });

    folder_zoom.addInput(view.zoom, "x", {
        label: "Adjust zoom x", 
        format: v => v.toFixed(1),
        min: 1, max: div_tree.offsetWidth / view.tree_size.width }).on("change", update);

    folder_zoom.addInput(view.zoom, "a", {
        label: "Adjust zoom a", 
        format: v => v.toFixed(1),
        min: 1, max: div_tree.offsetWidth / view.tree_size.width }).on("change", update);

    folder_zoom.addInput(view, "zoom_sensitivity", {
        label: "Zoom sensitivity",
        format: v => v.toFixed(1),
        min: 0.1, max: 2, step: 0.1,
    }).on("change", () => {
        view.zoom.delta.in = 0.25 * view.zoom_sensitivity;
        view.zoom.delta.out = -0.2 * view.zoom_sensitivity;
    })
}


function set_boxes_clickable(clickable) {
    const value = clickable ? "auto" : "none";
    Array.from(div_tree.getElementsByClassName("fg_node")).forEach(
        e => e.style.pointerEvents = value);
}


function add_folder_style(menu) {
    const folder_style = menu.addFolder({ title: "Style", expanded: false });

    const folder_node = folder_style.addFolder({ title: "Node", 
                                                 expaded: false });

    const folder_box = folder_node.addFolder({ title: "Box", expanded: false });

    folder_box.add(view.node.box, "opacity", 0, 0.2).step(0.001).onChange(
        () => style("node").opacity = view.node.box.opacity);
    folder_box.addColor(view.node.box, "color").onChange(
        () => style("node").fill = view.node.box.color);

    const folder_dot = folder_node.addFolder("dot");

    folder_dot.add(view.node.dot, "radius", 0, 10).step(0.1).onChange(() =>
        Array.from(div_tree.getElementsByClassName("nodedot")).forEach(
            e => e.setAttribute("r", view.node.dot.radius)));

    folder_dot.add(view.node.dot, "opacity", 0, 1).step(0.01).onChange(
        () => style("nodedot").opacity = view.node.dot.opacity);

    const folder_outline = folder_style.addFolder("outline");

    folder_outline.add(view.outline, "opacity", 0, 1).step(0.1).onChange(
        () => style("outline").fillOpacity = view.outline.opacity);
    folder_outline.addColor(view.outline, "color").onChange(
        () => style("outline").fill = view.outline.color);
    folder_outline.add(view.outline, "width", 0.1, 10).onChange(
        () => style("outline").strokeWidth = view.outline.width);
    folder_outline.add(view.outline, "slanted").onChange(() => {
        update();
        draw_minimap();
    });

    const folder_lines = folder_style.addFolder("lines");

    const folder_length = folder_lines.addFolder("length");

    folder_length.addColor(view.line.length, "color").onChange(
        () => style("lengthline").stroke = view.line.length.color);
    folder_length.add(view.line.length, "width", 0.1, 10).onChange(
        () => style("lengthline").strokeWidth = view.line.length.width);

    const folder_children = folder_lines.addFolder("children");

    folder_children.addColor(view.line.children, "color").onChange(
        () => style("childrenline").stroke = view.line.children.color);
    folder_children.add(view.line.children, "width", 0.1, 10).onChange(
        () => style("childrenline").strokeWidth = view.line.children.width);
    folder_children.add(view.line.children, "pattern",
        ["solid", "dotted", "dotted - 2", "dotted - 4"])
        .onChange(() => {
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

    const folder_text = folder_style.addFolder("text");

    const folder_name = folder_text.addFolder("name");

    folder_name.addColor(view.name, "color").onChange(
        () => style("name").fill = view.name.color);

    const folder_padding = folder_name.addFolder("padding");

    folder_padding.add(view.name.padding, "left", -20, 200).onChange(update);
    folder_padding.add(view.name.padding, "vertical", 0, 1).step(0.01).onChange(
        update);
    folder_name.add(view.name, "font", ["sans-serif", "serif", "monospace"])
        .onChange(() => style("name").fontFamily = view.name.font);
    folder_name.add(view.name, "max_size", 1, 200).name("max size").onChange(
        update);

    view.font_sizes.scroller.max = create_font_size_scroller("max");
    folder_text.add(view.font_sizes, "auto").name("automatic size").onChange(
        () => {
            style("font").fontSize =
                view.font_sizes.auto ? "" : `${view.font_sizes.fixed}px`;

            if (view.font_sizes.auto && view.font_sizes.scroller.fixed)
                view.font_sizes.scroller.fixed.remove();
            else
                view.font_sizes.scroller.fixed = create_font_size_scroller();
    });

    function create_font_size_scroller(type) {
        return folder_text.add(view.font_sizes, type, 0.1, 50).onChange(
            () => {
                if (type == "fixed")
                    style("font").fontSize = `${view.font_sizes[type]}px`;
                else
                    update();
            });
    }

    const folder_array = folder_style.addFolder("array");

    folder_array.add(view.array, "padding", 0, 1).step(0.01).onChange(
        update);
}


function style(name) {
    const pos = {
        "line": 1,
        "lengthline": 2,
        "childrenline": 3,
        "nodedot": 4,
        "font": 6,
        "name": 7,
        "node": 8,
        "outline": 9,
    };
    return document.styleSheets[0].cssRules[pos[name]].style;
}


function add_folder_minimap(menu) {
    const folder_minimap = menu.addFolder(
        { title: "Minimap", expanded: false });

    folder_minimap.addInput(view.minimap, "width", { min: 1, max: 100 })
      .on("change", () => {
        if (view.drawer.type === "circ")
            view.minimap.height = view.minimap.width * div_tree.offsetWidth
                                                     / div_tree.offsetHeight;
        draw_minimap();
    });
    folder_minimap.addInput(view.minimap, "height", { min: 1, max: 100 })
      .on("change", () => {
        if (view.drawer.type === "circ")
            view.minimap.width = view.minimap.height * div_tree.offsetHeight
                                                     / div_tree.offsetWidth;
        draw_minimap();
    });
    menus.minimap = folder_minimap.addInput(view.minimap, "show")
        .on("change", () => show_minimap(view.minimap.show));
}


function add_folder_tree_scale(menu) {
    const folder_scale = menu.addFolder(
        { title: "Tree scale legend", expanded: false });

    folder_scale.addInput(view.tree_scale, "length", 
        { label: "width (px)", min: 10, max: 300 })
        .on("change", draw_tree_scale);

    folder_scale.addInput(view.tree_scale, "color", { view: "color" })
        .on("change", draw_tree_scale);

    folder_scale.addInput(view.tree_scale, "show")
        .on("change", draw_tree_scale); 
}


function add_folder_aligned(menu) {
    const folder_aligned = menu.addFolder(
        { title: "Aligned panel", expanded: false });

    folder_aligned.addInput(view.aligned, "adjust_zoom", 
        { label: "adjust zoom" });

    folder_aligned.addInput(view.aligned.header, "show", 
        { label: "show header" })
        .on("change",() => draw_aligned());

    folder_aligned.addInput(view.aligned.footer, "show", 
        { label: "show footer" })
        .on("change",() => draw_aligned());

    folder_aligned.addInput(view.aligned, "pos", { label: "position", 
                                                 min: 0, max: 100 })
        .on("change", () => div_aligned.style.width = `${100 - view.aligned.pos}%`);

    folder_aligned.addInput(view.aligned, "adjust_pos", { label: "adjust position" })
        .on("change", () => update_aligned_panel_display());

    folder_aligned.addInput(view.aligned, "padding", { label: "padding from tree", 
                                                 min: 0, max: 600 })
        .on("change", () => update_aligned_panel_display());
}
