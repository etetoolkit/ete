// Search-related functions.

import { view, menus, get_tid } from "./gui.js";
import { draw_tree } from "./draw.js";
import { api } from "./api.js";
import { store_selection } from "./select.js";

export { search, get_searches, remove_searches, get_search_class, colorize_searches };


const searchError = Swal.mixin({
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


// Search nodes in the server and redraw the tree (with the results too).
async function search() {
    let search_text;

    const result = await Swal.fire({
        input: "text",
        position: "bottom-start",
        inputValue: view.search_cache ?? "",
        inputPlaceholder: "Enter name (or ? for help)",
        showClass: { popup: "swal2-search" },
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

                document.querySelector(".swal2-container").style.cursor = "wait";

                const qs = `text=${encodeURIComponent(text)}`;
                return await api(`/trees/${get_tid()}/search?${qs}`);
            } catch (exception) {
                searchError
                    .fire({ html: exception.message })
                    .then(() => search());
                // Store in cache to allow for correction
                view.search_cache = search_text;
            }
        },
    });

    if (result.isConfirmed) {
        const res = result.value;  // shortcut

        try {
            if (res.message !== "ok")
                throw new Error(res.message);

            if (res.nresults === 0)
                throw new Error(`No results found by: ${search_text}`);

            store_search(search_text, res);
            // Search was successful
            view.search_cache = undefined;
            draw_tree();

        } catch (exception) {
            searchError
                .fire({ html: exception.message })
                .then(() => search());
            // Store in cache to allow for correction
            view.search_cache = search_text;
        }
    }

    div_tree.style.cursor = "auto";
    return search_text;
}

// Store search with info from backend (number of results and parents)
function store_search(search_text, res) {
    // purple, pink, yellow, blue, turquoise
    const colors = ["#9b5de5", "#f15bb5", "#fee440", "#00bbf9", "#00f5d4"];
    const nsearches = Object.keys(view.searches).length;

    view.searches[search_text] = {
        results: {n: res.nresults,
                  opacity: 0.4,
                  color: colors[nsearches % colors.length]},
        parents: {n: res.nparents,
                  color: "#000",
                  width: 2.5},
    };

    add_search_to_menu(search_text);
}

// Add a folder to the menu that corresponds to the given search text
// and lets you change the result nodes color and so on.
function add_search_to_menu(text) {
    const folder = menus.searches.addFolder({ title: text, expanded: false });

    const vsearch = view.searches[text];

    vsearch.remove = async function(purge=true) {
        if (purge) {
            const qs = `text=${encodeURIComponent(text)}`;
            await api(`/trees/${get_tid()}/remove_search?${qs}`);
        }
        delete view.searches[text];
        folder.dispose();
        draw_tree();
    }

    const folder_style = folder.controller.view.buttonElement.style;

    folder_style.background = vsearch.results.color;

    const on_change = () => {
        folder_style.background = vsearch.results.color;
        colorize_search(text);
    }

    folder.addButton({ title: "edit search" }).on("click", async () => {
        view.search_cache = text;
        const new_search = await search();
        if (view.searches[new_search])
            view.searches[text].remove();
    })

    if (!Object.keys(view.selected).includes(text))
        folder.addButton({ title: "convert search to selection" })
            .on("click", async () => {
                const qs = `text=${encodeURIComponent(text)}`;
                await api(`/trees/${get_tid()}/search_to_selection?${qs}`);
                store_selection(text, {
                    nresults: vsearch.results.n, nparents: vsearch.parents.n,
                })
                vsearch.remove();
            })

    const folder_results = folder.addFolder({ title: `results (${vsearch.results.n})` });
    folder_results.addBinding(vsearch.results, "opacity",
        { min: 0, max: 1, step: 0.1 })
        .on("change", on_change);
    folder_results.addBinding(vsearch.results, "color", { view: "color" })
        .on("change", on_change);

    const folder_parents = folder.addFolder({ title: `parents (${vsearch.parents.n})` });
    folder_parents.addBinding(vsearch.parents, "color", { view: "color" })
        .on("change", on_change);
    folder_parents.addBinding(vsearch.parents, "width", { min: 0.1, max: 10 })
        .on("change", on_change);

    folder.addButton({ title: "remove" }).on("click", vsearch.remove);
}

