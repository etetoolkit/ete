// Main file for the gui.

import { init_menus, update_folder_layouts } from "./menu.js";
import { init_events, notify_parent } from "./events.js";
import { update } from "./draw.js";
import { download_newick, download_svg } from "./download.js";
import { activate_node, deactivate_node } from "./active.js";
import { search, get_searches, remove_searches } from "./search.js";
import { get_selections, remove_selections } from "./select.js";
import { get_active_nodes } from "./active.js";
import { zoom_into_box, zoom_around, zoom_towards_box } from "./zoom.js";
import { draw_minimap, update_minimap_visible_rect } from "./minimap.js";
import { api, api_put, escape_html } from "./api.js";
import { remove_collapsed } from "./collapse.js";

export { view, menus, on_tree_change, on_drawer_change, show_minimap,
         tree_command, get_tid, on_box_click, on_box_wheel, 
         on_box_mouseenter, on_box_mouseleave, coordinates,
         reset_view, show_help, sort, get_active_layouts };


// Run main() when the page is loaded.
document.addEventListener("DOMContentLoaded", main);


// Global variables related to the current view on the tree.
// Most will be shown on the top-right gui (using Tweakpane).
const view = {
    path: "",  // path when adding app to werkzeug.wsgi.DispatchMiddleWare server
    // tree
    tree: null,  // string with the current tree name
    tree_size: {width: 0, height: 0},
    ultrametric: false,
    subtree: "",  // node id of the current subtree; looks like "0,1,0,0,1"
    sorting: {
        sort: () => sort(),
        key: "(dy, dx, name)",
        reverse: false,
    },
    upload: () => window.location.href = "upload_tree.html",
    download: {
        newick: () => download_newick(),
        svg:    () => download_svg(),
    },
    allow_modifications: true,

    // representation
    drawer: {name: "RectFaces", type: "rect", npanels: 1},  // default drawer
    min_size: 15,  // for less pixels, the drawer will collapse things
    current_property: "name",  // pre-selected property in the add label menu
    rmin: 0,
    angle: {min: -180, max: 180},
    tooltip: {
        timeout: undefined,
    },
    aligned: {
        x: -10,
        pos: 80,  // % of the screen width where the aligned panel starts
        adjust_pos: false,
        padding: 200,
        timeout: 100,  // ms to refresh
        zoom: false,
        max_zoom: undefined,
        adjust_zoom: true,
        header: {
            show: true, height: 50 },
        footer: {
            show: true, height: 50 },
    },
    collapsed_ids: {},

    layouts: {},

    // selected
    selected: {},  // will contain the selected nodes (saved)
    active: {
        nodes: [],    // will contain list of active nodes
        color: "#b3004b",
        opacity: 0.4,
        remove: undefined,
        folder: undefined,
        buttons: [],
    },

    // searches
    search: () => search(),
    search_cache: undefined,  // last search if not successful
    searches: {},  // will contain the searches done

    // info
    nnodes: 0,  // number of visible nodeboxes
    tnodes: 0,  // number of total nodeboxes
    tleaves: 0,  // number of total leaves (outer nodeboxes)
    pos: {cx: 0, cy: 0},  // in-tree current pointer position
    show_tree_info: () => show_tree_info(),

    // view
    reset_view: () => reset_view(),
    tl: {x: null, y: null},  // top-left of the view (in tree coordinates)
    zoom: {
        x: null, y: null, a: null,  // initially chosen depending on the tree size
        delta: { in: 0.25, out: -0.2 }
    },
    select_text: false,  // if true, clicking and moving the mouse selects text

    // style
    node: {
        box: {
            opacity: 0.2,
            color: "#fff",
        },
        dot: {
            radius: 2,
            opacity: 1,
        },
    },
    outline: {
        opacity: 0.1,
        color: "#A50",
        width: 0.5,
        slanted: true,
    },
    line: {
        length: {
            color: "#000",
            width: 0.5,
        },
        children: {
            color: "#000",
            width: 0.5,
            pattern: "solid",
        },
    },
    font_sizes: {auto: true, fixed: 10, max: 15, scroller: {
        fixed: undefined, max: undefined
    }},

    // minimap
    minimap: {
        show: true,
        uptodate: false,
        width: 10,
        height: 40,
        zoom: {x: 1, y: 1},
    },

    tree_scale: {
        show: true,
        length: 100,
        width: 1.5,
        height: 10,
        color: "#000",
        fsize: 12,
    },

    control_panel: { show: false },

    smart_zoom: false,

    zoom_sensitivity: 1,

    share_view: () => share_view(),

    show_help: () => show_help(),
};

