// Functions related to selecting nodes.

import { view, menus } from "./gui.js";

export { select_node };


// Select node with the given name and return true if things went well.
function select_node(node_id, name) {

    parent.postMessage({ selected: [node_id] }, "*");

    if (name in view.selected) {
        view.selected[name].nodes.push(node_id);
        colorize_selection(name);
        return true;
    }

    const folder = menus.selected.addFolder({ title: name, expanded: false });
    const colors = ["#FF0", "#F0F", "#0FF", "#F00", "#0F0", "#00F"].reverse();
    const nselected = Object.keys(view.selected).length;
    view.selected[name] = {
        nodes: [node_id],
        opacity: 0.4,
        color: colors[nselected % colors.length],
    };

    view.selected[name].remove = function() {
        view.selected[name].opacity = view.node.box.opacity;
        view.selected[name].color = view.node.box.color;
        colorize_selection(name);
        parent.postMessage({ unselected: view.selected[name].nodes }, "*");
        delete view.selected[name];
        folder.dispose();
    }

    folder.addInput(view.selected[name], "opacity", { min: 0, max: 1, step: 0.1 })
        .on("change", () => colorize_selection(name));
    folder.addInput(view.selected[name], "color", { view: "color" })
        .on("change", () => colorize_selection(name));

    folder.addButton({ title: "remove" }).on("click", view.selected[name].remove);

    colorize_selection(name);

    return true;

}

function colorize_selection(name) {
    const selection = view.selected[name];
    selection.nodes.forEach(node_id => {
        const node = document.getElementById("node-" + node_id.join("_"));
        if (node) {
            node.style.opacity = selection.opacity;
            node.style.fill = selection.color;
        }
    });
}
