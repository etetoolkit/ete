// Functions related to the context menu (right-click menu).

import { view, tree_command, on_tree_change, reset_view, sort, get_tid }
    from "./gui.js";
import { draw_minimap } from "./minimap.js";
import { update } from "./draw.js";
import { download_newick, download_seqs } from "./download.js";
import { zoom_into_box } from "./zoom.js";
import { collapse_node } from "./collapse.js";
import { activate_node, deactivate_node } from "./active.js";
import { api, api_put } from "./api.js";
import { icons } from "./icons.js";

export { on_box_contextmenu };

const inputError = Swal.mixin({
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


async function on_box_contextmenu(event, box, name, properties, node_id=[]) {

    event.preventDefault();

    div_contextmenu.innerHTML = "";

    if (box) {
        const name_text = ": " + (name.length < 20 ? name :
                                  (name.slice(0, 8) + "..." + name.slice(-8)));

        add_label("Node" + (name.length > 0 ? name_text : ""));

        add_button("Zoom into branch <span>Dblclick</span>", () => zoom_into_box(box),  "", "zoom");

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
    const safe_properties = { ...properties };
    if (safe_properties.tooltip)
        delete safe_properties["tooltip"]

    add_button("Go to subtree at branch", () => {
        view.subtree += (view.subtree ? "," : "") + node_id;
        on_tree_change();
    }, "Explore the subtree starting at the current node.",
       "login", false);
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
    }, "", "info", false);
    add_button("Download branch as newick", () => download_newick(node_id),
               "Download subtree starting at this node as a newick file.",
               "download", false);
    const nid = get_tid() + "," + node_id;
    const nseq = Number(await api(`/trees/${nid}/nseq`));
    if (nseq > 0)
        add_button("Download " + (nseq === 1 ? "sequence" : `leaf sequences (${nseq})`),
            () => download_seqs(node_id),
                   "Download " + (nseq === 1 ? "sequence" : `leaf sequences (${nseq})`) 
                               + " as fasta file.",
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
                   "open", false);
    else
        add_button("Collapse branch", () => collapse_node(node_id),
                   "Do not show nodes below the current one.",
                   "close", false);

    if (view.active.nodes.nodes.find(n => n.id == String(node_id)))
        add_button("Unselect node <span>Alt+Click</span>", () => deactivate_node(node_id, "nodes"),
                   "Remove current node from active selection.",
                   "unselect", false);
    else
        add_button("Select node <span>Alt+Click</span>", () => activate_node(node_id, safe_properties, "nodes"),
                   "Add current node from active selection.",
                   "hand", false);

    const active = await api(`/trees/${nid}/active`);
    if (active === "active_clade")
        add_button("Unselect clade <span>Shift+Click</span>", () => deactivate_node(node_id, "clades"),
                   "Remove current clade from active selection.",
                   "unselect", false);
    else
        add_button("Select clade <span>Shift+Click</span>", () => activate_node(node_id, safe_properties, "clades"),
                   "Add current clade from active selection.",
                   "hand", false);

    if ("hyperlink" in properties) {
        const [ label, url ] = properties["hyperlink"];
        add_button("Go to " + label, () => window.open(url), 
            url, "external-link-alt");
    }

    if (view.allow_modifications) {
        const nodestyle = await api(`/trees/${nid}/nodestyle`);
        const editable_props = await api(`/trees/${nid}/editable_props`);
        add_node_modifying_options(editable_props, nodestyle, node_id);
    }
}


async function add_json_editor(nid, json, endpoint, reinitialize=false, errortag="json", html) {
    const prefix = `${endpoint}-swal-input`;
    html = html || get_menu_input_html(json, prefix);
    const result = await Swal.fire({
          title: `Edit node ${errortag}`,
          html: html,
          focusConfirm: false,
          preConfirm: () => {
              const newprops = {};
              Object.keys(json).forEach((k, idx) => {
                  const element = document.getElementById(`${prefix}${idx}`);
                  if (element.type == "checkbox")
                      newprops[k] = element.checked;
                  else {
                      const value = element.value;
                      if (value !== "")
                          newprops[k] = value;
                  }
              })
              return newprops;
          }
    });
    if (result.isConfirmed) {
        const newprops = result.value;
        const res = await api_put(`/trees/${nid}/${endpoint}`, newprops);
        if (res.message !== "ok")
            inputError.fire({ text: `An error ocurred when editing node ${errortag}` })
        else {
            if (reinitialize)
                api_put(`/trees/${nid}/reinitialize`);
                view.tree_size = await api(`/trees/${get_tid()}/size`);
            draw_minimap();
            update();
        }
    }
}


const NODESTYLE = {
    nodedot: {
        shape: "Shape",
        size: "Size",
        fgcolor: "Color",
        fgopacity: "Opacity",
    }, 
    background : {
        bgcolor: "Color",
    },
    lines: {
        hz_line_color: "Horizontal line color",
        hz_line_type: "Horizontal line type",
        hz_line_width: "Horizontal line width",
        vt_line_color: "Vertical line color",
        vt_line_type: "Vertical line type",
        vt_line_width: "Vertical line width",
    },
    outline: {
        outline_line_color: "Outline line color",
        outline_line_width: "Outline line width",
        outline_color: "Outline color",
        outline_opacity: "Outline opacity",
    },
}

function get_menu_input_html(json, prefix, counter=0) {
    return  Object.entries(json).map(([k, v], idx) => {
        idx += counter;
        return `<div class="swal2-input-flex">` +
        `<label class="swal2-input-label" for="${prefix}${idx}">${k}</label>`+
        `<input id="${prefix}${idx}" class="swal2-input" value="${v}"`+
        ([true, "true", false, "false"].includes(v) ? "type='checkbox'>" : ">") +
        `</div>`}).join(" ");
}

function get_nodestyle_html(nodestyle) {
    function get_label(label) {
        return `<div class='swal2-input-title'>${label}</div>`
    }
    function get_json(style) {
        const json = {};
        Object.entries(style).forEach(([k, v]) =>
            json[v] = nodestyle[k])
        return json;
    }
    const prefix = "update_nodestyle-swal-input";
    let column = 0
    let html = get_label("Foreground")
    html += get_menu_input_html(get_json(NODESTYLE.nodedot), prefix, column)
    column += Object.keys(NODESTYLE.nodedot).length;
    html += get_label("Background")
    html += get_menu_input_html(get_json(NODESTYLE.background), prefix, column)
    column += Object.keys(NODESTYLE.background).length;
    html += get_label("Lines")
    html += get_menu_input_html(get_json(NODESTYLE.lines), prefix, column)
    column += Object.keys(NODESTYLE.lines).length;
    html += get_label("Outline (collapsed)")
    html += get_menu_input_html(get_json(NODESTYLE.outline), prefix, column)
    column += Object.keys(NODESTYLE.outline).length;
    html += get_menu_input_html({ "Apply to all descendants": false }, prefix, column)
    return html
}

function format_nodestyle(style) {
    const keys = [
        ...Object.keys(NODESTYLE.nodedot),
        ...Object.keys(NODESTYLE.background),
        ...Object.keys(NODESTYLE.lines),
        ...Object.keys(NODESTYLE.outline),
    ];
    const nodestyle = {};
    keys.forEach(key => nodestyle[key] = style[key]);
    nodestyle["extend_to_descendants"] = false
    return nodestyle;
}

async function add_node_modifying_options(properties, nodestyle, node_id) {
    const nid = get_tid() + "," + node_id;
    nodestyle = format_nodestyle(nodestyle);
    add_button("Edit node properties", () =>
        add_json_editor(nid, properties, "update_props", true, "properties"),
       "Edit the properties of this node. Changes the tree structure.",
       "edit", true);
    add_button("Edit node style", () => {
        const html = get_nodestyle_html(nodestyle);
        add_json_editor(nid, nodestyle, "update_nodestyle", false, "style", html)},
       "Edit the style of this node. Changes the tree structure.",
       "edit", false);
    if (!view.subtree) {
        add_button("Root on this node", async () => {
            await tree_command("root_at", node_id);
            draw_minimap();
            update();
        }, "Set this node as the root of the tree. Changes the tree structure.",
           "root", true);
    }
    add_button("Move branch up", async () => {
        await tree_command("move", [node_id, -1]);
        draw_minimap();
        update();
    }, "Move the current branch one step above its current position. " +
        "Changes the tree structure.",
        "up", true);
    add_button("Move branch down", async () => {
        await tree_command("move", [node_id, +1]);
        draw_minimap();
        update();
    }, "Move the current branch one step below its current position. " +
        "Changes the tree structure.",
        "down", true);
    add_button("Sort branch", () => sort(node_id),
        "Sort branches below this node according to the current sorting " +
        "function. Changes the tree structure.",
        "sort", true);
    add_button("Remove branch", async () => {
        await tree_command("remove", node_id);
        draw_minimap();
        update();
    }, "Prune this branch from the tree. Changes the tree structure.",
        "trash", true);
}


function add_tree_options() {
    add_button("Reset view", reset_view,
               "Fit tree to the window.", "view");
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
            "sort", true);
        if (!view.subtree) {
            add_button("Reload tree", async () => {
                await tree_command("reload", get_tid());
                on_tree_change();
            }, "Reload current tree. Restores the original tree structure.",
                "refresh", true);
        }
    }
}

function create_icon(name) {
    const el = document.createElement("div");
    el.innerHTML = icons[name] || "";
    el.style.height = "20px";
    if (name === "exclamation")
        el.style["margin-left"] = "3px";
    return el;
}

function add_button(text, fn, tooltip, icon_before, icon_warning=false) {
    const button = document.createElement("button");
    if (icon_before)
        button.appendChild(create_icon(icon_before));
    const content = document.createElement("div");
    content.innerHTML = text;
    button.appendChild(content)
    if (icon_warning) 
        button.appendChild(create_icon("exclamation"))
    button.addEventListener("click", event => {
        div_contextmenu.style.visibility = "hidden";
        fn(event);
    });
    button.classList.add("ctx_button");

    if (tooltip)
        button.setAttribute("title", tooltip);

    div_contextmenu.appendChild(button);
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
