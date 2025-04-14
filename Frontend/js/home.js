document.addEventListener("DOMContentLoaded", async () => {
    // const userRoleSpan = document.getElementById("user-role");

    // Retrieve credentials from localStorage
    // const account = localStorage.getItem("account");
    // const username = localStorage.getItem("username");
    // const password = localStorage.getItem("password");

    // Check if credentials are available
    // if (!account || !username || !password) {
    //     userRoleSpan.textContent = "Credentials not found! Please log in again.";
    //     console.error("Credentials are missing.");
    //     return;
    // }

    // // Fetch roles from the Snowflake API
    // try {
    //     const response = await fetch(`${CONFIG.API_BASE_URL}/api/snowflake/get_User_role`, {
    //         method: "POST",
    //         headers: {
    //             "Content-Type": "application/json",
    //         },
    //         body: JSON.stringify({ account, username, password }),
    //     });

    //     const data = await response.json();

    //     if (response.ok) {
    //         // Display roles in a list format
    //         const rolesList = document.getElementById("roles-list");
    //         rolesList.innerHTML = ""; // Clear any previous roles
    //         data.roles.forEach(role => {
    //             const roleItem = document.createElement("li");
    //             roleItem.textContent = role;
    //             rolesList.appendChild(roleItem);
    //         });

    //         console.log("Fetched Roles:", data.roles);
    //     } else {
    //         throw new Error(data.error);
    //     }
    // } catch (error) {
    //     userRoleSpan.textContent = "Error fetching roles!";
    //     console.error("Error fetching roles:", error.message);
    // }

    // Add button click handlers
    document.getElementById("create-roles").addEventListener("click", () => {
        window.location.href = "create_role.html";
    });

    document.getElementById("create-users").addEventListener("click", () => {
        window.location.href = "create_users.html";
    });

    document.getElementById("create-views").addEventListener("click", () => {
        window.location.href ="create_views.html"
    });
    document.getElementById("Migrate-views").addEventListener("click", () => {
        window.location.href ="migrate_views.html"
    });

    document.getElementById("create-database").addEventListener("click", () => {
        alert("Create Database clicked! (To be implemented)");
    });

    document.getElementById("create-warehouse").addEventListener("click", () => {
        alert("Create Warehouse clicked! (To be implemented)");
    });
});
