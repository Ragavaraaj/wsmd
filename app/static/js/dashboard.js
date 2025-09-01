document.addEventListener("DOMContentLoaded", function () {
  // Get user information from the server-rendered template
  const isKeyUser =
    document.getElementById("currentUser").dataset.isKeyUser === "true";

  // Update UI based on user role
  updateUIForUserRole(isKeyUser);

  // Logout button
  document.getElementById("logoutBtn").addEventListener("click", function () {
    // Send logout request to server
    fetch("/logout", {
      method: "POST",
    }).then(() => {
      // Redirect to login page
      window.location.href = "/login";
    });
  });

  // Form submission handlers
  setupFormHandlers();

  // Setup Server-Sent Events for real-time updates
  setupEventSource();
});

function updateUIForUserRole(isKeyUser) {
  // Show or hide key user specific elements
  const keyUserElements = document.querySelectorAll(".key-user-only");
  keyUserElements.forEach((elem) => {
    elem.style.display = isKeyUser ? "block" : "none";
  });
}

async function loadDevices() {
  try {
    const response = await fetchWithAuth("/admin/devices");
    if (response.ok) {
      const devices = await response.json();
      populateDeviceTable(devices);
      updateDeviceDropdowns(devices);
    }
  } catch (error) {
    console.error("Error loading devices:", error);
  }
}

async function loadUsers() {
  try {
    const response = await fetchWithAuth("/admin/users");
    if (response.ok) {
      const users = await response.json();
      populateUserDropdown(users);
    }
  } catch (error) {
    console.error("Error loading users:", error);
  }
}

function populateDeviceTable(devices) {
  const tableBody = document.getElementById("deviceTableBody");
  tableBody.innerHTML = "";

  devices.forEach((device) => {
    const row = document.createElement("tr");

    // Highlight row if hit counter exceeds max hits
    if (device.hit_counter > device.max_hits) {
      row.classList.add("warning");
    }

    row.innerHTML = `
            <td>${device.name || device.mac_address}</td>
            <td>${device.order}</td>
            <td>${device.hit_counter}</td>
            <td>${device.max_hits}</td>
            <td>
                <button class="edit-device" data-mac="${device.mac_address}" 
                  data-order="${device.order}" data-max="${device.max_hits}" 
                  data-name="${device.name || ""}">
                    Edit Device
                </button>
            </td>
        `;

    tableBody.appendChild(row);
  });

  // Add event listeners to the edit buttons
  document.querySelectorAll(".edit-device").forEach((btn) => {
    btn.addEventListener("click", function () {
      const mac = this.getAttribute("data-mac");
      const order = this.getAttribute("data-order");
      const maxHits = this.getAttribute("data-max");
      const name = this.getAttribute("data-name");

      document.getElementById("deviceMac").value = mac;
      document.getElementById("deviceOrder").value = order;
      document.getElementById("deviceMaxHits").value = maxHits;
      document.getElementById("deviceName").value = name;
    });
  });
}

function updateDeviceDropdowns(devices) {
  const deviceSelect = document.getElementById("deviceMac");

  // Clear existing options except the first one
  deviceSelect.innerHTML = '<option value="">Select Device</option>';

  // Add devices to dropdown
  devices.forEach((device) => {
    const option = document.createElement("option");
    option.value = device.mac_address;
    option.textContent = `${device.name} (Order: ${device.order}, Max Hits: ${device.max_hits})`;
    deviceSelect.appendChild(option);
  });
}

function populateUserDropdown(users) {
  const userSelect = document.getElementById("passwordUsername");

  // Clear existing options except the first one
  userSelect.innerHTML = '<option value="">Select User</option>';

  // Add users to dropdown
  users.forEach((user) => {
    const option = document.createElement("option");
    option.value = user.username;
    option.textContent = `${user.username} ${
      user.is_key_user ? "(Key User)" : ""
    }`;
    userSelect.appendChild(option);
  });
}

