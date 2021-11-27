// Functions related to selecting nodes.

import { view, get_tid } from "./gui.js";
import { draw_tree } from "./draw.js";
import { api } from "./api.js";
import { notify_parent } from "./events.js";
import { store_selection } from "./select.js";

export { 
    activate_node, deactivate_node,
    update_active_nodes,
    get_active_class, colorize_active,
    add_folder_active, get_active_nodes
};

const selectError = Swal.mixin({
    position: "bottom-start",
    showConfirmButton: false,
    icon: "error",
    timer: 3000,
    timerProgressBar: true,
    didOpen: el => {
        el.addEventListener('mouseenter', Swal.stopTimer)
        el.addEventListener('mouseleave', Swal.resumeTimer)
    }
});


function notify_active() {
    notify_parent("active", { nodes: view.active.nodes });
}

async function activate_node(node_id, properties, notify=true) {
    const tid = get_tid() + "," + node_id;

    // Remove active node
    await api(`/trees/${tid}/activate`)

    view.active.nodes.push({ id: String(node_id), ...properties });

    update_active_folder();

    if (notify)
        notify_active();

    draw_tree();
}

async function deactivate_node(node_id, notify=true) {
    const tid = get_tid() + "," + node_id;

    // Remove active node
    await api(`/trees/${tid}/deactivate`)

    view.active.nodes = view.active.nodes
        .filter(n => n.id !== String(node_id));

    update_active_folder();

    if (notify)
        notify_active();

    draw_tree();
}


// Notify parent window if encapsulated in iframe
async function store_active(name) {
    try {
        if (!name)
            return false;  // prevent popup from closing

        const qs = `text=${encodeURIComponent(name)}`;
        const res = await api(`/trees/${get_tid()}/store_active?${qs}`);

        if (res.message !== "ok")
            throw new Error("Something went wrong.");

        store_selection(name, res);

        notify_active();

        view.active.remove(false);

    } catch (exception) {
        selectError.fire({ html: exception });
    }
}


function add_folder_active() {

    const folder = view.active.folder;
    folder.addInput(view.active, "color", { view: "color" })
        .on("change", colorize_active);

    view.active.remove = async function(purge=true, redraw=true) {
        if (purge)
            await api(`/trees/${get_tid()}/remove_active`);

        view.active.nodes = [];

        notify_active();

        update_active_folder();

        if (redraw)
            draw_tree();
    }

    view.active.buttons.push(folder.addButton({ 
        title: "save selection",
        disabled: true })
        .on("click", () => {
            Swal.fire({
                input: "text",
                text: "Enter name to describe selection",
                preConfirm: name => store_active(name)
            });
        }));
    view.active.buttons.push(folder
        .addButton({ title: "remove", disabled: true })
        .on("click", view.active.remove));
}


function update_active_folder() {
    // Update value in control panel
    view.active.folder.title = `Active (${view.active.nodes.length})`;
    const disable = view.active.nodes.length === 0
    view.active.buttons.forEach(b => b.disabled = disable);
}


// Return a class name related to the results of selecting nodes.
function get_active_class(type="results") {
    return "selected_" + type + "_active";
}


function colorize_active() {
    const cresults = get_active_class("results");
    Array.from(div_tree.getElementsByClassName(cresults)).forEach(e => {
        e.style.opacity = view.active.opacity;
        e.style.fill = view.active.color;
    });
}


async function get_active_nodes() {
    view.active.nodes = await api(`/trees/${get_tid()}/all_active`);
    notify_active();
    if (view.active.folder)
        update_active_folder();
}


function update_active_nodes(nodes) {
    const active_ids = view.active.nodes.map(n => n.id);
    const new_ids = nodes.map(n => String(n.id));

    nodes.forEach(node => {
        if (!active_ids.includes(String(node.id)))
            activate_node(node.id, node, false)
    })

    active_ids.forEach(id => {
        if (!new_ids.includes(id))
            deactivate_node(id, false)
    })

    if (view.active.folder)
        update_active_folder();
}
