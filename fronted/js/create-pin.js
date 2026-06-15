const createForm = document.getElementById("create-pin-form");
const imageUrlInput = document.getElementById("image_url");
const imageFileInput = document.getElementById("image_file");
const imagePreview = document.getElementById("image-preview");
const previewPlaceholder = document.getElementById("preview-placeholder");
const createMessage = document.getElementById("create-message");
let uploadedImageData = "";

const currentUser = requireUser();

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
    uploadedImageData = "";
    imageFileInput.value = "";
    setPreview(imageUrlInput.value.trim());
});

imageFileInput.addEventListener("change", () => {
    const file = imageFileInput.files[0];

    if (!file) {
        return;
    }

    const reader = new FileReader();

    reader.addEventListener("load", () => {
        uploadedImageData = reader.result;
        imageUrlInput.value = "";
        setPreview(uploadedImageData);
    });

    reader.readAsDataURL(file);
});

createForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const imageUrl = uploadedImageData || imageUrlInput.value.trim();

    if (!imageUrl) {
        showCreateMessage("Agrega una imagen con URL o archivo.");
        return;
    }

    const payload = {
        title: createForm.title.value.trim(),
        description: createForm.description.value.trim(),
        image_url: imageUrl,
        user_id: currentUser.id
    };

    try {
        const response = await apiFetch("/pins", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

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