const menus = {  // will contain the menus on the top
    pane: undefined, // main pane containing different tabs
    selected: undefined,
    searches: undefined,
    collapsed: undefined,
    layouts: undefined,
    minimap: undefined, // minimap toggler
    subtree: undefined,
};

const trees = {};  // will translate names to ids (trees[tree_name] = tree_id)


async function main() {
    await init_trees();

    set_app_path();

    view.layouts = await api(`/layouts`); // init layouts

    await set_query_string_values();

    view.ultrametric = await api(`/trees/${get_tid()}/ultrametric`);

    reset_node_count();

    init_menus(Object.keys(trees));

    await reset_layouts();

    init_events();

    get_searches();
    get_selections();
    get_active_nodes();

    setTimeout(async () => {
        reset_zoom();
        reset_position();
        draw_minimap();
        show_minimap(view.minimap.show);
        await update();
    }, 100)

    const sample_trees = ["ncbi", "GTDB_bact_r95"];  // hardcoded for the moment
    view.allow_modifications = !sample_trees.includes(view.tree);
}


// Fill global var trees, which translates tree names into their database ids.
async function init_trees() {
    try {
        const trees_info = await api("/trees");

        trees_info.forEach(t => trees[t.name] = t.id);  // like trees["mytree"] = 7
    } catch {
     // Working in memory_only mode
        view.upload = undefined;
    }
}


// Return current (sub)tree id (its id number followed by its subtree id).
function get_tid() {
    if (view.tree in trees) {
        return trees[view.tree] + (view.subtree ? "," + view.subtree : "");
    }
    else {
        Swal.fire({
            html: `Cannot find tree ${escape_html(view.tree)}<br><br>
                   Opening a default tree.`,
            icon: "error",
        });

        view.tree = Object.keys(trees)[0];  // select a default tree
        on_tree_change();

        return trees[view.tree];
    }
}


// Perform an action on a tree (among the available in the API as PUT calls).
async function tree_command(command, params=undefined) {
    try {
        await api_put(`/trees/${get_tid()}/${command}`, params);

        const commands_modifying_size = ["root_at", "remove"];
        if (commands_modifying_size.includes(command))
            view.tree_size = await api(`/trees/${get_tid()}/size`);
    }
    catch (ex) {
        Swal.fire({
            title: "Command Error",
            html: `When running <tt>${command}</tt>:<br><br>${ex.message}`,
            icon: "error",
        });
    }
}


// What happens when the user selects a new tree in the menu.
async function on_tree_change() {
    if (!menus.pane)
        return;  // we haven't initialized yet!

    div_tree.style.cursor = "wait";
    remove_searches();
    remove_selections();
    remove_collapsed();
    view.tree_size = await api(`/trees/${get_tid()}/size`);
    view.min_size = await api(`/trees/${get_tid()}/collapse_size`);

    // Get searches and selections if any are stored in backend
    if (Object.keys(view.searches).length === 0)
        get_searches();
    if (Object.keys(view.selected).length === 0)
        get_selections();
    if (Object.keys(view.active.nodes).length === 0)
        get_active_nodes();

    reset_node_count();
    await reset_layouts();
    reset_zoom();
    reset_position();
    draw_minimap();
    await update();

    menus.subtree.refresh(); // show subtree in control panel

    const sample_trees = ["ncbi", "GTDB_bact_r95"];  // hardcoded for the moment
    view.allow_modifications = !sample_trees.includes(view.tree);
}


// What happens when the user selects a new drawer in the menu.
async function on_drawer_change() {
    const previous_type = view.drawer.type;

    const drawer_info = await api(`/drawers/${view.drawer.name}/${get_tid()}`);
    view.drawer.type = drawer_info.type;
    view.drawer.npanels = drawer_info.npanels;

    if (drawer_info.type !== previous_type) {
        reset_zoom();
        reset_position();
        draw_minimap();
    }

    update();
}


function reset_view() {
    reset_zoom();
    reset_position();
    if (!view.minimap.uptodate)
        draw_minimap();
    update();
}


function set_app_path() {
    const params = new URLSearchParams(location.search);

    for (const [param, value] of params)
        if (param === "path")
            view.path = value;
}

