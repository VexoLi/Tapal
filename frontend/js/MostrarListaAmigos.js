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
    const friendsList = document.getElementById("friendsList");
    friendsList.innerHTML = ""; // Limpiar contenido previo

    // Generar los elementos usando un bucle clásico
    for (const friend of friends) {
      const listItem = document.createElement("li");
      listItem.className =
        "p-4 bg-white shadow rounded flex justify-between items-center";

      const friendInfo = document.createElement("span");
      friendInfo.textContent = `${friend.fullname} (${friend.username})`;

      const chatButton = document.createElement("button");
      chatButton.textContent = "Xateja";
      chatButton.className =
        "bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 transition";
      chatButton.addEventListener("click", () => startChat(friend.username));

      listItem.appendChild(friendInfo);
      listItem.appendChild(chatButton);
      friendsList.appendChild(listItem);
    }
  }

  // Función de ejemplo para iniciar un chat
  function startChat(username) {
    alert(`Iniciando chat con ${username}`);
  }

  // Ejemplo de datos
  const friends = [
    { fullname: "Joan Vicnes", username: "jvicnes" },
    { fullname: "Maria Lopez", username: "mlopez" },
    { fullname: "Carlos Sanchez", username: "csanchez" },
  ];

  // Mostrar los amigos al cargar la página
  document.addEventListener("DOMContentLoaded", () => {
    displayFriends(friends);
  });

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

import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

const MostrarListaAmigos = () => {
  const [friends, setFriends] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const navigate = useNavigate();

  // Obtener la lista de compañeros
  useEffect(() => {
    const fetchFriends = async () => {
      try {
        const response = await fetch("http://localhost:8000/llistaamics", {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        });
        const data = await response.json();
        setFriends(data);
      } catch (error) {
        console.error("Error al obtener los compañeros:", error);
      }
    };
    fetchFriends();
  }, []);

  // Filtrar la lista de compañeros
  const filteredFriends = friends.filter((friend) =>
    friend.fullname.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Redirigir al chat
  const startChat = (username) => {
    navigate(`/chat/${username}`);
  };

  return (
    <div className="min-h-screen p-6 bg-gray-100">
      <h2 className="text-2xl font-bold text-center mb-4">Llista de companys</h2>
      <input
        type="text"
        id="searchInput"
        className="w-full p-2 border border-gray-300 rounded mb-4"
        placeholder="Cerca un company per nom..."
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      <ul id="friendsList" className="space-y-2">
        {filteredFriends.map((friend) => (
          <li
            key={friend.username}
            className="p-4 bg-white shadow rounded flex justify-between items-center"
          >
            <span>{friend.fullname} ({friend.username})</span>
            <button
              className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 transition"
              onClick={() => startChat(friend.username)}
            >
              Xateja
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default MostrarListaAmigos;

