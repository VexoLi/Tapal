document.addEventListener("DOMContentLoaded", () => {
  const darkModeButton = document.getElementById("toggleDarkMode");
  const chatSidebar = document.querySelector(".chat-sidebar");
  const chatWindow = document.querySelector(".chat-window");
  const logoutButton = document.getElementById("logoutButton");
  const backArrowButton = document.querySelector(".back-arrow");
  const friendsList = document.getElementById("friendsList");
  const groupsList = document.getElementById("groupsList");
  const backButton = document.querySelector(".back-button");

  /* ----- Modo oscuro ----- */
  function toggleDarkMode() {
    document.body.classList.toggle("dark-mode");
    sessionStorage.setItem(
      "darkMode",
      document.body.classList.contains("dark-mode") ? "enabled" : "disabled"
    );
  }

  if (darkModeButton) {
    darkModeButton.addEventListener("click", (event) => {
      event.preventDefault(); // Evita que el enlace navegue
      toggleDarkMode();
    });

    if (sessionStorage.getItem("darkMode") === "enabled") {
      document.body.classList.add("dark-mode");
    }
  } else {
    console.warn("⚠️ toggleDarkMode no encontrado en el DOM");
  }

  /* ----- Mostrar sidebar en móvil ----- */
  const menuToggle = document.querySelector(".menu-toggle");
  if (menuToggle) {
    menuToggle.addEventListener("click", () => {
      chatSidebar.classList.add("show");
      chatWindow.classList.add("hidden");
      backArrowButton.classList.remove("hidden");
    });
  }

  /* ----- Regresar al chat desde el sidebar ----- */
  if (backArrowButton) {
    backArrowButton.addEventListener("click", () => {
      chatSidebar.classList.add("show");
      chatWindow.classList.add("hidden");
      backArrowButton.classList.add("hidden");
    });
  }

  /* ----- Ajustar layout y visibilidad del botón según tamaño de pantalla ----- */
  function toggleLayout() {
    if (window.innerWidth > 768) {
      chatSidebar.classList.remove("show");
      chatWindow.classList.remove("hidden");
      backArrowButton?.classList.add("hidden");
    } else {
      chatSidebar.classList.add("show");
      chatWindow.classList.add("hidden");
      backArrowButton?.classList.remove("hidden");
    }
  }

  toggleLayout();
  window.addEventListener("resize", toggleLayout);

  /* ----- Mostrar chat al hacer clic en un chat ----- */
  function handleChatClick(event) {
    chatSidebar.classList.remove("show");
    chatWindow.classList.remove("hidden");
    backArrowButton?.classList.remove("hidden");

    // Opcional: Actualiza el título del chat seleccionado
    const chatTitle = document.getElementById("chatTitle");
    if (chatTitle) {
      chatTitle.textContent = event.currentTarget.textContent.trim();
    }
  }

  // Añadir eventos de clic a cada chat en ambas listas
  function addChatClickEvents() {
    const chatItems = document.querySelectorAll(
      ".amigos-lista li, .grupos-lista li"
    );
    chatItems.forEach((chatItem) => {
      chatItem.addEventListener("click", handleChatClick);
    });
  }

  addChatClickEvents(); // Llama a esta función para agregar eventos a los elementos de la lista

  /* ----- Logout ----- */
  if (logoutButton) {
    logoutButton.addEventListener("click", () => {
      sessionStorage.removeItem("token");
      console.log("Logout realizado");
    });
  }

  if (backButton) {
    backButton.addEventListener("click", () => {
      chatSidebar.classList.add("show");
      chatWindow.classList.add("hidden");
    });
  }
});