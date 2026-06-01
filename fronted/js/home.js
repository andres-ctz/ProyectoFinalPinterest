/*parte el lucho*/
console.log("Cargando pins...");
const pinsContainer =
    document.getElementById(
        "pins-container"
    );

async function loadPins() {
    console.log("loadPins ejecutado");

    const response =
        await fetch(
            `${API_URL}/pins`
        );

    const pins =
        await response.json();

    pinsContainer.replaceChildren();

    pins.forEach(pin => {

        const card =
            document.createElement(
                "div"
            );

        card.className =
            "pin-card";

        const link =
            document.createElement(
                "a"
            );

        link.href =
            `detalle.html?id=${pin.id}`;

        const image =
            document.createElement(
                "img"
            );

        image.src =
            pin.image_url;

        image.alt =
            pin.title;

        link.appendChild(
            image
        );

        card.appendChild(
            link
        );

        pinsContainer.appendChild(
            card
        );

    });

}

loadPins();