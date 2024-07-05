// Search-related functions.

import { view, menus, get_tid } from "./gui.js";
import { draw_tree } from "./draw.js";
import { api } from "./api.js";

export { search, remove_searches, get_search_class, colorize_searches };


// Search nodes in the server and redraw the tree (with the results too).
async function search() {
    let search_text;

    const result = await Swal.fire({
        input: "text",
        position: "bottom-start",
        inputPlaceholder: "Enter name (or ? for help)",
        showConfirmButton: false,
        preConfirm: async text => {
            if (!text)
                return false;  // prevent popup from closing

            search_text = text;  // to be used when checking the result later on

            try {
                if (text.trim() === "?") {
                    show_search_help();
                    return;
                }

                if (text in view.searches)
                    throw new Error("Search already exists.");

                const qs = `text=${encodeURIComponent(text)}`;
                return await api(`/trees/${get_tid()}/search?${qs}`);
            }
            catch (exception) {
                Swal.fire({
                    position: "bottom-start",
                    showConfirmButton: false,
                    html: exception,
                    icon: "error",
                });
            }
        },
    });

    if (result.isConfirmed) {
        const res = result.value;  // shortcut

        if (res.message === "ok") {
            const colors = ["#FF0", "#F0F", "#0FF", "#F00", "#0F0", "#00F"];
            const nsearches = Object.keys(view.searches).length;

            view.searches[search_text] = {
                results: {n: res.nresults,
                          opacity: 0.4,
                          color: colors[nsearches % colors.length]},
                parents: {n: res.nparents,
                          color: "#000",
                          width: 5},
                order: menus.searches.children.length,
            };

            add_search_to_menu(search_text);

            update_order_lists();  // so this new position appears everywhere

            draw_tree();
        }
        else {
            Swal.fire({
                position: "bottom-start",
                showConfirmButton: false,
                text: res.message,
                icon: "error",
            });
        }
    }
}


// Update the lists with the sort order for each search.
function update_order_lists() {
    const folders = menus.searches.children.slice(1);
    // menus.searches has a button first, and then the search folders.

    const order_options = {};  // to use as the options for the list with orders
    for (let i = 0; i < folders.length; i++)
        order_options[i] = `${i}`;  // {"0": "0", "1": "1", ...}

    folders.forEach((folder, i) => update_order_list(folder, i, order_options));
}


function update_order_list(folder, i, order_options) {
    const index_of_list = folder.children.length - 2;
    // The list is the element before the last one.

    folder.children[index_of_list].dispose();  // delete the drowpdown list

    const search = view.searches[folder.title];

    search.order = `${i}`;
    const old_order = search.order;  // to switch the other to this when changed

    folder.addBinding(search, "order", {
        index: index_of_list,  // we put the list in the same position it was
        label: "sort order",
        options: order_options,
      }).on("change", () => {
          // Switch search that was in that order before to our old order.
          Object.values(view.searches)
              .filter(s => s.order === search.order && s !== search)
              .map(s => s.order = old_order);

          setTimeout(reconstruct_search_folders);  // don't delete us yet!
      });
}


function reconstruct_search_folders() {
    // Remove them all.
    const folders = menus.searches.children.slice(1);
    folders.forEach(folder => folder.dispose());

    // Add the searches in order.
    Object.entries(view.searches)
        .sort(([,s1], [,s2]) => Number(s1.order) - Number(s2.order))
        .map(([text,]) => text)
        .forEach(add_search_to_menu);

    update_order_lists();

    colorize_searches();
}


// Return a class name related to the results of searching for text.
function get_search_class(text, type="results") {
    return "search_" + type + "_" + text.replace(/[^A-Za-z0-9_-]/g, '');
}


// Add a folder to the menu that corresponds to the given search text
// and lets you change the result nodes color and so on.
function add_search_to_menu(text) {
    const folder = menus.searches.addFolder({title: text, expanded: false});

    const search = view.searches[text];

    search.remove = function() {
        delete view.searches[text];
        folder.dispose();
        update_order_lists();
        draw_tree();
    }

    const folder_style = folder.controller.view.buttonElement.style;

    folder_style.background = search.results.color;

    const on_change = () => {
        folder_style.background = search.results.color;
        colorize_search(text);
    }

    const folder_results = folder.addFolder(
        {title: `results (${search.results.n})`, expanded: false});
    folder_results.addBinding(search.results, "opacity", {min: 0, max: 1, step: 0.01})
        .on("change", on_change);
    folder_results.addBinding(search.results, "color")
        .on("change", on_change);

    const folder_parents = folder.addFolder(
        {title: `parents (${search.parents.n})`, expanded: false});
    folder_parents.addBinding(search.parents, "color")
        .on("change", on_change);
    folder_parents.addBinding(search.parents, "width", {min: 0.1, max: 20})
        .on("change", on_change);

    folder.addBinding(search, "order", {label: "sort order", options: {}});

    folder.addButton({title: "remove"}).on("click", search.remove);
}


