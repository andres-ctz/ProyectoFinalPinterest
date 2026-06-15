const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const authMessage = document.getElementById("auth-message");

function showAuthMessage(message, type = "error") {
    if (!authMessage) {
        return;
    }

    authMessage.textContent = message;
    authMessage.className = `form-message ${type}`;
}

async function postAuth(endpoint, payload) {
    const response = await apiFetch(endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.detail || "No se pudo completar la accion");
    }

    return data;
}

if (registerForm) {
    registerForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = {
            email: registerForm.email.value.trim(),
            username: registerForm.username.value.trim(),
            password: registerForm.password.value
        };

        try {
            const user = await postAuth("/users/register", payload);
            setCurrentUser(user);
            showAuthMessage("Cuenta creada correctamente.", "success");
            window.location.href = "index.html";
        } catch (error) {
            showAuthMessage(error.message);
        }
    });
}

if (loginForm) {
    loginForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = {
            email: loginForm.email.value.trim(),
            password: loginForm.password.value
        };

        try {
            const data = await postAuth("/users/login", payload);

            if (!data.success) {
                showAuthMessage(data.message);
                return;
            }

            setCurrentUser(data.user);
            showAuthMessage("Sesion iniciada correctamente.", "success");
            window.location.href = "index.html";
        } catch (error) {
            showAuthMessage(error.message);
        }
    });
}