// Set values that have been given with the query string.
async function set_query_string_values() {
    const unknown_params = [];
    const params = new URLSearchParams(location.search);

    for (const [param, value] of params) {
        if (param === "tree")
            view.tree = trees[value] || value;
        else if (param === "subtree")
            view.subtree = value;
        else if (param === "x")
            view.tl.x = Number(value);
        else if (param === "y")
            view.tl.y = Number(value);
        else if (param === "w")
            view.zoom.x = div_tree.offsetWidth / Number(value);
        else if (param === "h")
            view.zoom.y = div_tree.offsetHeight / Number(value);
        else if (param === "drawer")
            view.drawer.name = value;
        else if (param === "path")
            view.path = value;
        else if (param === "controlpanel")
            view.control_panel.show = value === "1";
        else if (param === "minimap")
            view.minimap.show = value === "1";
        else if (param === "layouts") {
            const active = value.split(",");
            active.forEach(a => {
                const [ key, ly ] = a.split(":");
                const layouts = view.layouts[key];
                if (layouts) {
                    if (ly === "all")
                        for (let l in layouts)
                            layouts[l] = true;
                    else if ([...Object.keys(layouts)].includes(ly))
                        layouts[ly] = true;
                }
            })
        }
        else
            unknown_params.push(param);
    }

    if (unknown_params.length > 0) {
        const pars = unknown_params.map(t => `<tt>${escape_html(t)}</tt>`);
        Swal.fire({
            title: "Oops!",
            html: "Unknown parameters passed in url:<br><br>" + pars.join(", "),
            icon: "warning",
        });
    }

    await set_consistent_values();
}

async function set_consistent_values() {
    if (view.tree === null)
        view.tree = Object.keys(trees)[0];  // select default tree
    else if (Object.keys(trees).length === 0 && !isNaN(+view.tree)) {
        // Working in memory only mode
        const name = await api(`/trees/${view.tree}/name`);
        trees[name] = view.tree;
        view.tree = name;
    }

    view.tree_size = await api(`/trees/${get_tid()}/size`);
    view.min_size = await api(`/trees/${get_tid()}/collapse_size`);

    let drawer_info;
    try {
        drawer_info = await api(`/drawers/${view.drawer.name}/${get_tid()}`);
    }
    catch (ex) {
        Swal.fire({
            html: `Cannot find drawer ${escape_html(view.drawer.name)}<br><br>
                   Opening a default drawer.`,
            icon: "error",
        });
        view.drawer.name = "RectFaces";
        drawer_info = {"type": "rect", "npanels": 1};
    }

    view.drawer.type = drawer_info.type;  // "rect" or "circ"
    view.drawer.npanels = drawer_info.npanels;  // if > 1, there's aligned stuff

    if (drawer_info.type === "rect" && drawer_info.npanels > 1)
        div_aligned.style.display = "initial";  // show div for aligned content
    else
        div_aligned.style.display = "none";     // hide div for aligned content

    if (view.drawer.type === "circ") {  // adjust zoom nicely so zx == zy
        if (view.zoom.x !== null && view.zoom.y !== null)
            view.zoom.x = view.zoom.y = Math.min(view.zoom.x, view.zoom.y);
        else if (view.zoom.x !== null)
            view.zoom.y = view.zoom.x;
        else if (view.zoom.y !== null)
            view.zoom.x = view.zoom.y;
    }

    reset_zoom(view.zoom.x === null, view.zoom.y === null, view.zoom.a === null);
    reset_position(view.tl.x === null, view.tl.y === null);
}


function show_minimap(show) {
    const status = (show ? "visible" : "hidden");
    div_minimap.style.visibility = div_visible_rect.style.visibility = status;
    if (show) {
        if (!view.minimap.uptodate)
            draw_minimap();
        update_minimap_visible_rect();
    }
}


function reset_node_count() {
    api(`/trees/${get_tid()}/nodecount`).then(n => {
        view.tnodes = n.tnodes;
        view.tleaves = n.tleaves;
    });
}


function get_active_layouts() {
    return  Object.entries(view.layouts).reduce((all, [key, lys]) => {
        Object.entries(lys).forEach(([ly, val]) => { 
            if (val === true) 
                all.push(`${key}:${ly}`) 
        });
        return all;
    }, []);
}

