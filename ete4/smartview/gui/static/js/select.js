// Functions related to selecting nodes.

import { view, menus } from "./gui.js";

export { select_node };


// Select node with the given name and return true if things went well.
function select_node(node_id, name) {

    parent.postMessage({ selected: [node_id] }, "*");

    if (name in view.selection) {
        view.selection[name].nodes.push(node_id);
        colorize_selection(name);
        return true;
    }

    const folder = menus.selection.addFolder({ title: name, expanded: false });
    const colors = ["#FF0", "#F0F", "#0FF", "#F00", "#0F0", "#00F"].reverse();
    const nselected = Object.keys(view.selection).length;
    view.selection[name] = {
        nodes: [node_id],
        opacity: 0.4,
        color: colors[nselected % colors.length],
    };

    view.selection[name].remove = function() {
        view.selection[name].opacity = view.node.box.opacity;
        view.selection[name].color = view.node.box.color;
        colorize_selection(name);
        parent.postMessage({ unselected: view.selection[name].nodes }, "*");
        delete view.selection[name];
        folder.dispose();
    }

    folder.addInput(view.selection[name], "opacity", { min: 0, max: 1, step: 0.1 })
        .on("change", () => colorize_selection(name));
    folder.addInput(view.selection[name], "color", { view: "color" })
        .on("change", () => colorize_selection(name));

    folder.addButton({ title: "remove" }).on("click", view.selection[name].remove);

    colorize_selection(name);

    return true;

}

function colorize_selection(name) {
    const selection = view.selection[name];
    selection.nodes.forEach(node_id => {
        const node = document.getElementById("node-" + node_id.join("_"));
        if (node) {
            node.style.opacity = selection.opacity;
            node.style.fill = selection.color;
        }
    });
}
