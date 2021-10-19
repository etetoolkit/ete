// Functions related to selecting nodes.

import { view, menus } from "./gui.js";

export { select_node }


// Select node with the given name and return true if things went well.
function select_node(node_id) {
    parent.postMessage({ selected: node_id }, "*");
}

function unselect_node(node_id) {
    parent.postMessage({ unselected: node_id }, "*");
}
