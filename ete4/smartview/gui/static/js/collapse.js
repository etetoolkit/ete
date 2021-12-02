// Functions related to manually collapsed nodes.

import { view } from "./gui.js";
import { draw_tree } from "./draw.js";

export { collapse_node, remove_collapsed };


// Mark node as collapsed and show it in the corresponding menu.
function collapse_node(node_id) {
    const id = node_id.toString();  // [1,0,1] -> "1,0,1"

    view.collapsed_ids[id] = {};

    const collapsed_node = view.collapsed_ids[id];

    collapsed_node.remove = function() {
        delete view.collapsed_ids[id];
        draw_tree();
    }

    draw_tree();
}


// Empty view.collapsed_ids.
function remove_collapsed() {
    const ids = Object.keys(view.collapsed_ids);
    ids.forEach(id => view.collapsed_ids[id].remove());
}
