document.addEventListener("DOMContentLoaded", async () => {
    try {
        await fetchRoles(); // Fetch roles from Snowflake and populate the dropdown

        // Initialize Select2 for role dropdown
        $('#role-name').select2();

        // Form submission
        document.getElementById("create-user-form").addEventListener("submit", async e => {
            e.preventDefault();
        
            const userName = document.getElementById("user-name").value;
            const userPassword = document.getElementById("user-password").value;
            const roleName = document.getElementById("role-name").value;
            const userEmail = document.getElementById("user-email").value;
        
            // Retrieve Snowflake credentials from localStorage
            const account = localStorage.getItem("account");
            const username = localStorage.getItem("username");
            const password = localStorage.getItem("password");
        
            if (!account || !username || !password) {
                console.error("Missing Snowflake credentials");
                alert("Missing credentials, please log in again.");
                return;
            }
        
            try {
                const spinner = document.getElementById("spinner");
                spinner.classList.remove("hidden");
        
                const response = await fetch(`${CONFIG.API_BASE_URL}/create_user`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        account: account, // Include Snowflake credentials
                        username: username,
                        password: password,
                        user_name: userName,
                        user_password: userPassword,
                        role_name: roleName,
                        email: userEmail
                    }),
                });
        
                const data = await response.json();
        
                if (!response.ok) {
                    throw new Error(data.error || "Failed to create user");
                }
        
                alert(data.message);
                window.location.href = "home.html";
            } catch (error) {
                const errorMessage = document.getElementById("error-message");
                errorMessage.textContent = error.message;
                errorMessage.classList.remove("hidden");
            } finally {
                document.getElementById("spinner").classList.add("hidden");
            }
        });
        
    } catch (error) {
        console.error("Error initializing the page:", error);
    }
});

async function fetchRoles() {
    const account = localStorage.getItem("account");
    const username = localStorage.getItem("username");
    const password = localStorage.getItem("password");

    if (!account || !username || !password) {
        console.error("Missing credentials");
        return;
    }

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/get_roles`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ account, username, password }),
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch roles: ${response.statusText}`);
        }

        const { roles } = await response.json();
        const dropdown = document.getElementById("role-name");

        // Clear existing options
        dropdown.innerHTML = '<option value="">Select a role</option>';

        // Populate roles dynamically
        roles.forEach(role => {
            const option = document.createElement("option");
            option.value = role;
            option.textContent = role;
            dropdown.appendChild(option);
        });
    } catch (error) {
        console.error("Error fetching roles:", error);
        const errorMessage = document.getElementById("error-message");
        errorMessage.textContent = "Failed to load roles. Please try again.";
        errorMessage.classList.remove("hidden");
    }
}
