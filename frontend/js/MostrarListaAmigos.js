document.addEventListener("DOMContentLoaded", async () => {
    const friendsList = document.getElementById("friendsList");
    const searchInput = document.getElementById("searchInput");
  
    // Función para obtener la lista de compañeros
    async function fetchFriends() {
      try {
        const token = localStorage.getItem("token"); // Asegúrate de tener el token
        const response = await fetch("http://localhost:8000/llistaamics", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
  
        if (!response.ok) {
          throw new Error("Error al obtener la lista de compañeros");
        }
  
        const friends = await response.json();
        displayFriends(friends);
      } catch (error) {
        console.error(error);
        friendsList.innerHTML = "<li>Error al cargar la lista</li>";
      }
    }
  
    // Función para mostrar los compañeros en la lista
    function displayFriends(friends) {
      friendsList.innerHTML = friends
        .map(
          (friend) => `
        <li class="p-4 bg-white shadow rounded flex justify-between items-center">
          <span>${friend.fullname} (${friend.username})</span>
          <button
            class="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 transition"
            onclick="startChat('${friend.username}')"
          >
            Xateja
          </button>
        </li>
      `
        )
        .join("");
    }
  
    // Función para buscar en la lista
    searchInput.addEventListener("input", (e) => {
      const searchTerm = e.target.value.toLowerCase();
      const allFriends = document.querySelectorAll("#friendsList li");
  
      allFriends.forEach((friend) => {
        const text = friend.innerText.toLowerCase();
        friend.style.display = text.includes(searchTerm) ? "" : "none";
      });
    });
  
    // Llama a la función para obtener los datos
    fetchFriends();
  });
  
  // Función para iniciar un chat (puedes personalizarla más adelante)
  function startChat(username) {
    alert(`Inicia chat amb ${username}`);
    // Aquí puedes redirigir a la página de chat
  }
  