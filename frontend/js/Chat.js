import { handleFetchErrors, showErrorMessage } from "./errorHandler.js";

// js/Chat.js
document.addEventListener("DOMContentLoaded", () => {
  // Elementos del DOM
  const friendsList = document.getElementById("friendsList");
  const groupsList = document.getElementById("groupsList");
  const chatTitle = document.getElementById("chatTitle");
  const chatMessages = document.querySelector(".chat-messages");
  const messageInput = document.getElementById("messageInput");
  const sendButton = document.getElementById("sendButton");
  const crearGrupoButton = document.getElementById("crearGrupo");
  const chatHeader = document.querySelector(".chat-header");
  const chatWindow = document.querySelector(".chat-window");
  const chatInput = document.querySelector(".chat-input");
  const sidebar = document.querySelector(".chat-sidebar");
  const settingsButton = document.getElementById("settings-button");
  const groupMenu = document.getElementById("groupMenu");
  const addAdminButton = document.getElementById("addAdmin");
  const addUserButton = document.getElementById("addUser");
  const changeGroupNameButton = document.getElementById("changeGroupName");
  const deleteChatButton = document.getElementById("deleteChat");
  const deleteGroupButton = document.getElementById("deleteGroup");
  const userSelectionModal = document.getElementById("userSelectionModal");
  const modalTitle = document.getElementById("modalTitle");
  const userList = document.getElementById("userList");
  const confirmSelectionButton = document.getElementById("confirmSelection");
  const closeModalButton = document.getElementById("closeModal");
  const removeUserButton = document.getElementById("removeUser");

  let selectedUserId = null;
  let chatRefreshInterval = null; // Almacenar el intervalo para controlarlo

  async function startChatAutoRefresh(chatId, chatType) {
    // Limpiar intervalos previos
    if (chatRefreshInterval) {
      clearInterval(chatRefreshInterval);
    }

    // Configurar la actualización cada 3 segundos
    chatRefreshInterval = setInterval(async () => {
      await fetchMessages(chatId, chatType, false); // 🔥 Llama a la función de obtener mensajes
    }, 3000);
  }

  // Obtener token y definir encabezados para fetch
  const token = sessionStorage.getItem("token") || null;
  if (!token) {
    console.warn(
      "No hay token en sessionStorage, redirigiendo a index.html..."
    );
    window.location.href = "index.html"; // Redirige a index.html
    return; // Detiene la ejecución del script si no hay token
  }

  // Variable global para guardar los amigos (para usarlos al crear un grupo)
  let globalFriends = [];

  /**
   * Obtiene la lista de amigos y grupos mediante la API,
   * renderiza cada lista y guarda los amigos en globalFriends.
   */

  async function fetchFriendsAndGroups() {
    try {
      const [friendsData, groupsData] = await Promise.all([
        fetch("http://127.0.0.1:8000/users/llistaamics", { headers }).then(
          handleFetchErrors
        ),
        fetch("http://127.0.0.1:8000/users/grups", { headers }).then(
          handleFetchErrors
        ),
      ]);

      // Guardar los amigos para usarlos en el modal de creación de grupo
      globalFriends = friendsData.friends || [];
      const groups = groupsData.groups || [];

      renderList(friendsList, globalFriends, "friend");
      renderList(groupsList, groups, "group");
    } catch (error) {
      showErrorMessage(error);
    }
  }

  /**
   * Renderiza una lista (amigos o grupos) en el elemento indicado.
   */
  function renderList(listElement, items, type) {
    listElement.innerHTML = "";
    items.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = item.username || item.name;
      li.dataset.id = item.id;
      li.dataset.type = type;
      // Al hacer clic se abre el chat correspondiente
      li.addEventListener("click", () => {
        // Quitar la clase "active" de los demás ítems
        [...listElement.children].forEach((elem) =>
          elem.classList.remove("active")
        );
        li.classList.add("active");
        openChat(item.id, type, li.textContent);
      });
      listElement.appendChild(li);
    });
  }

  /**
   * Abre el chat seleccionando el grupo o amigo,
   * actualiza el título y carga los mensajes.
   */
  async function openChat(chatId, chatType, chatName) {
    if (currentChatId === chatId) return; // 🔥 Evita resetear si ya está abierto

    // 🔥 Reiniciar variables de paginación y chat
    currentChatId = chatId;
    currentChatType = chatType;
    currentPage = 1;
    hasMoreMessages = true;
    isLoadingMessages = false;

    chatHeader.style.display = "flex";
    chatInput.style.display = "flex";
    chatTitle.textContent = chatName;
    chatTitle.dataset.id = chatId;
    chatTitle.dataset.type = chatType;

    chatMessages.innerHTML = ""; // 🔥 Borrar mensajes anteriores
    selectChatMessage.style.display = "none";

    if (chatType === "group") {
      settingsButton.style.display = "block";
    } else {
      settingsButton.style.display = "none";
    }

    await fetchMessages(chatId, chatType, false); // 🔥 Cargar mensajes iniciales
  }

  /**
   * Obtiene los mensajes del chat (de amigo o grupo) y los renderiza.
   */
  let currentChatId = null; // 🔥 Guardar el ID del chat actual
  let currentChatType = null;

  let currentPage = 1;
  let hasMoreMessages = true;
  let isLoadingMessages = false;
  let messagesPerLoad = 1000;

  async function fetchMessages(chatId, chatType, prepend = false) {
    if (isLoadingMessages || chatId !== currentChatId) return;
    isLoadingMessages = true;

    try {
      const endpoint =
        chatType === "friend"
          ? `http://127.0.0.1:8000/users/missatgesAmics?friend_id=${chatId}&page=${currentPage}&limit=${messagesPerLoad}`
          : `http://127.0.0.1:8000/users/missatgesgrup?group_id=${chatId}&page=${currentPage}&limit=${messagesPerLoad}`;

      console.log("📨 Fetching messages from:", endpoint);
      const response = await fetch(endpoint, { headers });
      if (!response.ok) throw new Error("Error al obtener mensajes");

      const data = await response.json();
      const messages = data.messages || [];
      console.log("📥 Mensajes (ASC) recibidos del backend:", messages);

      if (!messages.length) {
        hasMoreMessages = false;
        console.log("⚠️ No hay más mensajes para cargar.");
        return;
      }

      // No invertimos nada: ya vienen 1..45 en orden
      renderMessages(messages, prepend);

      if (messages.length < messagesPerLoad) {
        hasMoreMessages = false; // Ya no hay más
      } else {
        currentPage++;
      }
    } catch (err) {
      console.error("❌ Error fetchMessages:", err);
    } finally {
      isLoadingMessages = false;
    }
  }

  function renderMessages(messages, prepend = false) {
    if (!chatMessages) {
      console.error("⚠️ El contenedor chatMessages no existe en el DOM.");
      return;
    }

    if (!messages.length) {
      console.warn("⚠️ No hay mensajes para mostrar.");
      return;
    }

    // Guardamos el primer mensaje visible antes de agregar más
    const firstMessage = chatMessages.firstChild;

    // Recorremos el array del más viejo al más nuevo (que ya es ASC)
    messages.forEach((msg) => {
      const senderId = Number(msg.sender_id);
      const isSentByUser =
        senderId === Number(sessionStorage.getItem("user_id"));
      const messageDiv = document.createElement("div");
      messageDiv.classList.add("message", isSentByUser ? "sent" : "received");

      if (chatTitle.dataset.type === "group" && !isSentByUser) {
        messageDiv.innerHTML = `<strong>${msg.sender_username}</strong> <p>${msg.content}</p>`;
      } else {
        messageDiv.innerHTML = `<p>${msg.content}</p>`;
      }

      // Si prepend = false → appendChild (los mensajes se añaden abajo, final)
      // Si prepend = true → insertBefore (los mensajes se añaden arriba)
      if (prepend) {
        chatMessages.insertBefore(messageDiv, chatMessages.firstChild);
      } else {
        chatMessages.appendChild(messageDiv);
      }
    });

    // Ajustar scroll
    if (prepend && firstMessage) {
      firstMessage.scrollIntoView();
    } else {
      // Ir al final donde esté el último mensaje (más nuevo)
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }

  /**
   * Envía un mensaje (ya sea a un amigo o a un grupo).
   */
  async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;

    const chatId = parseInt(chatTitle.dataset.id, 10);
    const chatType = chatTitle.dataset.type;

    try {
      const endpoint =
        chatType === "friend"
          ? `http://127.0.0.1:8000/users/missatgesAmics?receiver_id=${chatId}&content=${encodeURIComponent(
              message
            )}`
          : `http://127.0.0.1:8000/users/missatgesgrup?group_id=${chatId}&content=${encodeURIComponent(
              message
            )}`;

      const response = await fetch(endpoint, { method: "POST", headers });
      await handleFetchErrors(response);

      const sentMessage = document.createElement("div");
      sentMessage.classList.add("message", "sent");
      sentMessage.innerHTML = `<p>${message}</p>`;
      chatMessages.appendChild(sentMessage);
      messageInput.value = "";
      chatMessages.scrollTop = chatMessages.scrollHeight;
    } catch (error) {
      showErrorMessage(error);
    }
  }

  sendButton.addEventListener("click", sendMessage);
  messageInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      sendMessage();
    }
  });

  // 🚀 Evento para detectar scroll y cargar más mensajes
  chatMessages.addEventListener("scroll", () => {
    if (chatMessages.scrollTop === 0 && hasMoreMessages && !isLoadingMessages) {
      console.log("🔄 Detectado scroll arriba, cargando más mensajes...");
      fetchMessages(currentChatId, currentChatType, true);
    }
  });

  /* =========================
     CREAR GRUPO (Popup Modal)
     ========================= */
  function openCreateGroupModal() {
    // Crea el overlay del modal
    const modalOverlay = document.createElement("div");
    modalOverlay.style.position = "fixed";
    modalOverlay.style.top = "0";
    modalOverlay.style.left = "0";
    modalOverlay.style.width = "100%";
    modalOverlay.style.height = "100%";
    modalOverlay.style.backgroundColor = "rgba(0,0,0,0.5)";
    modalOverlay.style.display = "flex";
    modalOverlay.style.alignItems = "center";
    modalOverlay.style.justifyContent = "center";
    modalOverlay.style.zIndex = "2000";

    // Crea el contenido del modal
    const modalContent = document.createElement("div");
    modalContent.style.background = "#fff";
    modalContent.style.padding = "20px";
    modalContent.style.borderRadius = "5px";
    modalContent.style.width = "300px";
    modalContent.style.maxHeight = "80%";
    modalContent.style.overflowY = "auto";

    // Título del modal
    const title = document.createElement("h2");
    title.textContent = "Crear Grupo";
    modalContent.appendChild(title);

    // Input para el nombre del grupo
    const nameLabel = document.createElement("label");
    nameLabel.textContent = "Nombre del grupo:";
    modalContent.appendChild(nameLabel);
    const groupNameInput = document.createElement("input");
    groupNameInput.type = "text";
    groupNameInput.style.width = "100%";
    groupNameInput.style.marginBottom = "10px";
    modalContent.appendChild(groupNameInput);

    // Selección de miembros (lista de checkboxes)
    const membersLabel = document.createElement("label");
    membersLabel.textContent = "Agregar miembros:";
    modalContent.appendChild(membersLabel);
    const membersContainer = document.createElement("div");
    membersContainer.style.maxHeight = "150px";
    membersContainer.style.overflowY = "auto";
    membersContainer.style.border = "1px solid #ccc";
    membersContainer.style.padding = "5px";
    membersContainer.style.marginBottom = "10px";

    // Para cada amigo disponible (guardado en globalFriends), crear un checkbox
    globalFriends.forEach((friend) => {
      const checkboxContainer = document.createElement("div");
      checkboxContainer.style.display = "flex";
      checkboxContainer.style.alignItems = "center";
      const checkbox = document.createElement("input");
      checkbox.type = "checkbox";
      checkbox.value = friend.id;
      checkbox.style.marginRight = "5px";
      const label = document.createElement("label");
      label.textContent = friend.username || friend.name;
      checkboxContainer.appendChild(checkbox);
      checkboxContainer.appendChild(label);
      membersContainer.appendChild(checkboxContainer);
    });
    modalContent.appendChild(membersContainer);

    // Contenedor de botones (Cancelar y Crear)
    const buttonsContainer = document.createElement("div");
    buttonsContainer.style.display = "flex";
    buttonsContainer.style.justifyContent = "flex-end";
    buttonsContainer.style.gap = "10px";

    // Botón Cancelar: cierra el modal
    const cancelButton = document.createElement("button");
    cancelButton.textContent = "Cancelar";
    cancelButton.addEventListener("click", () => {
      document.body.removeChild(modalOverlay);
    });
    buttonsContainer.appendChild(cancelButton);

    // Botón Crear: envía la solicitud para crear el grupo
    const createButton = document.createElement("button");
    createButton.textContent = "Crear";
    createButton.addEventListener("click", async () => {
      const groupName = groupNameInput.value.trim();
      if (!groupName) {
        alert("Por favor, ingresa un nombre para el grupo.");
        return;
      }
      // Obtiene los ids de los amigos seleccionados
      const selectedIds = [];
      const checkboxes = membersContainer.querySelectorAll(
        "input[type='checkbox']"
      );
      checkboxes.forEach((checkbox) => {
        if (checkbox.checked) {
          selectedIds.push(checkbox.value);
        }
      });
      try {
        await createGroup(groupName, selectedIds);
        alert("Grupo creado con éxito.");
        document.body.removeChild(modalOverlay);
        // Actualiza la lista de grupos luego de la creación
        fetchFriendsAndGroups();
      } catch (error) {
        console.error("Error creating group:", error);
        alert("Error al crear el grupo. Inténtalo de nuevo.");
      }
    });
    buttonsContainer.appendChild(createButton);
    modalContent.appendChild(buttonsContainer);

    modalOverlay.appendChild(modalContent);
    document.body.appendChild(modalOverlay);
  }

  async function addUsersToGroup(groupId, members) {
    try {
      for (const memberId of members) {
        const response = await fetch(
          `http://127.0.0.1:8000/users/grups/${groupId}/agregar-usuario?nuevo_miembro_id=${memberId}`,
          {
            method: "POST",
            headers,
          }
        );
        await handleFetchErrors(response);
      }
    } catch (error) {
      showErrorMessage(error);
    }
  }

  /**
   * Envía la solicitud para crear un grupo y, en caso de haber miembros seleccionados,
   * los agrega al grupo.
   * @param {string} groupName - Nombre del grupo.
   * @param {array} members - Array con los ids de los amigos seleccionados.
   */
  async function createGroup(groupName, members) {
    try {
      const url = `http://127.0.0.1:8000/users/grups?nombre=${encodeURIComponent(
        groupName
      )}`;
      const response = await fetch(url, { method: "POST", headers });
      const groupData = await handleFetchErrors(response);

      const groupId = groupData.id || groupData.group_id;
      if (!groupId) {
        throw new Error("No se recibió el ID del grupo creado");
      }

      await addUsersToGroup(groupId, members);
      return groupData;
    } catch (error) {
      showErrorMessage(error);
    }
  }

  // Asigna el evento al botón "Crear grupo" si existe en el DOM
  if (crearGrupoButton) {
    crearGrupoButton.addEventListener("click", (e) => {
      e.preventDefault();
      openCreateGroupModal();
    });
  }

  // Headers para las peticiones a la API
  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };

  // Función de logout actualizada para SessionStorage
  function logout() {
    sessionStorage.removeItem("token");
    sessionStorage.removeItem("user_id");

    // Redirigir a la página de inicio de sesión
    window.location.href = "index.html";
  }

  // Agregar el evento al botón de logout
  const logoutButton = document.getElementById("logoutButton");
  if (logoutButton) {
    logoutButton.addEventListener("click", (e) => {
      e.preventDefault();
      logout();
    });
  }

  // Obtener la barra de búsqueda del DOM
  const searchBar = document.querySelector(".search-bar");

  // Función para filtrar chats
  function filterChats() {
    const searchText = searchBar.value.toLowerCase();

    // Filtrar amigos
    const friendItems = document.querySelectorAll("#friendsList li");
    friendItems.forEach((item) => {
      const name = item.textContent.toLowerCase();
      item.style.display = name.includes(searchText) ? "block" : "none";
    });

    // Filtrar grupos
    const groupItems = document.querySelectorAll("#groupsList li");
    groupItems.forEach((item) => {
      const name = item.textContent.toLowerCase();
      item.style.display = name.includes(searchText) ? "block" : "none";
    });
  }

  // Agregar evento de entrada en la barra de búsqueda
  if (searchBar) {
    searchBar.addEventListener("input", filterChats);
  }

  const selectChatMessage = document.createElement("div");

  function resetChatView() {
    chatInput.style.display = "none";
    chatHeader.style.display = "none"; // Oculta la cabecera del chat
    chatMessages.innerHTML = ""; // Vacía los mensajes
    chatTitle.textContent = ""; // Limpia el título
    chatTitle.dataset.id = "";
    chatTitle.dataset.type = "";
    selectChatMessage.style.display = "block"; // Muestra el mensaje central
  }

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      resetChatView();
    }
  });

  // Función para eliminar el chat (salir del grupo)
  async function leaveGroup() {
    const groupId = parseInt(chatTitle.dataset.id, 10);
    const confirmLeave = confirm("¿Seguro que quieres salir del grupo?");

    if (!confirmLeave) return;

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/users/grups/${groupId}/salir`,
        { method: "DELETE", headers }
      );

      if (!response.ok) throw new Error("Error al salir del grupo");

      alert("Has salido del grupo.");

      resetChatView(); // 🔥 Volver a la pantalla principal del chat
      await fetchFriendsAndGroups(); // 🔥 Recargar lista de amigos y grupos
    } catch (error) {
      showErrorMessage(error);
    }
  }

  // Función para eliminar un grupo
  async function deleteGroup() {
    const groupId = parseInt(chatTitle.dataset.id, 10);
    const confirmDelete = confirm(
      "¿Seguro que quieres eliminar el grupo? Esta acción no se puede deshacer."
    );

    if (!confirmDelete) return;

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/users/grups/${groupId}`,
        { method: "DELETE", headers }
      );

      await handleFetchErrors(response);
      alert("Grupo eliminado correctamente.");
      resetChatView();
    } catch (error) {
      showErrorMessage(error);
    }
  }

  // Función para abrir el modal con una lista de usuarios con checkboxes para agregar varios
  async function openUserSelectionModal(action) {
    const groupId = parseInt(chatTitle.dataset.id, 10);

    // Eliminar cualquier modal previo para evitar duplicados
    const existingModal = document.getElementById("customUserModal");
    if (existingModal) existingModal.remove();

    // Crear el overlay del modal
    const modalOverlay = document.createElement("div");
    modalOverlay.id = "customUserModal";
    modalOverlay.style.position = "fixed";
    modalOverlay.style.top = "0";
    modalOverlay.style.left = "0";
    modalOverlay.style.width = "100%";
    modalOverlay.style.height = "100%";
    modalOverlay.style.backgroundColor = "rgba(0,0,0,0.5)";
    modalOverlay.style.display = "flex";
    modalOverlay.style.alignItems = "center";
    modalOverlay.style.justifyContent = "center";
    modalOverlay.style.zIndex = "2000";

    // Crear el contenido del modal
    const modalContent = document.createElement("div");
    modalContent.style.background = "#fff";
    modalContent.style.padding = "20px";
    modalContent.style.borderRadius = "5px";
    modalContent.style.width = "300px";
    modalContent.style.maxHeight = "80%";
    modalContent.style.overflowY = "auto";

    // Título del modal
    const title = document.createElement("h2");
    title.textContent =
      action === "addAdmin"
        ? "Selecciona usuarios para hacer admin"
        : action === "addUser"
        ? "Selecciona usuarios para agregar"
        : "Selecciona usuarios para eliminar";
    modalContent.appendChild(title);

    // Contenedor de lista de usuarios
    const userListContainer = document.createElement("div");
    userListContainer.style.maxHeight = "150px";
    userListContainer.style.overflowY = "auto";
    userListContainer.style.border = "1px solid #ccc";
    userListContainer.style.padding = "5px";
    userListContainer.style.marginBottom = "10px";

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/users/grups/${groupId}/usuarios`,
        { headers }
      );
      const data = await handleFetchErrors(response);
      let users = data.users || [];

      // Filtrar usuarios según la acción
      if (action === "addAdmin") {
        users = users.filter((user) => !user.is_admin);
      } else if (action === "addUser") {
        const allUsersResponse = await fetch(
          "http://127.0.0.1:8000/users/llistaamics",
          { headers }
        );
        const allUsersData = await handleFetchErrors(allUsersResponse);
        const allUsers = allUsersData.friends || [];
        users = allUsers.filter(
          (user) => !data.users.some((groupUser) => groupUser.id === user.id)
        );
      } else if (action === "removeUser") {
        users = users.filter(
          (user) => user.id !== parseInt(sessionStorage.getItem("user_id"))
        );
      }

      // Crear lista de usuarios con checkboxes
      users.forEach((user) => {
        const checkboxContainer = document.createElement("div");
        checkboxContainer.style.display = "flex";
        checkboxContainer.style.alignItems = "center";
        checkboxContainer.style.padding = "5px";

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.value = user.id;
        checkbox.style.marginRight = "5px";

        const label = document.createElement("label");
        label.textContent = user.username;

        checkboxContainer.appendChild(checkbox);
        checkboxContainer.appendChild(label);
        userListContainer.appendChild(checkboxContainer);
      });

      modalContent.appendChild(userListContainer);
    } catch (error) {
      showErrorMessage(error);
      return;
    }

    // Contenedor de botones (Cancelar y Confirmar)
    const buttonsContainer = document.createElement("div");
    buttonsContainer.style.display = "flex";
    buttonsContainer.style.justifyContent = "flex-end";
    buttonsContainer.style.gap = "10px";

    // Botón Cancelar
    const cancelButton = document.createElement("button");
    cancelButton.textContent = "Cancelar";
    cancelButton.addEventListener("click", () => {
      document.body.removeChild(modalOverlay);
    });
    buttonsContainer.appendChild(cancelButton);

    // Botón Confirmar
    const confirmButton = document.createElement("button");
    confirmButton.textContent = "Confirmar";
    confirmButton.addEventListener("click", async () => {
      const selectedUsers = [
        ...userListContainer.querySelectorAll("input[type='checkbox']:checked"),
      ].map((cb) => cb.value);
      if (selectedUsers.length === 0) {
        alert("Selecciona al menos un usuario.");
        return;
      }

      // Llamar a la función de confirmación
      await confirmUserSelection(action, groupId, selectedUsers);
      document.body.removeChild(modalOverlay);
    });

    buttonsContainer.appendChild(confirmButton);
    modalContent.appendChild(buttonsContainer);
    modalOverlay.appendChild(modalContent);
    document.body.appendChild(modalOverlay);
  }

  /**
   * Función para confirmar la selección de usuarios y hacer la petición al backend.
   */
  async function confirmUserSelection(action, groupId, selectedUsers) {
    try {
      for (const userId of selectedUsers) {
        let endpoint = "";
        let method = "";

        if (action === "addAdmin") {
          endpoint = `/grups/${groupId}/asignar-admin?nuevo_admin_id=${userId}`;
          method = "PUT";
        } else if (action === "addUser") {
          endpoint = `/grups/${groupId}/agregar-usuario?nuevo_miembro_id=${userId}`;
          method = "POST";
        } else if (action === "removeUser") {
          endpoint = `/grups/${groupId}/eliminar-usuario/${userId}`;
          method = "DELETE";
        }

        const response = await fetch(`http://127.0.0.1:8000/users${endpoint}`, {
          method: method,
          headers,
        });

        await handleFetchErrors(response);
      }

      alert("Operación realizada con éxito.");
    } catch (error) {
      showErrorMessage(error);
    }
  }

  async function checkIfAdmin(groupId) {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/users/grups/${groupId}/es-admin`,
        { headers }
      );
      const data = await handleFetchErrors(response);
      return data.is_admin; // true o false
    } catch (error) {
      showErrorMessage(error);
      return false;
    }
  }

  // Eventos para abrir el modal con la nueva interfaz
  document
    .getElementById("addAdmin")
    .addEventListener("click", () => openUserSelectionModal("addAdmin"));
  document
    .getElementById("addUser")
    .addEventListener("click", () => openUserSelectionModal("addUser"));
  document
    .getElementById("removeUser")
    .addEventListener("click", () => openUserSelectionModal("removeUser"));

  if (deleteChatButton) {
    deleteChatButton.addEventListener("click", leaveGroup);
  }

  if (deleteGroupButton) {
    deleteGroupButton.addEventListener("click", deleteGroup);
  }

  settingsButton.style.display = "none";
  fetchFriendsAndGroups();
  resetChatView();
});
