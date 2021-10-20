// Functions related to selecting nodes.

import { view, menus, get_tid } from "./gui.js";
import { draw_tree } from "./draw.js";
import { api } from "./api.js";

export { select_node, colorize_selections, get_selection_class, remove_selections };


// Select node with the given name and return true if things went well.
async function select_node(node_id, name) {
    const tid = get_tid() + "," + node_id;
    const res = await api(`/trees/${tid}/select`);

    if (res.message !== "ok")
        throw new Error("Something went wrong.");

    if (self !== top)  // notify parent window
        parent.postMessage({ 
            selected: true,
            node: node_id,
            name: name,
            // Maybe also provide the color used to tag it...
        }, "*");

    // Add to selected dict
    const colors = ["#FF0", "#F0F", "#0FF", "#F00", "#0F0", "#00F"].reverse();
    const nselected = Object.keys(view.selected).length;
    view.selected[node_id] = {
        result: { name: name,
                  opacity: 0.4,
                  color: colors[nselected % colors.length] },
        parents: { n: res.nparents,
                   color: "#000",
                   width: 2.5 },
    };

    add_selected_to_menu(node_id);

    draw_tree();
    
    //try {

    //}
    //catch (exception) {
        //Swal.fire({
            //position: "bottom-start",
            //showConfirmButton: false,
            //html: exception,
            //icon: "error",
        //});
    //}

    return true;

}


function add_selected_to_menu(node_id) {
    const selected = view.selected[node_id];
    console.log(selected)
    const name = selected.result.name;

    const folder = menus.selected.addFolder({
        title: name,
        expanded: false 
    });

    selected.remove = function() {
        if (self !== top)  // notify parent window
            parent.postMessage({
                selected: false,
                node: node_id,
                name: name,
            }, "*");
        delete view.selected[name];
        folder.dispose();
        draw_tree();
    }

    const folder_selected = folder.addFolder({ title: "selected node" });
    folder_selected.addInput(selected.result, "opacity", 
        { min: 0, max: 1, step: 0.1 })
        .on("change", () => colorize_selection(node_id));
    folder_selected.addInput(selected.result, "color", { view: "color" })
        .on("change", () => colorize_selection(node_id));

    const folder_parents = folder.addFolder({ title: `parents (${selected.parents.n})` });
    folder_parents.addInput(selected.parents, "color", { view: "color" })
        .on("change", () => colorize_selection(node_id));
    folder_parents.addInput(selected.parents, "width", { min: 0.1, max: 10 })
        .on("change", () => colorize_selection(node_id));

    folder.addButton({ title: "remove" }).on("click", selected.remove);
}


// Return a class name related to the results of selecting nodes.
function get_selection_class(text, type="result") {
    return "selected_" + type + "_" + String(text).replace(/[^A-Za-z0-9_-]/g, '');
}


function colorize_selection(node_id) {
    const selected = view.selected[node_id];

    const cresult = get_selection_class(node_id, "result");
    // There should be just one result (avoid error when not in viewport)
    Array.from(div_tree.getElementsByClassName(cresult)).forEach(e => {
        e.style.opacity = selected.result.opacity;
        e.style.fill = selected.result.color;
    });

    const cparents = get_selection_class(node_id, "parents");
    Array.from(div_tree.getElementsByClassName(cparents)).forEach(e => {
        e.style.stroke = selected.parents.color;
        e.style.strokeWidth = selected.parents.width;
    });
}


function colorize_selections() {
    Object.keys(view.selected).forEach(s => colorize_selection(s));
}


function remove_selections() {
    Object.keys(view.selected).forEach(s => view.selected[s].remove());
}
