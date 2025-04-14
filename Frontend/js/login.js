document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const account = document.getElementById("account").value;
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const spinner = document.getElementById("spinner");
    const errorMessage = document.getElementById("error-message");

    spinner.classList.remove("hidden");
    errorMessage.classList.add("hidden");

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ account, username, password }),
        });

        const data = await response.json();

        if (response.ok) {
            // Store credentials in localStorage
            localStorage.setItem("account", account);
            localStorage.setItem("username", username);
            localStorage.setItem("password", password);

            // Redirect to home page
            window.location.href = "home.html";
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        errorMessage.textContent = error.message;
        errorMessage.classList.remove("hidden");
    } finally {
        spinner.classList.add("hidden");
    }
});
