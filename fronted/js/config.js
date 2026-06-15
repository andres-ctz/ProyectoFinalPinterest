const API_URL = "http://127.0.0.1:8000";

function apiFetch(path, options = {}) {
    return fetch(`${API_URL}${path}`, options);
}
