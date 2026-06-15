const profileParams = new URLSearchParams(window.location.search);
const currentSessionUser = getCurrentUser();
const profileId = profileParams.get("id") || currentSessionUser?.id;

const profileAvatar = document.getElementById("profile-avatar");
const profileName = document.getElementById("profile-name");
const profileUsername = document.getElementById("profile-username");
const createdCount = document.getElementById("created-count");
const savedCount = document.getElementById("saved-count");
const profilePins = document.getElementById("profile-pins");
const tabs = document.querySelectorAll("[data-tab]");

let createdPins = [];
let savedPins = [];

function renderPinGrid(pins) {
    profilePins.replaceChildren();

    if (!pins.length) {
        profilePins.innerHTML = '<p class="state-message">No hay pines para mostrar.</p>';
        return;
    }

    pins.forEach((pin) => {
        const card = document.createElement("article");
        card.className = "pin-card";
        card.innerHTML = `
            <a href="detalle.html?id=${pin.id}">
                <img src="${pin.image_url}" alt="${pin.title || "Pin"}" loading="lazy">
            </a>
            <div class="pin-overlay"><span>${pin.title || "Ver pin"}</span></div>
        `;
        profilePins.appendChild(card);
    });
}

function activateTab(tabName) {
    tabs.forEach((tab) => {
        tab.classList.toggle("active", tab.dataset.tab === tabName);
    });

    renderPinGrid(tabName === "saved" ? savedPins : createdPins);
}

async function loadProfile() {
    if (!profileId) {
        profileName.textContent = "Inicia sesion";
        profileUsername.textContent = "Necesitas una cuenta para ver tu perfil.";
        profilePins.innerHTML = '<p class="state-message">Inicia sesion para ver tus pines.</p>';
        return;
    }

    try {
        const [userResponse, createdResponse, savedResponse] = await Promise.all([
            apiFetch(`/users/${profileId}`),
            apiFetch(`/users/${profileId}/pins`),
            apiFetch(`/users/${profileId}/saved`)
        ]);

        const user = await userResponse.json();
        createdPins = await createdResponse.json();
        savedPins = await savedResponse.json();

        if (!userResponse.ok) {
            throw new Error(user.detail || "No se pudo cargar el usuario");
        }

        profileAvatar.textContent = user.username?.charAt(0)?.toUpperCase() || "U";
        profileName.textContent = user.username;
        profileUsername.textContent = `@${user.username}`;
        createdCount.textContent = createdPins.length;
        savedCount.textContent = savedPins.length;
        renderPinGrid(createdPins);
    } catch (error) {
        profileName.textContent = "Perfil no disponible";
        profileUsername.textContent = error.message;
        profilePins.innerHTML = '<p class="state-message">No se pudo cargar este perfil.</p>';
    }
}

tabs.forEach((tab) => {
    tab.addEventListener("click", () => activateTab(tab.dataset.tab));
});

loadProfile();