// Apply colors (and opacity) to results and parents of a search made
// on the given text.
function colorize_search(text) {
    const search = view.searches[text];

    // Select (by their class) elements that are the results and
    // parents of the search, and apply the style (color and
    // opacity) specified in view.searches[text].

    const cresults = get_search_class(text, "results");
    Array.from(div_tree.getElementsByClassName(cresults)).forEach(e => {
        e.style.opacity = search.results.opacity;
        e.style.fill = search.results.color;
    });

    const cparents = get_search_class(text, "parents");
    Array.from(div_tree.getElementsByClassName(cparents)).forEach(e => {
        e.style.stroke = search.parents.color;
        e.style.strokeWidth = search.parents.width;
    });
}


// Colorize all the elements related to searches (nodes that are the
// results, and lines for their parent nodes).
function colorize_searches() {
    Object.entries(view.searches)
        .sort(([,s1], [,s2]) => Number(s1.order) - Number(s2.order))
        .forEach(([text,]) => colorize_search(text));
}


// Empty view.searches.
function remove_searches() {
    const texts = Object.keys(view.searches);
    texts.forEach(text => view.searches[text].remove());
}


function show_search_help() {
    const help_text = `
<div style="text-align: left">

<details>
<summary><b>Simple search</b></summary>
<span>

<p>Put a text in the search box to find all the nodes whose name matches
it.</p><br />

<p>The search will be <i>case-insensitive</i> if the text is all in lower
case, and <i>case-sensitive</i> otherwise.</p>

</span>
</details>

<br />

<details>
<summary><b>Regular expression search</b></summary>
<span>

<p>To search for names matching a given regular expression, you can prefix your
text with the command <b>/r</b> (the <i>regexp command</i>) and follow it
with the regular expression.</p>

</span>
</details>

<br />

<details>
<summary><b>General expression search</b></summary>
<span>

<p>When prefixing your text with <b>/e</b> (the <i>eval command</i>),
you can use a Python expression to search for nodes.
The expression will be evaluated for every node, and the ones that satisfy
it will be selected.</p><br />

<p>In the expression you can use, among others, the following
symbols: <b>node</b>,
<b>parent</b>, <b>name</b>, <b>is_leaf</b>, <b>length</b> or <b>dist</b> or <b>d</b>,
<b>properties</b> or <b>props</b> or <b>p</b>, <b>children</b> or <b>ch</b>,
<b>size</b>, <b>dx</b>, <b>dy</b>, <b>regex</b>.</p>

</span>
</details>

<br />

<details>
<summary><b>Topological search</b></summary>
<span>

<p>Similar to the expression search, if you prefix your text with <b>/t</b>
(the <i>topological command</i>), you can write a newick tree with quoted
names in each node containing an eval command. This will select the nodes
that satisfy the full subtree of expressions that you passed.</p>

</span>
</details>

<br />

<details>
<summary><b>Examples</b></summary>
<span>

<table style="margin: 0 auto">
<thead>
<tr><th>Search text</th><th></th><th>Possible matches</th></tr>
</thead>
<tbody>

<tr><td></td><td>&nbsp;&nbsp;&nbsp;</td><td></td></tr>
<tr><td style="text-align: left"><code>citrobacter</code></td><td></td>
<td style="text-align: left">
nodes named "[...]citrobacter[...]" (case insensitive)
</td></tr>

<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td style="text-align: left"><code>BA</code></td><td></td>
<td style="text-align: left">
matches "UBA20" but not "Rokubacteria"
</td></tr>

<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td style="text-align: left"><code>/r sp\\d\\d</code></td><td></td>
<td style="text-align: left">
any name with "sp" followed by 2 digits, like "E. sp0029" and "C. sp0052"
</td></tr>

<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td style="text-align: left"><code>/e d &gt; 1</code></td><td></td>
<td style="text-align: left">
nodes with length &gt; 1
</td></tr>

<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td style="text-align: left"><code>/e is_leaf and p['species'] == 'Homo'</code></td><td></td>
<td style="text-align: left">
leaf nodes with property "species" equal to "Homo"
</td></tr>

<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td style="text-align: left"><code>/t ("is_leaf","d > 1")"name=='AB'"</code></td><td></td>
<td style="text-align: left">
nodes named "AB" with two children, one that is a leaf and another that has a length &gt; 1
</td></tr>

</tbody>
</table>

</span>
</details>

</div>
`;
    Swal.fire({
        title: "Searching nodes",
        html: help_text,
        width: "80%",
    });
}
