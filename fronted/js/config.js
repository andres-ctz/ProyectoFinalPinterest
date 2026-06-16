const API_URL = "http://127.0.0.1:8000";

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

    return `${API_URL}${url}`;
}