// Return a class name related to the results of searching for text.
function get_search_class(text, type="results") {
    return "search_" + type + "_" + text.replace(/[^A-Za-z0-9_-]/g, '');
}


function colorize_search(text) {
    const search = view.searches[text];

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


function colorize_searches() {
    Object.keys(view.searches).forEach(text => colorize_search(text));
}

// Get searches from api and fill view.searches
async function get_searches() {
    const searches = await api(`/trees/${get_tid()}/searches`);
    Object.entries(searches.searches).forEach(([text, res]) => store_search(text, res));
}

// Empty view.searches.
function remove_searches() {
    const texts = Object.keys(view.searches);
    texts.forEach(text => view.searches[text].remove(false));
}


function show_search_help() {
    const help_text = `
<div style="text-align: left">
<br />
<h3>Simple search</h3><br />

<p>Put a text in the search box to find all the nodes whose name matches
it.</p><br />

<p>The search will be <i>case-insensitive</i> if the text is all in lower
case, and <i>case-sensitive</i> otherwise.</p><br /><br />

<h3>Regular expression search</h3><br />

<p>To search for names mathing a given regular expression, you can prefix your
text with the command <b>/r</b> (the <i>regexp command</i>) and follow it
with the regular expression.</p><br /><br />

<h3>Expression search</h3><br />

<p>When prefixing your text with <b>/e</b> (the <i>eval command</i>),
you can use a quite general Python expression to search for nodes. This is
the most powerful search method available (and the most complex to
use).</p><br />

<p>The expression will be evaluated for every node, and will select those
that satisfy it. In the expression you can use (among others) the following
variables, with their straightforward interpretation: <b>node</b>,
<b>parent</b>, <b>is_leaf</b>, <b>length</b> / <b>dist</b> / <b>d</b>,
<b>properties</b> / <b>p</b>, <b>children</b> / <b>ch</b>, <b>size</b>,
<b>dx</b>, <b>dy</b>, <b>regex</b>.</p><br /><br />

<h3>Topological search</h3><br />

<p>Similar to the expression search, if you prefix your text with <b>/t</b>
(the <i>topological command</i>), you can write a newick tree with quoted
names in each node containing an eval command. This will select the nodes
that satisfy the full subtree of expressions that you passed.</p><br /><br />

<h3>Examples of searches and possible matches</h3>

</div>

<table style="margin: 0 auto">
<tbody>

<tr><td></td><td>&nbsp;&nbsp;&nbsp;</td><td></td></tr>
<tr><td style="text-align: left"><b>citrobacter</b></td><td></td>
<td style="text-align: left">
will match nodes named "Citrobacter werkmanii" and "Citrobacter youngae"
</td></tr>

<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td style="text-align: left"><b>UBA</b></td><td></td>
<td style="text-align: left">
will match "spx UBA2009" but not "Rokubacteriales"
</td></tr>

<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td style="text-align: left"><b>/r sp\\d\\d</b></td><td></td>
<td style="text-align: left">
will match any name that contains "sp" followed by (at least)
two digits, like "Escherichia sp002965065" and "Citrobacter sp005281345"
</td></tr>

<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td style="text-align: left"><b>/e d &gt; 1</b></td><td></td>
<td style="text-align: left">
will match nodes with a length &gt; 1
</td></tr>

<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td style="text-align: left"><b>/e is_leaf and p['species'] == 'Homo'</b></td><td></td>
<td style="text-align: left">
will match leaf nodes with property "species" equal to "Homo"
</td></tr>

<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>
<tr><td style="text-align: left"><b>/t ("is_leaf","d > 1")"name=='AB'"</b></td><td></td>
<td style="text-align: left">
will match nodes named "AB" that have two children, one that is a leaf and another that has a length &gt; 1
</td></tr>

</tbody>
</table>

`;
    Swal.fire({
        title: "Searching nodes",
        html: help_text,
    });
}
