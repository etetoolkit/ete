// Functions related to manually collapsed nodes.

import { view, menus } from "./gui.js";
import { draw_tree } from "./draw.js";

export { collapse_node, remove_collapsed };


// Mark node as collapsed and show it in the corresponding menu.
function collapse_node(name, node_id) {
    const id = node_id.toString();  // [1,0,1] -> "1,0,1"

    view.collapsed_ids[id] = {};

    const fname = `${get_next_number()} - ` +
        (name ? name.slice(0, 20) : "(unnamed)");

    const folder = menus.collapsed.addFolder({ title: fname });

    const collapsed_node = view.collapsed_ids[id];

    collapsed_node.remove = function() {
        delete view.collapsed_ids[id];
        folder.dispose();
        draw_tree();
    }

    folder.addButton({ title: "remove" }).on("click", collapsed_node.remove)

    draw_tree();
}

function get_next_number() {
    const names = menus.collapsed.children.map(c => c.title);
    const numbers = names.map(x => Number(x.split(" - ", 1)[0]));
    return Math.max(0, ...numbers) + 1;
}


// Empty view.collapsed_ids.
function remove_collapsed() {
    const ids = Object.keys(view.collapsed_ids);
    ids.forEach(id => view.collapsed_ids[id].remove());
}
