document.addEventListener("DOMContentLoaded", () => {
  const loginForm = document.getElementById("form");

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault(); // Evita que la página se recargue

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
      const response = await fetch("http://127.0.0.1:8000/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        // 🚀 Guarda el token en localStorage correctamente
        localStorage.setItem("token", data.access_token);
        console.log(
          "✅ Token guardado en localStorage:",
          localStorage.getItem("token")
        );

        // Redirigir al usuario a la página de chats
        window.location.href = "chats.html";
      } else {
        console.error("❌ Error de autenticación:", data.detail);
        alert("Error de autenticación: " + data.detail);
      }
    } catch (error) {
      console.error("❌ Error en la solicitud:", error);
    }
  });
});
