const params = new URLSearchParams(window.location.search);
const pinId = params.get("id");

const image = document.getElementById("pin-image");
const title = document.getElementById("pin-title");
const description = document.getElementById("pin-description");
const authorName = document.getElementById("author-name");
const authorAvatar = document.getElementById("author-avatar");
const commentsList = document.getElementById("comments-list");
const commentForm = document.getElementById("comment-form");
const commentInput = document.getElementById("comment-input");
const savePinButton = document.getElementById("save-pin-btn");
const editPinButton = document.getElementById("edit-pin-btn");
const deletePinButton = document.getElementById("delete-pin-btn");
const detailMessage = document.getElementById("detail-message");

let currentPin = null;

function showDetailMessage(message, type = "error") {
    detailMessage.textContent = message;
    detailMessage.className = `form-message ${type}`;
}

function renderDetailError(message) {
    title.textContent = message;
    description.textContent = "Vuelve al inicio y selecciona otro pin.";
    image.removeAttribute("src");
}

function renderOwnerActions(pin) {
    const user = getCurrentUser();
    const isOwner = user && user.id === pin.user_id;

    if (editPinButton) {
        editPinButton.style.display = isOwner ? "" : "none";
    }

    if (deletePinButton) {
        deletePinButton.style.display = isOwner ? "" : "none";
    }
}

function renderComments(comments) {
    commentsList.replaceChildren();

    if (!comments.length) {
        commentsList.innerHTML = '<p class="state-message">Todavia no hay comentarios.</p>';
        return;
    }

    comments.forEach((comment) => {
        const item = document.createElement("div");
        item.className = "comment-item";
        item.innerHTML = `<strong>@${comment.username || "usuario"}:</strong> ${comment.content}`;
        commentsList.appendChild(item);
    });
}

async function loadComments() {
    const response = await apiFetch(`/pins/${pinId}/comments`);
    const comments = await response.json();

    if (!response.ok) {
        throw new Error("No se pudieron cargar los comentarios");
    }

    renderComments(comments);
}

async function loadPin() {
    if (!pinId) {
        renderDetailError("No se encontro el pin");
        return;
    }

    try {
        const response = await apiFetch(`/pins/${pinId}`);

        if (!response.ok) {
            throw new Error("Pin no encontrado");
        }

        const pin = await response.json();
        currentPin = pin;

        image.src = resolveImageUrl(pin.image_url);
        image.alt = pin.title || "Imagen del pin";
        title.textContent = pin.title || "Pin sin titulo";
        description.textContent = pin.description || "Este pin no tiene descripcion.";
        authorName.textContent = pin.username || "Usuario";
        authorAvatar.textContent = pin.username?.charAt(0)?.toUpperCase() || "U";
        authorAvatar.href = `usuario.html?id=${pin.user_id}`;
        renderOwnerActions(pin);

        await loadComments();
    } catch (error) {
        console.error(error);
        renderDetailError("No se pudo cargar este pin");
    }
}

commentForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!getCurrentUser()) {
        showDetailMessage("Inicia sesion para comentar.");
        return;
    }

    const content = commentInput.value.trim();

    if (!content) {
        showDetailMessage("Escribe un comentario.");
        return;
    }

    try {
        const response = await apiFetch(`/pins/${pinId}/comments`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ content })
        });

        const comment = await response.json();

        if (!response.ok) {
            throw new Error(comment.detail || "No se pudo comentar");
        }

        commentInput.value = "";
        showDetailMessage("Comentario publicado.", "success");
        await loadComments();
    } catch (error) {
        showDetailMessage(error.message);
    }
});

savePinButton.addEventListener("click", async () => {
    if (!getCurrentUser()) {
        showDetailMessage("Inicia sesion para guardar pines.");
        return;
    }

    try {
        const response = await apiFetch(`/pins/${pinId}/save`, {
            method: "POST"
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || "No se pudo guardar el pin");
        }

        showDetailMessage("Pin guardado en tu perfil.", "success");
    } catch (error) {
        showDetailMessage(error.message);
    }
});

if (editPinButton) {
    editPinButton.addEventListener("click", async () => {
        if (!currentPin) {
            return;
        }

        const nextTitle = window.prompt("Nuevo titulo", currentPin.title);
        const nextDescription = window.prompt("Nueva descripcion", currentPin.description);

        if (!nextTitle || !nextDescription) {
            return;
        }

        try {
            const response = await apiFetch(`/pins/${pinId}`, {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    title: nextTitle,
                    description: nextDescription
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "No se pudo editar el pin");
            }

            showDetailMessage("Pin editado correctamente.", "success");
            await loadPin();
        } catch (error) {
            showDetailMessage(error.message);
        }
    });
}

if (deletePinButton) {
    deletePinButton.addEventListener("click", async () => {
        if (!window.confirm("Seguro que quieres borrar este pin?")) {
            return;
        }

        try {
            const response = await apiFetch(`/pins/${pinId}`, {
                method: "DELETE"
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || "No se pudo borrar el pin");
            }

            window.location.href = "index.html";
        } catch (error) {
            showDetailMessage(error.message);
        }
    });
}

loadPin();
