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
        // 🚀 Guarda el token y el user_id en sessionStorage
        sessionStorage.setItem("token", data.access_token);
        sessionStorage.setItem("user_id", data.user_id); // Guardar el user_id
        console.log(
          "✅ Token guardado en sessionStorage:",
          sessionStorage.getItem("token")
        );
        console.log(
          "✅ User ID guardado en sessionStorage:",
          sessionStorage.getItem("user_id")
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
