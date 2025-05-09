// Functions related to the context menu (right-click menu).

import { view, tree_command, on_tree_change, reset_view, sort, get_tid }
    from "./gui.js";
import { draw_minimap } from "./minimap.js";
import { update } from "./draw.js";
import { download_newick } from "./download.js";
import { zoom_into_box } from "./zoom.js";
import { tag_node } from "./tag.js";
import { collapse_node } from "./collapse.js";

export { on_box_contextmenu };


function on_box_contextmenu(event, box, name, props, node_id=[]) {
    event.preventDefault();

    div_contextmenu.innerHTML = "";

    if (box) {
        add_label("Node" + (name ? ": " + repr_short(name) : ""));

        add_button("🔍 Zoom into branch", () => zoom_into_box(box));

        add_node_options(box, name, props, node_id);

        add_element("hr");
    }

    add_label("Tree");

    add_tree_options();

    const x_max = div_tree.offsetWidth - div_contextmenu.offsetWidth,
          y_max = div_tree.offsetHeight - div_contextmenu.offsetHeight;
    div_contextmenu.style.left = Math.min(event.pageX, x_max) + "px";
    div_contextmenu.style.top = Math.min(event.pageY, y_max) + "px";
    div_contextmenu.style.visibility = "visible";
}


function repr_short(txt, max_len=30) {
    if (txt.length < max_len)
        return txt;
    else
        return txt.slice(0, max_len-10) + " ... " + txt.slice(-5);
}


function add_node_options(box, name, props, node_id) {
    add_button("📌 Go to subtree at branch", () => {
        view.subtree += (view.subtree ? "," : "") + node_id;
        on_tree_change();
    }, "Explore the subtree starting at the current node.");
    add_button("❓ Show node id", () => {
        Swal.fire({input: "text",
                   text: "node id",
                   inputValue: `${node_id}`,
                   inputAttributes: {disabled: true},
                   position: "bottom",
                   showConfirmButton: false});
    });
    add_button("📥 Download branch as newick", () => download_newick(node_id),
               "Download subtree starting at this node as a newick file.");
    if ("taxid" in props) {
        const taxid = props["taxid"];
        add_button("📖 Show in taxonomy browser", () => {
            const urlbase = "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser";
            window.open(`${urlbase}/wwwtax.cgi?id=${taxid}`);
        }, `Open the NCBI Taxonomy Browser on this taxonomy ID: ${taxid}.`);
    }
    add_button("🏷️ Tag branch", () => {
        Swal.fire({
            input: "text",
            inputPlaceholder: "Enter tag",
            preConfirm: name => tag_node(node_id, name),
        });
    });

    if (view.collapsed_ids[node_id]) {
        add_button("🪗️ Uncollapse branch",
                   () => view.collapsed_ids[node_id].remove(),
                   "Show nodes below the current one.");
    }
    else {
        add_button("🗞️ Collapse branch", () => collapse_node(name, node_id),
                   "Do not show nodes below the current one.");
    }

    if (view.allow_modifications)
        add_node_modifying_options(box, name, props, node_id);
}


function add_node_modifying_options(box, name, props, node_id) {
    add_button("🖊️ Rename node  ⚠️", async () => {
        const result = await Swal.fire({
            input: "text",
            inputPlaceholder: "Enter new name",
            preConfirm: async name => {
                return await tree_command("rename", [node_id, name]);
            },
        });
        if (result.isConfirmed)
            update();
    }, "Change the name of this node. Changes the tree structure.");
    add_button("✍ Edit node  ⚠️", async () => {
        const result = await Swal.fire({
            input: "text",
            inputPlaceholder: "Enter content (in newick format)",
            preConfirm: async content => {
                return await tree_command("edit", [node_id, content]);
            },
        });
        if (result.isConfirmed) {
            draw_minimap();
            update();
        }
    }, "Edit the content of this node. Changes the tree structure.");
    if (!view.subtree) {
        add_button("🎯 Set node as outgroup ⚠️", async () => {
            await tree_command("set_outgroup", node_id);
            draw_minimap();
            update();
        }, "Set this node as the 1st child of the root. " +
           "Changes the tree structure.");
    }
    add_button("⬆️ Move branch up ⚠️", async () => {
        await tree_command("move", [node_id, -1]);
        draw_minimap();
        update();
    }, "Move the current branch one step above its current position. " +
        "Changes the tree structure.");
    add_button("⬇️ Move branch down ⚠️", async () => {
        await tree_command("move", [node_id, +1]);
        draw_minimap();
        update();
    }, "Move the current branch one step below its current position. " +
        "Changes the tree structure.");
    add_button("🔃 Sort branch ⚠️", () => sort(node_id),
        "Sort branches below this node according to the current sorting " +
        "function. Changes the tree structure.");
    add_button("🌿 Convert branch to dendrogram ⚠️", async () => {
        await tree_command("to_dendrogram", node_id);
        draw_minimap();
        update();
    }, "Remove all distances from branch. Changes the tree structure.");
    add_button("🟰 Convert branch to ultrametric ⚠️", async () => {
        await tree_command("to_ultrametric", node_id);
        draw_minimap();
        update();
    }, "Make leaves equally distant from node. Changes the tree structure.");
    add_button("✂️ Remove branch ⚠️", async () => {
        await tree_command("remove", node_id);
        draw_minimap();
        update();
    }, "Prune this branch from the tree. Changes the tree structure.");
}


function add_tree_options() {
    add_button("🔭 Reset view", reset_view, "Fit tree to the window.");
    if (view.subtree) {
        add_button("⬅️ Go back to main tree", () => {
            view.subtree = "";
            on_tree_change();
        }, "Exit view on current subtree.");
    }

    if (view.allow_modifications) {
        add_button("🔃 Sort tree ⚠️", () => sort(),
            "Sort all branches according to the current sorting function. " +
                   "Changes the tree structure.");
        add_button("🌿 Convert tree to dendrogram ⚠️", async () => {
            await tree_command("to_dendrogram", []);
            draw_minimap();
            update();
        }, "Remove all distances from tree. Changes the tree structure.");
        add_button("🟰 Convert tree to ultrametric ⚠️", async () => {
            await tree_command("to_ultrametric", []);
            draw_minimap();
            update();
        }, "Make all leaves equally distant from root. " +
                       "Changes the tree structure.");
    }
}


function add_button(text, fn, tooltip) {
    const button = document.createElement("button");
    button.appendChild(document.createTextNode(text));
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