async function reset_layouts() {
    view.layouts = await api(`/layouts/${get_tid()}`);
    update_folder_layouts()
}


// Set the zoom so the full tree fits comfortably on the screen.
function reset_zoom(reset_zx=true, reset_zy=true, reset_za=true) {
    if (!(reset_zx || reset_zy || reset_za))
        return;

    const size = view.tree_size;

    if (view.drawer.type === "rect") {
        if (reset_zx)
            view.zoom.x = 0.6 * div_tree.offsetWidth / size.width;
        if (reset_zy)
            view.zoom.y = 0.9 * div_tree.offsetHeight / size.height;
        if (reset_za)
            view.zoom.a = 1;
    }
    else if (view.drawer.type === "circ") {
        const min_w_h = Math.min(div_tree.offsetWidth, div_tree.offsetHeight);
        view.zoom.x = view.zoom.y = min_w_h / (view.rmin + size.width) / 2;
        view.zoom.a = view.zoom.x;
    }
}


function reset_position(reset_x=true, reset_y=true) {
    if (view.drawer.type === "rect") {
        if (reset_x)
            view.tl.x = -0.10 * div_tree.offsetWidth / view.zoom.x;
        if (reset_y)
            view.tl.y = -0.05 * div_tree.offsetHeight / view.zoom.y;
    }
    else if (view.drawer.type === "circ") {
        if (!(view.angle.min === -180 && view.angle.max === 180)) {
            view.angle.min = -180;
            view.angle.max = 180;
            view.minimap.uptodate = false;
        }
        if (reset_x)
            view.tl.x = -div_tree.offsetWidth / view.zoom.x / 2;
        if (reset_y)
            view.tl.y = -div_tree.offsetHeight / view.zoom.y / 2;
    }
}


// Return an url with the view of the given rectangle of the tree.
function get_url_view(x, y, w, h) {
    const qs = new URLSearchParams({
        x: x, y: y, w: w, h: h,
        tree: view.tree, subtree: view.subtree, drawer: view.drawer.name,
        layouts: get_active_layouts(),
    }).toString();
    return window.location.origin + window.location.pathname + "?" + qs;
}


// Show an alert with information about the current tree and view.
async function show_tree_info() {
    const info = await api(`/trees/${get_tid()}`);

    const props = info.props.map(p =>
        `<tt>${escape_html(p)}</tt>`).join("<br>");

    const w = div_tree.offsetWidth / view.zoom.x,
          h = div_tree.offsetHeight / view.zoom.y;
    const url = get_url_view(view.tl.x, view.tl.y, w, h);

    const result = await Swal.fire({
        title: "Tree Information",
        icon: "info",
        html: `<b>Name</b>: ${escape_html(info.name)}<br><br>` +
            (info.description ? `${info.description}<br><br>` : "") +
            `Node properties:<br>${props}<br><br>` +
            `(<a href="${url}">current view</a>)`,
        confirmButtonText: navigator.clipboard ? "Copy view to clipboard" : "Ok",
        showCancelButton: true,
    });

    if (result.isConfirmed && navigator.clipboard)
        navigator.clipboard.writeText(url);
}


// Open a dialog with a link to the current view of the tree.
// It is either copied to the clipboard (if possible), or shown as a link.
// The link can be opened in a different browser by someone else and they
// would see the same part of the same tree.
function share_view() {
    const w = div_tree.offsetWidth / view.zoom.x,
          h = div_tree.offsetHeight / view.zoom.y;
    const url = get_url_view(view.tl.x, view.tl.y, w, h);

    if (navigator.clipboard) {
        navigator.clipboard.writeText(url);
        Swal.fire({
            text: "Current view has been copied to the clipboard.",
            icon: "success",
        });
    }
    else {
        Swal.fire({
            html: "Right-click on link to copy to the clipboard:<br><br>" +
                  `(<a href="${url}">current tree view</a>)`,
        });
    }
}


