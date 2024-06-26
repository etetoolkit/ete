// Functions related to the interaction with the server, including html cleanup
// and error handling.

export { escape_html, hash, api, api_post, api_put };


// API calls.

// Make a GET api call and return the retrieved data.
async function api(endpoint) {
    const response = await fetch(endpoint);

    await assert(response.status === 200, "Request failed :(", response);

    return await response.json();
}

// Make a POST api call.
async function api_post(endpoint, data) {
    const response = await fetch(endpoint, {
        method: "POST",
        body: data,
    });

    await assert(response.status === 201, "Upload failed", response);

    return await response.json();
}


// Make a PUT api call.
async function api_put(endpoint, params=undefined) {
    let response = await fetch(endpoint, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(params),
    });

    await assert(response.status === 200, "Modification failed :(", response);

    return await response.json();
}


// Text manipulation.

// Return the original text with the given replacements made.
function escape_html(text, replacements=[
        "& &amp;", "< &lt;", "> &gt;", '" &quot;', "' &#039;"]) {
    const pairs = replacements.map(pair => pair.split(" "));
    return pairs.reduce((t, [a, b]) => t.replace(new RegExp(a, "g"), b), text);
}


// Return a ~32-bit hash. Based on https://stackoverflow.com/questions/7616461
function hash(text) {
    const acc = (h, char) => ((h << 5) - h + char.charCodeAt(0)) | 0;
    return (text.split("").reduce(acc, 0) - (1 << 31)).toString(36);
}


// Error handling.

async function assert(condition, message, response=undefined) {
    if (!condition) {
        const response_error = response ? `<br><br>
            <b>Response status:</b> ${response.status}<br>
            <b>Message:</b> ${escape_html(await get_error(response))}` : "";
        throw new Error(message + response_error);
    }
}

async function get_error(response) {
    try {
        const data = await response.json();
        return data.message;
    }
    catch (error) {
        return response.statusText;
    }
}
