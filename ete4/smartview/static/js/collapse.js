// Functions related to manually collapsed nodes.

import { view, menus } from "./gui.js";
import { draw_tree } from "./draw.js";

export { collapse_node, remove_collapsed };


// Mark node as collapsed and show it in the corresponding menu.
function collapse_node(name, node_id) {
    const folder_name = `${get_next_number()} - ` +
        (name ? name.slice(0, 20) : "(unnamed)");  // looks like "1 - Bacteria"

    const folder = menus.collapsed.addFolder(
        {title: folder_name, expanded: false});

    const id = node_id.toString();  // [1,0,1] -> "1,0,1"

    // Create object in view.collapsed_ids with a function that knows
    // how to remove it.
    view.collapsed_ids[id] = {
        remove: function() {
            delete view.collapsed_ids[id];
            folder.dispose();
            draw_tree();
        }
    }

    folder.addButton({title: "remove"})
        .on("click", view.collapsed_ids[id].remove);

    draw_tree();
}

// All entries in the menu for collapsed nodes are named like:
//   <number> - blahblah
// This returns a number higher than all, so we can have unique full names.
function get_next_number() {
    const names = menus.collapsed.children.map(x => x.title);
    const numbers = names.map(x => Number(x.split(" - ", 1)[0]));
    return Math.max(0, ...numbers) + 1;
}


// Empty view.collapsed_ids.
function remove_collapsed() {
    const ids = Object.keys(view.collapsed_ids);
    ids.forEach(id => view.collapsed_ids[id].remove());
}