function show_help() {
    const help_text = `
<table style="margin: 0 auto">
<thead><tr><th>General Instructions</th></tr></thead>
<tbody style="text-align: left">
<tr><td><br>
Click and drag with the left mouse button to move around the tree.
</td></tr>
<tr><td><br>
Use the mouse wheel to zoom in and out. Press <kbd>Ctrl</kbd> or <kbd>Alt</kbd>
while using the wheel to zoom differently.
</td></tr>
<tr><td><br>
Click on the minimap to go to a different area or drag the current view.
</td></tr>
<tr><td><br>
Right-click on a node to show options to interact with it.
</td></tr>
<tr><td><br>
Use the options in the menu at the top right to change the visualization.
</td></tr>
</tbody>
</table>

<br>
<br>

<table style="margin: 0 auto">
<thead><tr><th colspan="2">Keyboard Shortcuts</th></tr></thead>
<tbody>
<tr><td> </td><td>&nbsp; </td></tr>
<tr><td><kbd>F1</kbd></td><td style="text-align: left">&nbsp; help</td></tr>
<tr><td><kbd>/</kbd></td><td style="text-align: left">&nbsp; search</td></tr>
<tr><td><kbd>r</kbd></td><td style="text-align: left">&nbsp; reset view</td></tr>
<tr><td><kbd>m</kbd></td><td style="text-align: left">&nbsp; toggle minimap</td></tr>
<tr><td><kbd>p</kbd></td><td style="text-align: left">&nbsp; toggle control panel</td></tr>
<tr><td><kbd>⬅️</kbd> <kbd>➡️</kbd> <kbd>⬆️</kbd> <kbd>⬇️</kbd></td>
    <td style="text-align: left">&nbsp; move the view</td></tr>
<tr><td><kbd>+</kbd> <kbd>&ndash;</kbd></td>
    <td style="text-align: left">&nbsp; zoom in / out</td></tr>
</tbody>
</table>

<br>

<hr>

<br>

<div style="font-size: 0.8em">
<p>
<img src="icon.png" alt="ETE Toolkit logo">
Tree Explorer is part of the
<a href="http://etetoolkit.org/">ETE Toolkit</a>.
</p>

<p>
<img src="https://chanzuckerberg.com/wp-content/themes/czi/img/logo.svg"
     width="50" alt="Chan Zuckerberg Initiative logo">
Smart visualization funded by
<a href="https://chanzuckerberg.com/">CZI</a>.
</p>
</div>

<br>
<br>
`;
    Swal.fire({
        title: "Tree Explorer",
        html: help_text,
        icon: "info",
    });
}


// Return the corresponding in-tree position of the given point (on the screen).
function coordinates(point) {
    const x = view.tl.x + point.x / view.zoom.x,
          y = view.tl.y + point.y / view.zoom.y;

    if (view.drawer.type === "rect") {
        return [x, y];
    }
    else if (view.drawer.type === "circ") {
        const r = Math.sqrt(x*x + y*y);
        const a = Math.atan2(y, x) * 180 / Math.PI;
        return [r, a];
    }
}


async function on_box_click(event, box, node_id, properties) {
    if (event.altKey && node_id.length) {
        const tid = get_tid() + "," + node_id;
        const active = await api(`/trees/${tid}/active`);
        if (active.length)
            deactivate_node(node_id)
        else
            activate_node(node_id, properties)
    }
    else if (event.detail === 2 || event.ctrlKey) {
        // double-click or ctrl-click
        zoom_into_box(box);
    }
    else if (event.shiftKey) {  // shift-click
        view.subtree += (view.subtree ? "," : "") + node_id;
        on_tree_change();
    }
}


// Mouse wheel -- zoom in/out (instead of scrolling).
function on_box_wheel(event, box) {
    event.preventDefault();

    const point = {x: event.pageX, y: event.pageY};
    const zoom_in = event.deltaY < 0;
    const do_zoom = {x: !event.ctrlKey, y: !event.altKey};

    if (view.drawer.type === "rect" && view.smart_zoom)
        zoom_towards_box(box, point, zoom_in, do_zoom);
    else
        zoom_around(point, zoom_in, do_zoom);
}


function on_box_mouseenter(node_id, properties) {
    notify_parent("hover", { 
        eventType: "mouseenter",
        node: { id: String(node_id), ...properties } })
}


function on_box_mouseleave(node_id, properties) {
    notify_parent("hover", { 
        eventType: "mouseleave",
        node: { id: String(node_id), ...properties } })
}


async function sort(node_id=[]) {
    if (view.allow_modifications) {
        await tree_command("sort",
                           [node_id, view.sorting.key, view.sorting.reverse]);
        draw_minimap();
        update();
    }
    else {
        Swal.fire({
            html: "Sorry, sorting is disabled for this tree. But you can try " +
                  "it on your own uploaded trees!",
            icon: "info",
        });
    }
}
