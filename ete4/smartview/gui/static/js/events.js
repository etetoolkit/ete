// Handle gui events.

import { view, menus, coordinates, reset_view, show_minimap, show_help }
    from "./gui.js";
import { zoom_around } from "./zoom.js";
import { move_minimap_view } from "./minimap.js";
import { drag_start, drag_stop, drag_move } from "./drag.js";
import { search } from "./search.js";
import { update } from "./draw.js";
import { on_box_contextmenu } from "./contextmenu.js";

export { init_events };


function init_events() {
    document.addEventListener("keydown", on_keydown);

    document.addEventListener("wheel", on_wheel, {passive: false});
    // NOTE: chrome now uses passive=true otherwise

    document.addEventListener("pointerdown", on_pointerdown);

    document.addEventListener("pointerup", on_pointerup);

    document.addEventListener("pointermove", on_pointermove);

    document.addEventListener("contextmenu", on_contextmenu);

    window.addEventListener("resize", on_resize);
}


// Hotkeys.
function on_keydown(event) {
    const key = event.key;  // shortcut
    let is_hotkey = true;  // will set to false if it isn't

    const menu_divs = [
        div_menu_main, div_menu_representation, div_menu_tags_searches];
    for (const div of menu_divs)
        if (div.contains(event.target))
            return;  // avoid interfering with writing on a field of the menus

    if (key === "F1") {
        show_help();
    }
    else if (key === "/") {
        search();
    }
    else if (key === "r") {
        reset_view();
    }
    else if (key === "m") {
        view.minimap.show = !view.minimap.show;
        show_minimap(view.minimap.show);
        menus.main.updateDisplay();  // update the info box on the top-right
    }
    else if (key === "+") {
        const center = {x: div_tree.offsetWidth / 2,
                        y: div_tree.offsetHeight / 2};
        const zoom_in = true;
        const do_zoom = {x: !event.ctrlKey, y: !event.altKey};
        zoom_around(center, zoom_in, do_zoom);
    }
    else if (key === "-") {
        const center = {x: div_tree.offsetWidth / 2,
                        y: div_tree.offsetHeight / 2};
        const zoom_in = false;
        const do_zoom = {x: !event.ctrlKey, y: !event.altKey};
        zoom_around(center, zoom_in, do_zoom);
    }
    else if (key === "ArrowLeft") {
        const fraction = event.shiftKey ? 0.2 : 0.04;
        view.tl.x -= fraction * div_tree.offsetWidth / view.zoom.x;
        update();
    }
    else if (key === "ArrowRight") {
        const fraction = event.shiftKey ? 0.2 : 0.04;
        view.tl.x += fraction * div_tree.offsetWidth / view.zoom.x;
        update();
    }
    else if (key === "ArrowUp") {
        const fraction = event.shiftKey ? 0.2 : 0.04;
        view.tl.y -= fraction * div_tree.offsetHeight / view.zoom.y;
        update();
    }
    else if (key === "ArrowDown") {
        const fraction = event.shiftKey ? 0.2 : 0.04;
        view.tl.y += fraction * div_tree.offsetHeight / view.zoom.y;
        update();
    }
    else if (key === "Escape") {
        div_contextmenu.style.visibility = "hidden";
    }
    else {
        is_hotkey = false;
    }

    if (is_hotkey)
        event.preventDefault();
}


// Mouse wheel -- zoom in/out (instead of scrolling).
function on_wheel(event) {
    const g_panel0 = div_tree.children[0].children[0];

    if (!is_svg(event.target) || g_panel0.contains(event.target))
        return;  // it will be done on the nodes instead

    event.preventDefault();

    const point = {x: event.pageX, y: event.pageY};
    const zoom_in = event.deltaY < 0;
    const do_zoom = {x: !event.ctrlKey, y: !event.altKey};

    zoom_around(point, zoom_in, do_zoom);
}

function is_svg(element) {
    return element.namespaceURI === "http://www.w3.org/2000/svg";
}


// Mouse down -- select text, or move in minimap, or start dragging.
function on_pointerdown(event) {
    if (!div_contextmenu.contains(event.target))
        div_contextmenu.style.visibility = "hidden";

    if (event.button !== 0)
        return;  // we are only interested in left-clicks

    if (view.select_text)
        return;  // if we can select text, that's it (use the default)

    const point = {x: event.pageX, y: event.pageY};

    if (div_visible_rect.contains(event.target))
        drag_start(point, div_visible_rect);
    else if (div_minimap.contains(event.target))
        move_minimap_view(point);
    else if (div_aligned.contains(event.target))
        drag_start(point, div_aligned);
    else if (div_tree.contains(event.target))
        drag_start(point, div_tree);
    // NOTE: div_tree contains div_minimap, which also contains div_visible,
    // so the order in which to do the contains() tests matters.
}


// Mouse up -- stop dragging.
function on_pointerup(event) {
    drag_stop();
}


// Mouse move -- move tree view if dragging, update position coordinates.
function on_pointermove(event) {
    const point = {x: event.pageX, y: event.pageY};

    drag_move(point);

    [view.pos.cx, view.pos.cy] = coordinates(point);
}


function on_contextmenu(event) {
    if (event.target !== div_tree.children[0])
        return;  // it will be done on the nodes instead

    on_box_contextmenu(event);
}


function on_resize(event) {
    update();
    // We could also draw_minimap()
}
