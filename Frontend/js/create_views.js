document.getElementById("connectionForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = {
        account: document.getElementById("account").value,
        user: document.getElementById("user").value,
        password: document.getElementById("password").value,
        warehouse: document.getElementById("warehouse").value,
        database: document.getElementById("database").value,
        schema: document.getElementById("schema").value,
    };

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/test_sf_vw_connection`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(formData),
        });

        const result = await response.json();
        
        // Show the result in a toast notification
        const toastMessage = result.status === "success"
            ? `Connection successful! Snowflake version: ${result.version}`
            : `Error: ${result.message}`;
        
        showToast(toastMessage, result.status);
        if (result.status === "success") {
            // Redirect to the databases page if the connection is successful
            localStorage.setItem("connectionData", JSON.stringify(formData));
            setTimeout(() => {
                window.location.href = "databases.html";  // Redirect to the next page
            }, 2000);
        }
    } catch (error) {
        showToast(`An error occurred: ${error}`, "error");
    }
});

// Function to show toast notification
function showToast(message, status) {
    const toast = document.createElement("div");
    toast.classList.add("toast", status);  // Add dynamic class for success or error
    toast.textContent = message;

    // Append the toast to the toast container
    const toastContainer = document.getElementById("toastContainer");
    toastContainer.appendChild(toast);

    // Show the toast for 3 seconds before removing it
    setTimeout(() => {
        toast.remove();
    }, 3000);
}
