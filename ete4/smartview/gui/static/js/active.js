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


function notify_active(type) {
    notify_parent("active", { activeType: type });
}

async function activate_node(node_id, properties, type, notify=true) {
    const tid = get_tid() + "," + node_id;

    // Remove active node
    await api(`/trees/${tid}/activate_${type.slice(0, -1)}`)

    if (type === "clades") {
        const active = await api(`/trees/${tid}/all_active`)
        view.active[type].nodes = active.clades;
    } else
        view.active[type].nodes.push({ id: String(node_id), ...properties });

    update_active_folder(type);

    if (notify)
        notify_active(type);

    draw_tree();
}

async function deactivate_node(node_id, type, notify=true) {
    const tid = get_tid() + "," + node_id;

    // Remove active node
    await api(`/trees/${tid}/deactivate_${type.slice(0, -1)}`)


    if (type === "clades") {
        const active = await api(`/trees/${tid}/all_active`)
        view.active[type].nodes = active.clades;
    } else
        view.active[type].nodes = view.active[type].nodes
            .filter(n => n.id !== String(node_id));

    update_active_folder(type);

    if (notify)
        notify_active(type);

    draw_tree();
}


// Notify parent window if encapsulated in iframe
async function store_active(name, type) {
    try {
        if (!name)
            return false;  // prevent popup from closing

        const qs = `text=${encodeURIComponent(name)}`;
        const res = await api(`/trees/${get_tid()}/store_active_${type}?${qs}`);

        if (res.message !== "ok")
            throw new Error("Something went wrong.");

        store_selection(name, res);

        notify_active(type);

        view.active[type].remove(false);

    } catch (exception) {
        selectError.fire({ html: exception });
    }
}


function add_folder_active(type) {

    const folder = view.active[type].folder;
    folder.addInput(view.active[type], "color", { view: "color" })
        .on("change", () => colorize_active(type));

    view.active[type].remove = async function(purge=true, redraw=true, notify=true) {
        if (purge)
            await api(`/trees/${get_tid()}/remove_active_${type}`);

        view.active[type].nodes = [];

        if (notify)
            notify_active(type);

        update_active_folder(type);

        if (redraw)
            draw_tree();
    }

    view.active[type].buttons.push(folder.addButton({ 
        title: "save selection",
        disabled: true })
        .on("click", () => {
            Swal.fire({
                input: "text",
                text: "Enter name to describe selection",
                preConfirm: name => store_active(name, type)
            });
        }));
    view.active[type].buttons.push(folder
        .addButton({ title: "remove", disabled: true })
        .on("click", view.active[type].remove));
}


function update_active_folder(type) {
    // Update value in control panel
    view.active[type].folder.title = `Active ${type} (${view.active[type].nodes.length})`;
    const disable = view.active[type].nodes.length === 0
    view.active[type].buttons.forEach(b => b.disabled = disable);
}


// Return a class name related to the results of selecting nodes.
function get_active_class(active_type, type="results") {
    return "selected_" + type + "_active_" + active_type;
}


function colorize_active(type) {
    const cresults = get_active_class(type, "results");
    Array.from(div_tree.getElementsByClassName(cresults)).forEach(e => {
        if ([...e.classList].includes("nodedot"))
            e.style.opacity = 1;
        else
            e.style.opacity = view.active[type].opacity;
        e.style.fill = view.active[type].color;
    });
}


async function get_active_nodes() {
    const all_active = await api(`/trees/${get_tid()}/all_active`);
    view.active.nodes.nodes = all_active.nodes;
    view.active.clades.nodes = all_active.clades;
    notify_active("nodes");
    notify_active("clades");
    if (view.active.nodes.folder)
        update_active_folder("nodes");
    if (view.active.clades.folder)
        update_active_folder("clades");
}


function update_active_nodes(nodes, type) {
    async function activate(node) {
        const node_id = String(node.id);
        if (type === "nodes")
            return !active_ids.includes(node_id);
        else {
            const nid = tid + "," + node_id;
            const active = await api(`/trees/${nid}/active`);
            return active !== "active_clade";
        }
    }
    async function deactivate(id) {
        if (type === "nodes")
            return !new_ids.includes(id);
        else {
            const nid = tid + "," + id;
            const active = await api(`/trees/${nid}/active`);
            return active === "active_clade";
        }
    }

    if (nodes.length === 0) {
        view.active[type].remove(true, true, false)
        return
    }

    const active_ids = view.active[type].nodes.map(n => n.id);
    const new_ids = nodes.map(n => String(n.id));
    const tid = get_tid();

    nodes.forEach(node => {
        if (activate(node))
            activate_node(node.id, node, type, false)
    })

    active_ids.forEach(id => {
        if (deactivate(id))
            deactivate_node(id, type, false)
    })

    if (view.active[type].folder)
        update_active_folder(type);
}
