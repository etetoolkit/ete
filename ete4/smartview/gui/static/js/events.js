// Handle gui events.  
import { view, get_tid, menus, coordinates, reset_view, show_minimap, show_help }
    from "./gui.js";
import { zoom_around, zoom_aligned } from "./zoom.js";
import { move_minimap_view } from "./minimap.js";
import { drag_start, drag_stop, drag_move } from "./drag.js";
import { search } from "./search.js";
import { select_by_command, prune_by_selection, remove_selections } from "./select.js";
import { activate_node, deactivate_node, update_active_nodes } from "./active.js";
import { update } from "./draw.js";
import { on_box_contextmenu } from "./contextmenu.js";

export { init_events, notify_parent };


function init_events() {
    document.addEventListener("keydown", on_keydown);

    document.addEventListener("wheel", on_wheel, {passive: false});
    // NOTE: chrome now uses passive=true otherwise

    document.addEventListener("mousedown", on_mousedown);

    document.addEventListener("mousemove", on_mousemove);

    document.addEventListener("mouseup", on_mouseup);

    document.addEventListener("contextmenu", on_contextmenu);

    window.addEventListener("resize", on_resize);

    document.addEventListener("touchstart", on_touchstart);

    document.addEventListener("touchmove", on_touchmove);

    document.addEventListener("touchend", on_touchend);

    if (self !== top)  // ETE is not within an iframe
        window.addEventListener("message", on_postMessage)
}


// Hotkeys.
function on_keydown(event) {
    const key = event.key;  // shortcut
    let is_hotkey = true;  // will set to false if it isn't

    try {
        if (document.querySelector(".tp-dfwv").contains(event.target))
                return;  // avoid interfering with writing on a field of the menus
    } catch {}

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
        menus.minimap.refresh();
    }
    else if (key === "p")
        menus.pane.expanded = !menus.pane.expanded;
    else if (key === "d")
        view.download.svg();
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

    if (div_aligned.contains(event.target) && view.aligned.zoom)
        zoom_aligned(point, zoom_in)
    else
        zoom_around(point, zoom_in, do_zoom);
}

function is_svg(element) {
    return element.namespaceURI === "http://www.w3.org/2000/svg";
}


// Mouse down -- select text, or move in minimap, or start dragging.
function on_mousedown(event) {
    if (!div_contextmenu.contains(event.target))
        div_contextmenu.style.visibility = "hidden";

    if (event.button && event.button !== 0)
        return;  // we are only interested in left-clicks

    if (view.select_text)
        return;  // if we can select text, that's it (use the default)

    const point = {x: event.pageX, y: event.pageY};

    if (div_visible_rect.contains(event.target))
        drag_start(point, div_visible_rect);
    else if (div_minimap.contains(event.target))
        move_minimap_view(point);
    else if (div_aligned_grabber.contains(event.target))
        drag_start(point, div_aligned);
    else if (div_aligned.contains(event.target) && view.aligned.zoom)
        drag_start(point, div_aligned, false);
    else if (div_tree.contains(event.target))
        drag_start(point, div_tree);
    // NOTE: div_tree contains div_minimap, which also contains div_visible,
    // so the order in which to do the contains() tests matters.
}

function update_tooltip(event) {
    
    if (!event.target.getAttribute)
        return

    function clear_timeout() {
        if (view.tooltip.timeout) {
            clearTimeout(view.tooltip.timeout);
            view.tooltip.timeout = undefined;
        }
    }

    if (tooltip.contains(event.target)) {
        clear_timeout();
        return
    }

    const style = tooltip.style;
    const data = event.target.getAttribute("data-tooltip");
    if (data) {
        tooltip.innerHTML = data;
        style.display = "block";
        const bbox = event.target.getBoundingClientRect();
        style.left = bbox.x + "px";
        style.top = bbox.y + "px";
        clear_timeout();
    } else if (!view.tooltip.timeout)
        view.tooltip.timeout = setTimeout(() => style.display = "none", 500);
}

// Mouse move -- move tree view if dragging, update position coordinates.
function on_mousemove(event) {
    const point = {x: event.pageX, y: event.pageY};

    drag_move(point);

    [view.pos.cx, view.pos.cy] = coordinates(point);

    update_tooltip(event);
}


