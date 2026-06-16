const createForm = document.getElementById("create-pin-form");
const imageUrlInput = document.getElementById("image_url");
const imageFileInput = document.getElementById("image_file");
const imagePreview = document.getElementById("image-preview");
const previewPlaceholder = document.getElementById("preview-placeholder");
const createMessage = document.getElementById("create-message");

requireUser();

function showCreateMessage(message, type = "error") {
    createMessage.textContent = message;
    createMessage.className = `form-message ${type}`;
}

function setPreview(src) {
    if (!src) {
        imagePreview.removeAttribute("src");
        imagePreview.alt = "";
        previewPlaceholder.style.display = "";
        return;
    }

    imagePreview.src = src;
    imagePreview.alt = "Vista previa del pin";
    previewPlaceholder.style.display = "none";
}

imageUrlInput.addEventListener("input", () => {
    imageFileInput.value = "";
    setPreview(imageUrlInput.value.trim());
});

imageFileInput.addEventListener("change", () => {
    const file = imageFileInput.files[0];

    if (!file) {
        return;
    }

    setPreview(URL.createObjectURL(file));
    imageUrlInput.value = "";
});

createForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const title = createForm.title.value.trim();
    const description = createForm.description.value.trim();
    const file = imageFileInput.files[0];
    const imageUrl = imageUrlInput.value.trim();

    if (!file && !imageUrl) {
        showCreateMessage("Agrega una imagen con URL o archivo.");
        return;
    }

    try {
        let response;

        if (file) {
            const formData = new FormData();
            formData.append("title", title);
            formData.append("description", description);
            formData.append("image", file);

            response = await apiFetch("/pins/upload", {
                method: "POST",
                body: formData
            });
        } else {
            response = await apiFetch("/pins", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    title,
                    description,
                    image_url: imageUrl
                })
            });
        }

        const pin = await response.json();

        if (!response.ok) {
            throw new Error(pin.detail || "No se pudo crear el pin");
        }

        showCreateMessage("Pin publicado correctamente.", "success");
        window.location.href = `detalle.html?id=${pin.id}`;
    } catch (error) {
        showCreateMessage(error.message);
    }
});
