const pinsContainer = document.getElementById("pins-container");
const searchInput = document.querySelector(".search-bar input");

function renderState(message) {
    pinsContainer.innerHTML = `<p class="state-message">${message}</p>`;
}

function createPinCard(pin) {
    const card = document.createElement("article");
    card.className = "pin-card";

    const link = document.createElement("a");
    link.href = `detalle.html?id=${pin.id}`;
    link.setAttribute("aria-label", `Ver detalle de ${pin.title}`);

    const image = document.createElement("img");
    image.src = resolveImageUrl(pin.image_url);
    image.alt = pin.title || "Imagen del pin";
    image.loading = "lazy";

    const overlay = document.createElement("div");
    overlay.className = "pin-overlay";

    const title = document.createElement("span");
    title.textContent = pin.title || "Ver pin";

    const save = document.createElement("button");
    save.className = "btn btn-save";
    save.type = "button";
    save.textContent = "Guardar";
    save.addEventListener("click", async (event) => {
        event.preventDefault();
        event.stopPropagation();

        const user = getCurrentUser();

        if (!user) {
            save.textContent = "Inicia sesion";
            return;
        }

        try {
            const response = await apiFetch(`/pins/${pin.id}/save`, {
                method: "POST"
            });

            if (!response.ok) {
                throw new Error("No se pudo guardar el pin");
            }

            save.textContent = "Guardado";
        } catch (error) {
            console.error(error);
            save.textContent = "Error";
        }
    });

    overlay.append(title, save);
    link.appendChild(image);
    card.append(link, overlay);

    return card;
}

async function loadPins(query = "") {
    try {
        renderState("Cargando pines...");

        const search = query ? `?q=${encodeURIComponent(query)}` : "";
        const response = await apiFetch(`/pins${search}`);

        if (!response.ok) {
            throw new Error("No se pudieron cargar los pines");
        }

        const pins = await response.json();
        pinsContainer.replaceChildren();

        if (!pins.length) {
            renderState("Todavia no hay pines para mostrar.");
            return;
        }

        pins.forEach((pin) => {
            pinsContainer.appendChild(createPinCard(pin));
        });
    } catch (error) {
        console.error(error);
        renderState("No se pudo conectar con la API. Revisa que el backend este encendido.");
    }
}

if (searchInput) {
    searchInput.addEventListener("input", () => {
        loadPins(searchInput.value.trim());
    });
}

loadPins();