function setupFormHandlers() {
  // Update Device Properties Form
  document
    .getElementById("updateDeviceForm")
    .addEventListener("submit", async function (e) {
      e.preventDefault();
      const formData = new FormData(this);
      const success = await submitForm(
        "/admin/device",
        formData,
        "deviceMessage"
      );

      // Clear the form if submission was successful
      if (success) {
        this.reset();
        document.getElementById("deviceMac").value = ""; // Reset the select element
      }
      // No need to manually refresh - SSE will handle updates
    });

  // Create User Form (key users only)
  const newUserForm = document.getElementById("newUserForm");
  if (newUserForm) {
    newUserForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const formData = new FormData(this);
      // Add checkbox value properly
      const success = await submitForm(
        "/admin/user",
        formData,
        "createUserMessage"
      );

      // Clear the form if submission was successful
      if (success) {
        this.reset();
      }
      // No need to manually refresh - SSE will handle updates
    });
  }

  // Update Password Form (key users only)
  const passwordForm = document.getElementById("passwordForm");
  if (passwordForm) {
    passwordForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      const formData = new FormData(this);
      const success = await submitForm(
        "/admin/user/password",
        formData,
        "passwordMessage"
      );

      // Clear the form if submission was successful
      if (success) {
        this.reset();
        document.getElementById("passwordUsername").value = ""; // Reset the select element
      }
    });
  }
}

async function submitForm(url, formData, messageElementId) {
  const messageElement = document.getElementById(messageElementId);

  try {
    const response = await fetchWithAuth(url, {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (response.ok) {
      messageElement.textContent = data.message || "Operation successful";
      messageElement.className = "message success";
      return true; // Return true to indicate success
    } else {
      messageElement.textContent = data.detail || "Operation failed";
      messageElement.className = "message error";
      return false; // Return false to indicate failure
    }
  } catch (error) {
    console.error(`Error submitting to ${url}:`, error);
    messageElement.textContent = "An error occurred. Please try again.";
    messageElement.className = "message error";
    return false; // Return false on error
  }
}

async function fetchWithAuth(url, options = {}) {
  // We don't need to manually add the token as it's in the cookie
  // and will be automatically sent with the request

  const response = await fetch(url, {
    ...options,
    credentials: "include", // Include cookies in the request
  });

  // Handle unauthorized response (expired token)
  if (response.status === 401) {
    window.location.href = "/login";
    throw new Error("Session expired. Please log in again.");
  }

  return response;
}

// Setup Server-Sent Events for real-time updates
function setupEventSource() {
  const isKeyUser =
    document.getElementById("currentUser").dataset.isKeyUser === "true";
  let eventSource = null;

  // Update connection status
  function updateConnectionStatus(status, message) {
    const connectionStatus = document.getElementById("connectionStatus");
    connectionStatus.textContent = message;
    connectionStatus.className = `status ${status}`;
  }

  // Update last updated timestamp
  function updateTimestamp() {
    const lastUpdated = document.getElementById("lastUpdated");
    if (lastUpdated) {
      lastUpdated.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
    }
  }

  // Create a function to connect and handle reconnection
  function connect() {
    // Close existing connection if any
    if (eventSource) {
      eventSource.close();
    }

    updateConnectionStatus("connecting", "Connecting...");

    // Create a new EventSource connection
    eventSource = new EventSource("/admin/events");

    // Handle connection open
    eventSource.onopen = function () {
      console.log("SSE connection established");
      updateConnectionStatus("connected", "Connected (Live)");
    };

    // Handle device updates
    eventSource.addEventListener("devices", function (event) {
      const devices = JSON.parse(event.data);
      populateDeviceTable(devices);
      updateDeviceDropdowns(devices);
      updateTimestamp();
    });

    // Handle user updates (for key users)
    if (isKeyUser) {
      eventSource.addEventListener("users", function (event) {
        const users = JSON.parse(event.data);
        populateUserDropdown(users);
        updateTimestamp();
      });
    }

    // Handle errors and reconnect
    eventSource.onerror = function (error) {
      console.error("SSE connection error:", error);
      updateConnectionStatus("disconnected", "Disconnected");
      eventSource.close();

      // Try to reconnect after a delay
      setTimeout(connect, 5000);
    };

    // Handle heartbeat events (do nothing, just keeps connection alive)
    eventSource.addEventListener("heartbeat", function (event) {
      // Connection is alive, just update the timestamp
      updateTimestamp();
    });

    // Handle server errors
    eventSource.addEventListener("error", function (event) {
      const errorData = JSON.parse(event.data);
      console.error("Server error:", errorData.message);
      updateConnectionStatus("disconnected", "Error: " + errorData.message);
    });
  }

  // Start the connection
  connect();

  // Clean up on page unload
  window.addEventListener("beforeunload", function () {
    if (eventSource) {
      eventSource.close();
    }
  });
}
