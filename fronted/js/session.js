const SESSION_KEY = "pinterest_session";
const LEGACY_SESSION_KEY = "pinterest_user";

function getSession() {
    const storedSession = localStorage.getItem(SESSION_KEY);
    const legacyUser = localStorage.getItem(LEGACY_SESSION_KEY);

    if (!storedSession && legacyUser) {
        try {
            return {
                user: JSON.parse(legacyUser),
                access_token: null
            };
        } catch (error) {
            localStorage.removeItem(LEGACY_SESSION_KEY);
        }
    }

    if (!storedSession) {
        return null;
    }

    try {
        return JSON.parse(storedSession);
    } catch (error) {
        localStorage.removeItem(SESSION_KEY);
        return null;
    }
}

function getCurrentUser() {
    return getSession()?.user || null;
}

function getAuthToken() {
    return getSession()?.access_token || null;
}

function setCurrentSession(data) {
    localStorage.setItem(SESSION_KEY, JSON.stringify({
        user: data.user,
        access_token: data.access_token
    }));
    localStorage.removeItem(LEGACY_SESSION_KEY);
}

function setCurrentUser(user) {
    setCurrentSession({
        user,
        access_token: getAuthToken()
    });
}

function logout() {
    localStorage.removeItem(SESSION_KEY);
    localStorage.removeItem(LEGACY_SESSION_KEY);
    window.location.href = "login.html";
}

function requireUser() {
    const user = getCurrentUser();

    if (!user || !getAuthToken()) {
        window.location.href = "login.html";
        return null;
    }

    return user;
}

function updateSessionUI() {
    const user = getCurrentUser();
    const authLinks = document.querySelectorAll("[data-auth-link]");
    const userLinks = document.querySelectorAll("[data-user-link]");
    const avatarLinks = document.querySelectorAll("[data-avatar]");
    const logoutButtons = document.querySelectorAll("[data-logout]");

    authLinks.forEach((link) => {
        link.style.display = user ? "none" : "";
    });

    userLinks.forEach((link) => {
        link.style.display = user ? "" : "none";
    });

    avatarLinks.forEach((avatar) => {
        avatar.textContent = user?.username?.charAt(0)?.toUpperCase() || "D";
    });

    logoutButtons.forEach((button) => {
        button.addEventListener("click", logout);
    });
}

document.addEventListener("DOMContentLoaded", updateSessionUI);
