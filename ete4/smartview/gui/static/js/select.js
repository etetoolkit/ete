// Functions related to selecting nodes.

import { view, menus, get_tid, on_tree_change } from "./gui.js";
import { draw_tree } from "./draw.js";
import { api } from "./api.js";
import { colors } from "./colors.js";
import { notify_parent } from "./events.js";

export { 
    select_node, unselect_node, store_selection,
    get_selections, remove_selections, 
    get_selection_class, colorize_selections,
    select_by_command, prune_by_selection };

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


// Select node with the given name and return true if things went well.
async function select_node(node_id, name) {
    try {
        if (!name)
            return false;  // prevent popup from closing

        const tid = get_tid() + "," + node_id;
        const qs = `text=${encodeURIComponent(name)}`;
        const res = await api(`/trees/${tid}/select?${qs}`);

        if (res.message !== "ok")
            throw new Error("Something went wrong.");

        store_selection(name, res);

        draw_tree();

    } catch (exception) {
        selectError.fire({ html: exception });
    }

    return true;
}


function notify_selection(modification, name) {
    if (view.selected[name])
        notify_parent("saved", {
            eventType: modification,
            name: name,
            color: view.selected[name].results.color,
        })
}


async function unselect_node(node_id) {
    const tid = get_tid() + "," + node_id;

    const old_selections = await api(`/trees/${tid}/selections`); // just names for specific node
    await api(`/trees/${tid}/unselect`);
    const selections = await api(`/trees/${tid}/all_selections`);  // names and nresults/nparents for whole tree
    const selection_names = [...Object.keys(selections.selected)];

    old_selections.selections.forEach(name => {
        if (!selection_names.includes(name)) {
            view.selected[name].remove();
        } else {
            update_selected_folder(name, selections.selected[name]);
            notify_selection("modify", name);
        }
    });
    draw_tree();
}


// Store selection with info from backend (number of results and parents)
// Notify parent window if encapsulated in iframe
//const colors = ["#FF0", "#F0F", "#0FF", "#F00", "#0F0", "#00F"].reverse();
function store_selection(name, res) {

    // Add to selected dict
    const nselected = Object.keys(view.selected).length;
    const selected = view.selected[name];
    if (selected) {
        update_selected_folder(name, res)
        notify_selection("modify", name);
    }
    else {
        view.selected[name] = {
            results: { n: res.nresults,
                      opacity: 0.4,
                      color: colors[nselected % colors.length] },
            parents: { n: res.nparents,
                       color: "#000",
                       width: 2.5 },};
        add_selected_to_menu(name);
        notify_selection("select", name);
    }

}


function update_selected_folder(name, res) {
    const selected = view.selected[name];
    // Update number of results and parents
    selected.results.n = res.nresults;
    selected.parents.n = res.nparents;
    // Update value in control panel
    selected.results.folder.title = `results (${res.nresults})`;
    selected.parents.folder.title = `parents (${res.nparents})`;
}


function change_name(name, folder) {
    Swal.fire({
        input: "text",
        text: "Enter name to describe selection",
        inputValue: name,
        showConfirmButton: false,
        preConfirm: async new_name => {
            if (name === new_name || !new_name)
                return false

            if (Object.keys(view.selected).includes(new_name))
                selectError.fire({ 
                    html: "Selection name already exists<br>Please choose a different name"
                }).then(() => change_name(name, folder));
            else {
                view.selected[new_name] = {...view.selected[name]};
                folder.title = new_name;
                delete view.selected[name];
                const qs = `name=${encodeURIComponent(name)}&newname=${encodeURIComponent(new_name)}`;
                await api(`/trees/${get_tid()}/change_selection_name?${qs}`)
                draw_tree();
            }
        },
    })
    
}


function add_selected_to_menu(name) {
    const selected = view.selected[name];

    const folder = menus.selected.addFolder({ title: name });

    folder.addInput(selected.results, "color", { view: "color" })
        .on("change", () => colorize_selection(name));


    selected.remove = async function(purge=true) {
        if (purge) {
            const qs = `text=${encodeURIComponent(folder.title)}`;
            await api(`/trees/${get_tid()}/remove_selection?${qs}`);
        }

        notify_selection("remove", folder.title);

        delete view.selected[folder.title];
        folder.dispose();
        draw_tree();
    }


    const folder_more = folder.addFolder({ title: "more", expanded: false });

    folder_more.addButton({ title: "edit name" }).on("click", () => change_name(folder.title, folder));

    const folder_results = folder_more.addFolder({ title: `results (${selected.results.n})` });
    folder_results.addInput(selected.results, "opacity", 
        { min: 0, max: 1, step: 0.1 })
        .on("change", () => colorize_selection(name));
    // Store to change title when selection is edited
    selected.results.folder = folder_results;

    const folder_parents = folder_more.addFolder({ title: `parents (${selected.parents.n})` });
    folder_parents.addInput(selected.parents, "color", { view: "color" })
        .on("change", () => colorize_selection(name));
    folder_parents.addInput(selected.parents, "width", { min: 0.1, max: 10 })
        .on("change", () => colorize_selection(name));
    // Store to change title when selection is edited
    selected.parents.folder = folder_parents;

    folder_more.addButton({ title: "remove" }).on("click", selected.remove);

}


// Return a class name related to the results of selecting nodes.
function get_selection_class(text, type="results") {
    return "selected_" + type + "_" + String(text).replace(/[^A-Za-z0-9_-]/g, '');
}


function colorize_selection(name, notify=true) {
    const selected = view.selected[name];

    if (notify)
        notify_selection("colorChange", folder.title);

    const cresults = get_selection_class(name, "results");
    Array.from(div_tree.getElementsByClassName(cresults)).forEach(e => {
        e.style.opacity = selected.results.opacity;
        e.style.fill = selected.results.color;
    });

    const cparents = get_selection_class(name, "parents");
    Array.from(div_tree.getElementsByClassName(cparents)).forEach(e => {
        e.style.stroke = selected.parents.color;
        e.style.strokeWidth = selected.parents.width;
    });
}


function colorize_selections() {
    Object.keys(view.selected).forEach(s => colorize_selection(s, false));
}


// Get selections from api and fill view.selections
async function get_selections() {
    const selected = await api(`/trees/${get_tid()}/all_selections`);
    Object.entries(selected.selected)
        .forEach(([name, res]) => store_selection(name, res));
}


function remove_selections(purge=false) {
    Object.keys(view.selected).forEach(s => view.selected[s].remove(purge));
}


async function select_by_command(select_command, name) {
    // First search with selectCommand then store as selection

    // Perform search given a select_command
    let qs = `text=${encodeURIComponent(select_command)}`;
    const res = await api(`/trees/${get_tid()}/search?${qs}`);

    if (res.message !== 'ok' || res.nresults === 0)
        throw new Error(`No results found by: ${select_command}`);

    // Conver search to selection if successful
    await api(`/trees/${get_tid()}/search_to_selection?${qs}`);

    if (name) {
        // Change selection name in backend
        qs = `name=${encodeURIComponent(select_command)}&newname=${encodeURIComponent(name)}`;
        await api(`/trees/${get_tid()}/change_selection_name?${qs}`);
    } else
        name = select_command;

    store_selection(name, { nresults: res.nresults, nparents: res.nparents });

    draw_tree();
}


async function prune_by_selection(names) {
    const qs = `names=${encodeURIComponent(names)}`;
    const res = await api(`/trees/${get_tid()}/prune_by_selection?${qs}`);

    if (res.message === 'ok')
        on_tree_change()
}