// Mouse up -- stop dragging.
function on_mouseup(event) {
    drag_stop();
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


// Pinch and zoom in touchscreen devices.

const finger_d = {x: 0, y: 0};  // distance between the two fingers, for x and y


// Touch start -- record the distance between the two fingers.
function on_touchstart(event) {
    if (event.touches.length > 2) {
        event.preventDefault();
    }
    else if (event.touches.length === 2) {
        event.preventDefault();
        const [t0, t1] = event.touches;
        const [x0, y0] = [t0.pageX, t0.pageY],
              [x1, y1] = [t1.pageX, t1.pageY];
        [finger_d.x, finger_d.y] = [Math.abs(x1 - x0), Math.abs(y1 - y0)];
    }
    else {  // single finger: like a pointer
        on_mousedown(event.touches[0]);
    }
}


// Touch move -- zoom according to the change in distance of the two fingers.
function on_touchmove(event) {
    if (event.touches.length > 2) {
        event.preventDefault();
    }
    else if (event.touches.length == 2) {
        event.preventDefault();
        const dx_min = div_tree.offsetWidth * 0.05,    // bigger than 5% of the
              dy_min = div_tree.offsetHeight * 0.05;   // screen width & height
        const [t0, t1] = event.touches;
        const [x0, y0] = [t0.pageX, t0.pageY],
              [x1, y1] = [t1.pageX, t1.pageY];

        const [dx, dy] = [Math.abs(x1 - x0), Math.abs(y1 - y0)];

        const do_zoom = {x: dx > dx_min, y: dy > dy_min};
        const zoom_in = (dx + dy) > (finger_d.x + finger_d.y);  // but not used
        const qz = {x: dx / finger_d.x,   // the zoom ratio qz is the same
                    y: dy / finger_d.y};  // as the distance ratio

        if (view.drawer.type === "circ")  // for those, we want zx == zy
            qz.x = qz.y = Math.sqrt(qz.x * qz.y);  // geometric mean

        zoom_around({x: x1, y: y1}, zoom_in, do_zoom, qz);

        [finger_d.x, finger_d.y] = [Math.abs(x1 - x0), Math.abs(y1 - y0)];
    }
    else {  // single finger: just drag the image
        on_mousemove(event.touches[0]);
    }
}


function on_touchend(event) {
    if (event.touches.length > 1)
        event.preventDefault();
    else
        on_mouseup(event.touches[0]);
}


function sendPostMessage(props) {
    parent.postMessage({ tid: get_tid(), ...props }, "*");
}


function notify_parent(selectionMode, { eventType, name, color, node }) {
    if (self === top)  // only notify when encapsulated in iframe
        return

    // Hovering over a node
    if (selectionMode === "hover")
        sendPostMessage({
            selectionMode: selectionMode,
            eventType: eventType,
            node: node
        })

    else if (selectionMode === "active")
        sendPostMessage({
            selectionMode: selectionMode,
            nodes: view.active.nodes,
        })

    else if (selectionMode === "saved")
        sendPostMessage({ 
            selectionMode: selectionMode,
            eventType: eventType,
            name: name,
            color: color,
        })
}

async function on_postMessage(event) {
    // Selection when placing ETE in iframe
    
    // TODO: we should register allowed origins
    //if (!wiew.allowed_origins.includes(event.origin))
        //return
    
    const { selectionMode, eventType, name, node, nodes, selectCommand } = event.data;

    div_tree.style.cursor = "wait";

    if (selectionMode === "active") {

        if (eventType === "select" && node && node.id)
            activate_node(node.id, node)

        else if (eventType === "remove" && node && node.id)
            deactivate_node(node.id)

        else if (eventType === "update") {
            update_active_nodes(nodes || [])
        }


    } else if (selectionMode === "saved") {
        // Selection
        if (eventType === "select" && selectCommand)
            try { await select_by_command(selectCommand, name) } catch {}

        // Remove selection
        else if (eventType === "remove" && name) {
            if (name === "*")
                remove_selections(true); // purge from backend as well
            else if (view.selected[name])
                view.selected[name].remove();
        } 

        // Prune based on selection names
        else if (eventType === "prune" && name)
            prune_by_selection(name.trim().split(","));

    }


    div_tree.style.cursor = "auto";
}
