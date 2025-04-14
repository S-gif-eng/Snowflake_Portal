document.addEventListener("DOMContentLoaded", async () => {
    try {
        await fetchPrivileges();
        await fetchRoles();

        // Initialize Select2 for all new dropdowns
        $('.privilege-dropdown').select2();
    } catch (error) {
        console.error("Error initializing the page:", error);
    }
});

async function fetchPrivileges() {
    const account = localStorage.getItem("account");
    const username = localStorage.getItem("username");
    const password = localStorage.getItem("password");

    if (!account || !username || !password) {
        console.error("Missing credentials");
        const errorMessage = document.getElementById("error-message");
        errorMessage.textContent = "Missing credentials, please log in again.";
        errorMessage.classList.remove("hidden");
        return;
    }

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/get_privileges`, {
            method: "POST", // Use POST to pass credentials in the request body
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ account, username, password }), // Send credentials in the body
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch privileges: ${response.statusText}`);
        }

        const { privileges } = await response.json();
        const container = document.getElementById("privileges-dropdowns");

        const privilegeCategories = {
            'Database Privileges': ['OWNERSHIP', 'USAGE', 'CREATE SCHEMA', 'CREATE DATABASE', 'MODIFY', 'MONITOR'],
            'Schema Privileges': ['OWNERSHIP', 'USAGE', 'CREATE TABLE', 'CREATE VIEW', 'CREATE PROCEDURE', 'CREATE FUNCTION'],
            'Table/View Privileges': ['OWNERSHIP', 'USAGE', 'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'REFERENCES', 'TRUNCATE', 'ALTER'],
            'Warehouse Privileges': ['OWNERSHIP', 'USAGE', 'MONITOR'],
            'Resource Monitor Privileges': ['OWNERSHIP', 'USAGE'],
            'Role Privileges': ['GRANT ROLE', 'ROLE ADMIN'],
        };

        for (const [category, privilegesList] of Object.entries(privilegeCategories)) {
            const categorySection = document.createElement("div");
            const categoryLabel = document.createElement("h3");
            categoryLabel.textContent = category;
            categorySection.appendChild(categoryLabel);

            const select = document.createElement("select");
            select.classList.add("privilege-dropdown");
            select.id = `privilege-${category}`;

            privilegesList.forEach(privilege => {
                const option = document.createElement("option");
                option.value = privilege;
                option.textContent = privilege;
                select.appendChild(option);
            });

            categorySection.appendChild(select);
            container.appendChild(categorySection);
        }

    } catch (error) {
        console.error("Error fetching privileges:", error);
        const errorMessage = document.getElementById("error-message");
        errorMessage.textContent = "Failed to load privileges. Please try again.";
        errorMessage.classList.remove("hidden");
    }
}

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
        const dropdown = document.getElementById("granted-to-role");

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

document.getElementById("create-role-form").addEventListener("submit", async e => {
    e.preventDefault();

    const roleName = document.getElementById("role-name").value;
    const privileges = Array.from(
        document.querySelectorAll(".privilege-dropdown")
    ).map(select => select.selectedOptions).flat().map(option => option.value); // Collect selected privileges

    const grantedToRole = document.getElementById("granted-to-role").value;

    // Get Snowflake credentials from localStorage
    const account = localStorage.getItem("account");
    const username = localStorage.getItem("username");
    const password = localStorage.getItem("password");

    if (!account || !username || !password) {
        alert("Missing credentials, please log in again.");
        return;
    }

    try {
        const spinner = document.getElementById("spinner");
        spinner.classList.remove("hidden");

        const response = await fetch(`${CONFIG.API_BASE_URL}/create_role`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                role_name: roleName, 
                privileges, 
                granted_to_role: grantedToRole,
                account,
                username,
                password
            }),
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Failed to create role");
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
