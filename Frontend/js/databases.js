window.addEventListener('load', async function () {
    // Retrieve connection data from localStorage
    const connectionData = JSON.parse(localStorage.getItem("connectionData"));

    if (!connectionData) {
        alert("No connection data found. Please connect first.");
        window.location.href = "index.html"; // Redirect to the connection page
        return;
    }

    const savedDatabase = localStorage.getItem("selectedDatabase");
    const savedSchema = localStorage.getItem("selectedSchema");

    // Fetch databases and schemas
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/get-databases-and-schemas`, {

            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                account: connectionData.account,
                user: connectionData.user,
                password: connectionData.password,
                warehouse: connectionData.warehouse,
            }),
        });

        const result = await response.json();
        if (result.status === "success") {
            populateDatabaseDropdown(result.data);

            // Pre-select the saved database
            if (savedDatabase) {
                document.getElementById("database").value = savedDatabase;
                await fetchSchemas();

                // Pre-select the saved schema
                if (savedSchema) {
                    document.getElementById("schema").value = savedSchema;
                    await fetchTablesAndViews();
                }
            }
        } else {
            alert(result.message);
        }
    } catch (error) {
        alert(`An error occurred: ${error}`);

    }
});

// Populate the database dropdown
function populateDatabaseDropdown(data) {
    const databaseSelect = document.getElementById("database");
    for (const database of Object.keys(data)) {
        const option = document.createElement("option");
        option.value = database;
        option.textContent = database;
        databaseSelect.appendChild(option);
    }
}

// Fetch schemas when a database is selected
async function fetchSchemas() {
    const database = document.getElementById("database").value;
    if (!database) return;

    const connectionData = JSON.parse(localStorage.getItem("connectionData"));

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/get-databases-and-schemas`, {

            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                account: connectionData.account,
                user: connectionData.user,
                password: connectionData.password,
                warehouse: connectionData.warehouse,
            }),
        });

        const result = await response.json();
        if (result.status === "success") {
            const schemas = result.data[database] || [];
            populateSchemaDropdown(schemas);
        } else {
            alert(result.message);
        }
    } catch (error) {
        alert(`An error occurred: ${error}`);
    }
}

// Populate the schema dropdown
function populateSchemaDropdown(schemas) {
    const schemaSelect = document.getElementById("schema");
    schemaSelect.innerHTML = '<option value="">Select Schema</option>'; // Clear previous options
    schemas.forEach((schema) => {
        const option = document.createElement("option");
        option.value = schema;
        option.textContent = schema;
        schemaSelect.appendChild(option);
    });
}

