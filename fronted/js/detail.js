/*parte del cris*/.const params =
    new URLSearchParams(
        window.location.search
    );

const pinId =
    params.get("id");

const image =
    document.getElementById(
        "pin-image"
    );

const title =
    document.getElementById(
        "pin-title"
    );

const description =
    document.getElementById(
        "pin-description"
    );

async function loadPin() {

    const response =
        await fetch(
            `${API_URL}/pins/${pinId}`
        );

    const pin =
        await response.json();

    image.src =
        pin.image_url;

    title.textContent =
        pin.title;

    description.textContent =
        pin.description;

}

loadPin();