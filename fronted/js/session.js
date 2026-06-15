const SESSION_KEY = "pinterest_user";

function getCurrentUser() {
    const storedUser = localStorage.getItem(SESSION_KEY);

    if (!storedUser) {
        return null;
    }

    try {
        return JSON.parse(storedUser);
    } catch (error) {
        localStorage.removeItem(SESSION_KEY);
        return null;
    }
}

function setCurrentUser(user) {
    localStorage.setItem(SESSION_KEY, JSON.stringify(user));
}

function logout() {
    localStorage.removeItem(SESSION_KEY);
    window.location.href = "login.html";
}

function requireUser() {
    const user = getCurrentUser();

    if (!user) {
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
