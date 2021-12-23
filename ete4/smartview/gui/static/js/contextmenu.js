// Functions related to the context menu (right-click menu).

import { view, tree_command, on_tree_change, reset_view, sort, get_tid }
    from "./gui.js";
import { draw_minimap } from "./minimap.js";
import { update } from "./draw.js";
import { download_newick } from "./download.js";
import { zoom_into_box } from "./zoom.js";
import { collapse_node } from "./collapse.js";
import { activate_node, deactivate_node } from "./active.js";
import { api } from "./api.js";

export { on_box_contextmenu };


async function on_box_contextmenu(event, box, name, properties, node_id=[]) {

    event.preventDefault();

    div_contextmenu.innerHTML = "";

    if (box) {
        const name_text = ": " + (name.length < 20 ? name :
                                  (name.slice(0, 8) + "..." + name.slice(-8)));

        add_label("Node" + (name.length > 0 ? name_text : ""));

        add_button("Zoom into branch", () => zoom_into_box(box),  "", "search");

        if (node_id.length > 0) {
            await add_node_options(box, name, properties, node_id);
        }

    }

    add_label("Tree");

    add_tree_options();

    const x_max = div_tree.offsetWidth - div_contextmenu.offsetWidth,
          y_max = div_tree.offsetHeight - div_contextmenu.offsetHeight;
    div_contextmenu.style.left = Math.min(event.pageX, x_max) + "px";
    div_contextmenu.style.top = Math.min(event.pageY, y_max) + "px";
    div_contextmenu.style.visibility = "visible";
}


async function add_node_options(box, name, properties, node_id) {
    add_button("Go to subtree at branch", () => {
        view.subtree += (view.subtree ? "," : "") + node_id;
        on_tree_change();
    }, "Explore the subtree starting at the current node.",
       "map-marker-alt", false);
    add_button("Show node info", () => {
        let text = "<div style='text-align: left'>";
        Object.entries(properties)
            .forEach(([k, v]) => {
                if (k && v)
                    text += `${k}: ${v}<br>`;
            });
        text += "</div>";
        Swal.fire({ 
            html: `${text}`, 
            showConfirmButton: false });
    }, "", "fingerprint", false);
    add_button("Download branch as newick", () => download_newick(node_id),
               "Download subtree starting at this node as a newick file.",
               "download", false);
    if ("taxid" in properties) {
        const taxid = properties["taxid"];
        add_button("Show in taxonomy browser", () => {
            const urlbase = "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser";
            window.open(`${urlbase}/wwwtax.cgi?id=${taxid}`);
        }, `Open the NCBI Taxonomy Browser on this taxonomy ID: ${taxid}.`,
           "book", false);
    }

    const collapsed_node = view.collapsed_ids[node_id];
    if (collapsed_node)
        add_button("Uncollapse branch", () => collapsed_node.remove(),
                   "Show nodes below the current one.",
                   "expand", false);
    else
        add_button("Collapse branch", () => collapse_node(node_id),
                   "Do not show nodes below the current one.",
                   "compress", false);

    const tid = get_tid() + "," + node_id;
    const active = await api(`/trees/${tid}/active`);
    if (active.length)
        add_button("Unselect node", () => deactivate_node(node_id),
                   "Remove current node from active selection.",
                   "trash-alt", false);
    else
        add_button("Select node", () => activate_node(node_id, properties),
                   "Add current node from active selection.",
                   "hand-pointer", false);

    if ("hyperlink" in properties) {
        const [ label, url ] = properties["hyperlink"];
        add_button("Go to " + label, () => window.open(url), 
            url, "external-link-alt");
    }

    if (view.allow_modifications)
        add_node_modifying_options(box, name, properties, node_id);
}


function add_node_modifying_options(box, name, properties, node_id) {
    add_button("Rename node", async () => {
        const result = await Swal.fire({
            input: "text",
            inputPlaceholder: "Enter new name",
            preConfirm: async name => {
                return await tree_command("rename", [node_id, name]);
            },
        });
        if (result.isConfirmed)
            update();
    }, "Change the name of this node. Changes the tree structure.",
       "edit", true);
    if (!view.subtree) {
        add_button("Root on this node", async () => {
            await tree_command("root_at", node_id);
            draw_minimap();
            update();
        }, "Set this node as the root of the tree. Changes the tree structure.",
           "anchor", true);
    }
    add_button("Move branch up", async () => {
        await tree_command("move", [node_id, -1]);
        draw_minimap();
        update();
    }, "Move the current branch one step above its current position. " +
        "Changes the tree structure.",
        "arrow-up", true);
    add_button("Move branch down", async () => {
        await tree_command("move", [node_id, +1]);
        draw_minimap();
        update();
    }, "Move the current branch one step below its current position. " +
        "Changes the tree structure.",
        "arrow-down", true);
    add_button("Sort branch", () => sort(node_id),
        "Sort branches below this node according to the current sorting " +
        "function. Changes the tree structure.",
        "sort-amount-down-alt", false);
    add_button("Remove branch", async () => {
        await tree_command("remove", node_id);
        draw_minimap();
        update();
    }, "Prune this branch from the tree. Changes the tree structure.",
        "trash-alt", true);
}


function add_tree_options() {
    add_button("Reset view", reset_view,
               "Fit tree to the window.", "power-off");
    if (view.subtree) {
        add_button("Go back to main tree", () => {
            view.subtree = "";
            on_tree_change();
        }, "Exit view on current subtree.",
           "backward", false);
    }

    if (view.allow_modifications) {
        add_button("Sort tree", () => sort(),
            "Sort all branches according to the current sorting function. " +
            "Changes the tree structure.", 
            "sort-amount-down-alt", true);
        if (!view.subtree) {
            add_button("Reload tree", async () => {
                await tree_command("reload", get_tid());
                on_tree_change();
            }, "Reload current tree. Restores the original tree structure.",
                "sync-alt", true);
        }
    }
}

function create_icon(name) {
    const i = document.createElement("i");
    i.classList.add("fas", `fa-${name}`);
    return i;
}

function add_button(text, fn, tooltip, icon_before, icon_warning=false) {
    const button = document.createElement("button");
    if (icon_before)
        button.appendChild(create_icon(icon_before));
    button.appendChild(document.createTextNode(text));
    if (icon_warning) 
        button.appendChild(create_icon("exclamation-circle"))
    button.addEventListener("click", event => {
        div_contextmenu.style.visibility = "hidden";
        fn(event);
    });
    button.classList.add("ctx_button");

    if (tooltip)
        button.setAttribute("title", tooltip);

    div_contextmenu.appendChild(button);
    add_element("br");
}


function add_label(text) {
    const p = document.createElement("p");
    p.appendChild(document.createTextNode(text));
    p.classList.add("ctx_label");

    div_contextmenu.appendChild(p);
}


function add_element(name) {
    div_contextmenu.appendChild(document.createElement(name));
}
