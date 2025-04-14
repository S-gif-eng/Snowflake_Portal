document.getElementById("loginForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const server = document.getElementById("server").value.trim();
    const database = document.getElementById("database").value.trim();
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();
    const viewsList = document.getElementById("viewsList");
    const viewSection = document.getElementById("viewSection");
    const migrateBtn = document.getElementById("migrateViewsBtn");

    if (!server || !database || !username || !password) {
        alert("Please fill in all required fields.");
        return;
    }

    try {
        // Save credentials locally (Be careful with sensitive data)
        localStorage.setItem("server", server);
        localStorage.setItem("database", database);
        localStorage.setItem("username", username);
        localStorage.setItem("password", password);

        // Indicate loading state
        viewSection.style.display = "none";
        viewsList.innerHTML = "<p>Fetching views...</p>";
        migrateBtn.style.display = "none";

        const response = await fetch(`${CONFIG.API_BASE_URL}/get_views`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ server, database, username, password })
        });

        const data = await response.json();

        if (data.success) {
            viewSection.style.display = "block";
            viewsList.innerHTML = "";

            if (data.views.length === 0) {
                viewsList.innerHTML = "<p>No views found in the database.</p>";
                return;
            }

            data.views.forEach(view => {
                const li = document.createElement("li");
                li.innerHTML = `
                    <input type="checkbox" class="view-checkbox" value="${view}">
                    <label>${view}</label>
                `;
                viewsList.appendChild(li);
            });

            migrateBtn.style.display = "block"; // Show button when views are loaded
        } else {
            alert("Login failed! Check credentials.");
            viewsList.innerHTML = "";
        }
    } catch (error) {
        alert("Error connecting to server: " + error.message);
    }
});


document.getElementById("migrateViewsBtn").addEventListener("click", async function() {
    const selectedViews = [...document.querySelectorAll(".view-checkbox:checked")].map(cb => cb.value);
    const environment = document.getElementById("environment").value;

    if (selectedViews.length === 0) {
        alert("Please select at least one view to alter.");
        return;
    }

    // Retrieve credentials from localStorage
    const server = localStorage.getItem("server");
    const database = localStorage.getItem("database");
    const username = localStorage.getItem("username");
    const password = localStorage.getItem("password");

    if (!server || !database || !username || !password) {
        alert("Session expired. Please log in again.");
        return;
    }

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/alter_views`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ server, database, username, password, views: selectedViews, environment })
        });

        const data = await response.json();
        alert(data.message);
    } catch (error) {
        alert("Error altering views: " + error.message);
    }
});
