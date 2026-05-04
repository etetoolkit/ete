// Per-frame performance debug overlay.
// Toggle visibility with Shift+D. Enabled by default.

export { init_debug, update_debug };


let div_debug = null;
let visible = true;


function init_debug() {
    div_debug = document.getElementById('div_debug');
    if (!div_debug) return;

    div_debug.querySelector('.dbg-close').addEventListener('click', () => {
        visible = false;
        div_debug.style.display = 'none';
    });

    document.addEventListener('keydown', e => {
        if (e.key === 'D' && e.shiftKey) {
            visible = !visible;
            div_debug.style.display = visible ? '' : 'none';
        }
    });
}


function update_debug(stats, rtt_ms) {
    if (!div_debug) return;

    const ms  = v => (v != null ? `${v} ms`          : '—');
    const num = v => (v != null ? v.toLocaleString()  : '—');

    const rows = [
        ['RTT',      ms(Math.round(rtt_ms))],
        ['Server',   ms(stats.t_draw_ms)],
        ...(stats.t_preload_ms != null ? [
            ['Preload',  ms(stats.t_preload_ms)],
        ] : []),
        ['Commands', num(stats.n_commands)],
        ...(stats.n_visible != null ? [
            ['Visible',  num(stats.n_visible)],
            ['Cached',   num(stats.n_cached)],
            ['Fetched',  num(stats.n_fetched)],
        ] : []),
    ];

    div_debug.querySelector('.dbg-body').innerHTML =
        rows.map(([k, v]) => `<tr><td>${k}</td><td>${v}</td></tr>`).join('');
}