// Fetch tables and views when a schema is selected
async function fetchTablesAndViews() {
    const database = document.getElementById("database").value;
    const schema = document.getElementById("schema").value;
    if (!database || !schema) return;

    const connectionData = JSON.parse(localStorage.getItem("connectionData"));

    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/get-tables-and-views-in-schema`, {

            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                account: connectionData.account,
                user: connectionData.user,
                password: connectionData.password,
                warehouse: connectionData.warehouse,
                database: database,
                schema: schema,
            }),
        });

        const result = await response.json();
        if (result.status === "success") {
            displayTablesAndViews(result.tables, result.views);
        } else {
            alert(result.message);
        }
    } catch (error) {
        alert(`An error occurred: ${error}`);

    }
}

// Display tables and views with checkboxes
function displayTablesAndViews(tables, views) {
    const container = document.getElementById("tablesContainer");
    container.innerHTML = ""; // Clear previous results

    function createCheckboxItem(type, name) {
        const checkboxDiv = document.createElement("div");
        checkboxDiv.classList.add("checkboxDiv");

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = name;
        checkbox.id = `${type}_${name}`;

        const label = document.createElement("label");
        label.setAttribute("for", `${type}_${name}`);
        label.textContent = type === "view" ? `View: ${name}` : name;

        // Create Edit button (disabled by default)
        const editBtn = document.createElement("button");
        editBtn.textContent = "Edit";
        editBtn.disabled = true; // Initially disabled
        editBtn.classList.add("edit-btn", "disabled"); // Add class for styling

        editBtn.addEventListener("click", (e) => {
            e.preventDefault();
            openEditDialog(type, name);
        });

        // Enable/Disable Edit button based on checkbox status
        checkbox.addEventListener("change", function () {
            if (this.checked) {
                editBtn.disabled = false;
                editBtn.classList.remove("disabled"); // Remove disabled style
            } else {
                editBtn.disabled = true;
                editBtn.classList.add("disabled"); // Apply disabled style
            }
        });

        checkboxDiv.appendChild(checkbox);
        checkboxDiv.appendChild(label);
        checkboxDiv.appendChild(editBtn);
        container.appendChild(checkboxDiv);
    }

    // Create checkboxes for tables
    tables.forEach((table) => createCheckboxItem("table", table));

    // Create checkboxes for views
    views.forEach((view) => createCheckboxItem("view", view));

    // Add Create Views button
    const createButton = document.createElement("button");
    createButton.textContent = "Create Views in SSMS";
    createButton.addEventListener("click", () => {
        const selectedViews = getSelectedViews();
        const selectedTables = getSelectedTables();

        // Gather edited details stored in a global variable
        const editedViews = {};
        selectedViews.forEach((view) => {
            if (editedObjects["view_" + view]) {
                editedViews[view] = editedObjects["view_" + view];
            }
        });
        const editedTables = {};
        selectedTables.forEach((table) => {
            if (editedObjects["table_" + table]) {
                editedTables[table] = editedObjects["table_" + table];
            }
        });

        localStorage.setItem("selectedViews", JSON.stringify(selectedViews));
        localStorage.setItem("selectedTables", JSON.stringify(selectedTables));
        localStorage.setItem("editedViews", JSON.stringify(editedViews));
        localStorage.setItem("editedTables", JSON.stringify(editedTables));

        // Navigate to SSMS connection page
        window.location.href = "ssms_connection.html";
    });
    container.appendChild(createButton);
}



// Get selected views
function getSelectedViews() {
    const selectedViews = [];
    const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    checkboxes.forEach((checkbox) => {
        if (checkbox.id.startsWith("view_")) {
            selectedViews.push(checkbox.value);
        }
    });
    return selectedViews;
}

// Get selected tables
function getSelectedTables() {
    const selectedTables = [];
    const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked');
    checkboxes.forEach((checkbox) => {
        if (checkbox.id.startsWith("table_")) {
            selectedTables.push(checkbox.value);
        }
    });
    return selectedTables;
}

// Listen for changes in the dropdowns
document.getElementById("database").addEventListener("change", function () {
    const selectedDatabase = this.value;
    localStorage.setItem("selectedDatabase", selectedDatabase);
    fetchSchemas();
});

document.getElementById("schema").addEventListener("change", function () {
    const selectedSchema = this.value;
    localStorage.setItem("selectedSchema", selectedSchema);
    fetchTablesAndViews();
});

// Global object to store edited details
let editedObjects = {};

// Function to open the edit dialog for a view/table
function openEditDialog(objectType, objectName) {
    // Get connection data, database, and schema for the API call
    const connectionData = JSON.parse(localStorage.getItem("connectionData"));
    const database = document.getElementById("database").value;
    const schema = document.getElementById("schema").value;
    
    fetch(`${CONFIG.API_BASE_URL}/get-columns`, {

        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            account: connectionData.account,
            user: connectionData.user,
            password: connectionData.password,
            warehouse: connectionData.warehouse,
            database: database,
            schema: schema,
            object_name: objectName,
        }),
    })
    .then(response => response.json())
    .then(result => {
        if (result.status === "success") {
            showEditModal(objectType, objectName, result.columns);
        } else {
            alert(result.message);
        }
    })
    .catch(error => alert(`An error occurred: ${error}`));
}

// Function to populate and show the modal
function showEditModal(objectType, objectName, columns) {
    const modal = document.getElementById("editModal");
    document.getElementById("editObjectType").textContent = objectType;
    document.getElementById("editedObjectName").value = objectName; // default value
    // Ensure the modal is displayed first
    // modal.style.display = "block";

 

    // Populate columns: display original column name and an adjacent editable input
    const columnsContainer = document.getElementById("columnsContainer");
    columnsContainer.innerHTML = "";
    columns.forEach(col => {
        const div = document.createElement("div");
        div.style.marginBottom = "8px";

        // Create a span to display the original column name (non-editable)
        const origNameSpan = document.createElement("span");
        origNameSpan.textContent = col.name;
        origNameSpan.style.marginRight = "10px";
        origNameSpan.style.fontWeight = "bold";

        // Separator text
        // const separator = document.createTextNode(" ------ ");

        // Create an input for the user to enter the new (editable) column name
        const input = document.createElement("input");
        input.type = "text";
        input.value = col.name; // default value is the same as original
        input.dataset.originalName = col.name;  // store original column name for reference
        input.classList.add("column-edit-input");

        // Append the elements: original name, separator, and input field
        div.appendChild(origNameSpan);
        // div.appendChild(separator);
        div.appendChild(input);
        columnsContainer.appendChild(div);
    });

    // Store current object being edited in the modal's dataset for later reference
    modal.dataset.objectType = objectType;
    modal.dataset.objectName = objectName;
    
    // Show the modal
    modal.style.display = "block";


       // Center it dynamically in case of viewport changes
    //    modal.style.left = "50%";
    //    modal.style.top = "50%";
       modal.style.transform = "translate(-50%, -50%)";
}

// Function to close the modal
function closeEditModal() {
    document.getElementById("editModal").style.display = "none";
}

// Close modal when clicking on the close icon
document.querySelector("#editModal .close").addEventListener("click", closeEditModal);

// Handle the edit form submission
document.getElementById("editForm").addEventListener("submit", function (e) {
    e.preventDefault();
    const modal = document.getElementById("editModal");
    const objectType = modal.dataset.objectType;
    const originalObjectName = modal.dataset.objectName;
    const newObjectName = document.getElementById("editedObjectName").value;

    // Build columns mapping from original name to edited value
    const columnsInputs = document.querySelectorAll(".column-edit-input");
    let columnsMapping = {};
    columnsInputs.forEach(input => {
        columnsMapping[input.dataset.originalName] = input.value;
    });

    // Save the edited details in the global object with a key like "view_originalName" or "table_originalName"
    editedObjects[objectType + "_" + originalObjectName] = {
        newName: newObjectName,
        columns: columnsMapping
    };
    console.log("editedObjects:", editedObjects);


    closeEditModal();
});

document.getElementById('replaceUnderscores').addEventListener('click', function () {
    const modal = document.getElementById("editModal");

    // Get the object type and name from modal dataset
    const objectType = modal.dataset.objectType;
    const originalObjectName = modal.dataset.objectName;

    // Update the object name (table/view name)
    let newObjectName = document.getElementById("editedObjectName").value;
    newObjectName = newObjectName.replace(/_/g, ' '); // Replace underscores
    document.getElementById("editedObjectName").value = newObjectName; // Update UI

    // Update the column names
    const columnsInputs = document.querySelectorAll(".column-edit-input");
    columnsInputs.forEach(input => {
        input.value = input.value.replace(/_/g, ' '); // Replace underscores in column names
    });

    // Update the `editedObjects` mapping with the new values
    if (editedObjects[objectType + "_" + originalObjectName]) {
        editedObjects[objectType + "_" + originalObjectName].newName = newObjectName;

        // Update column mappings in `editedObjects`
        columnsInputs.forEach(input => {
            editedObjects[objectType + "_" + originalObjectName].columns[input.dataset.originalName] = input.value;
        });
    }

    console.log("Updated editedObjects:", editedObjects);
});




