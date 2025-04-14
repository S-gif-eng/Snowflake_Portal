document.getElementById('ssmsForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent form submission

    const ssmsServer = document.getElementById('ssmsServer').value;
    const ssmsDatabase = document.getElementById('ssmsDatabase').value;
    const ssmsUsername = document.getElementById('ssmsUsername').value;
    const ssmsPassword = document.getElementById('ssmsPassword').value;
    const linkedServer = document.getElementById('linkedServer').value;

    if (!ssmsServer || !ssmsDatabase || !ssmsUsername || !ssmsPassword || !linkedServer) {
        alert('Please fill out all fields.');
        return;
    }

    // Test SSMS connection
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/test-ssms-connection`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                server: ssmsServer,
                database: ssmsDatabase,
                username: ssmsUsername,
                password: ssmsPassword,
            }),
        });

        const result = await response.json();
        if (result.status === "success") {
            document.getElementById('connectionResult').textContent = "Connection Successful!";
            document.getElementById('createViewsBtn').style.display = "inline-block"; // Show the create views button
        } else {
            document.getElementById('connectionResult').textContent = "Connection Failed: " + result.message;
        }
    } catch (error) {
        alert(`An error occurred: ${error}`);
    }
});

document.getElementById('createViewsBtn').addEventListener('click', async function() {
    const ssmsServer = document.getElementById('ssmsServer').value;
    const ssmsDatabase = document.getElementById('ssmsDatabase').value;
    const ssmsUsername = document.getElementById('ssmsUsername').value;
    const ssmsPassword = document.getElementById('ssmsPassword').value;
    const linkedServer = document.getElementById('linkedServer').value;

    const selectedViews = JSON.parse(localStorage.getItem("selectedViews"));
    const selectedTables = JSON.parse(localStorage.getItem("selectedTables"));
    const selectedDatabase = localStorage.getItem("selectedDatabase"); // Retrieve the selected database
    const selectedSchema = localStorage.getItem("selectedSchema"); // Retrieve the selected schema

    // Retrieve the edited column and object details from localStorage
    const editedViews = JSON.parse(localStorage.getItem("editedViews"));
    const editedTables = JSON.parse(localStorage.getItem("editedTables"));

    if (!linkedServer) {
        alert("Linked Server field is required.");
        return;
    }

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/create-views-in-ssms`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                server: ssmsServer,
                database: ssmsDatabase,
                username: ssmsUsername,
                password: ssmsPassword,
                linkedServer: linkedServer, // Include linked server in the payload
                selectedViews: selectedViews,
                selectedTables: selectedTables,
                sourceDatabase: selectedDatabase, // Include the source database
                sourceSchema: selectedSchema, // Include the source schema
                editedViews: editedViews,  // Newly added: contains new view name and columns mapping
                editedTables: editedTables // Newly added: contains new table name and columns mapping
            }),
        });

        const result = await response.json();
        if (result.status === "success") {
            alert("Views created successfully in SSMS!");
        } else {
            alert("Error: " + result.message);
        }
    } catch (error) {
        alert("Error: " + error);
    }
});
