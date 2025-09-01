document.addEventListener("DOMContentLoaded", function () {
  const loginForm = document.getElementById("loginForm");
  const loginMessage = document.getElementById("loginMessage");

  loginForm.addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    // Clear previous messages
    loginMessage.textContent = "";
    loginMessage.className = "message";

    try {
      // Send login request
      const response = await fetch("/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({
          username: username,
          password: password,
        }),
        credentials: "include", // Include cookies in the request
      });

      const data = await response.json();

      if (response.ok) {
        // Show success message
        loginMessage.textContent = "Login successful! Redirecting...";
        loginMessage.classList.add("success");

        // Redirect to dashboard
        setTimeout(() => {
          window.location.href = "/dashboard";
        }, 1000);
      } else {
        // Show error message
        loginMessage.textContent =
          data.detail || "Login failed. Please try again.";
        loginMessage.classList.add("error");
      }
    } catch (error) {
      console.error("Login error:", error);
      loginMessage.textContent = "An error occurred. Please try again later.";
      loginMessage.classList.add("error");
    }
  });
});
