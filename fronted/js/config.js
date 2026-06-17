const IS_LOCAL = ["127.0.0.1", "localhost"].includes(window.location.hostname);
const API_URL = IS_LOCAL ? "http://127.0.0.1:8000" : `${window.location.origin}/api`;

function apiFetch(path, options = {}) {
    const token = typeof getAuthToken === "function" ? getAuthToken() : null;
    const headers = {
        ...(options.headers || {})
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    return fetch(`${API_URL}${path}`, {
        ...options,
        headers
    });
}

function resolveImageUrl(url) {
    if (!url) {
        return "";
    }

    if (url.startsWith("http") || url.startsWith("data:")) {
        return url;
    }

    return IS_LOCAL ? `${API_URL}${url}` : `${window.location.origin}${url}`;
}
