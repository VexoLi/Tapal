import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";

const Chat = () => {
  const { username } = useParams();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");

  useEffect(() => {
    // Obtener mensajes previos (puedes conectar esto a la API más adelante)
    setMessages([
      { from: username, text: "Hola, ¿cómo estás?" },
      { from: "yo", text: "Bien, ¿y tú?" },
    ]);
  }, [username]);

  const sendMessage = async () => {
    if (!newMessage.trim()) return;
    // Aquí puedes enviar el mensaje a la API
    setMessages([...messages, { from: "yo", text: newMessage }]);
    setNewMessage("");
  };

  return (
    <div className="p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-4">Chat con {username}</h1>
      <div className="space-y-2 mb-4">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`p-2 rounded ${
              msg.from === "yo" ? "bg-blue-100 self-end" : "bg-gray-200"
            }`}
          >
            <strong>{msg.from}:</strong> {msg.text}
          </div>
        ))}
      </div>
      <textarea
        className="w-full p-2 border border-gray-300 rounded mb-4"
        placeholder="Escribe tu mensaje aquí"
        value={newMessage}
        onChange={(e) => setNewMessage(e.target.value)}
      ></textarea>
      <button
        className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 transition"
        onClick={sendMessage}
      >
        Enviar
      </button>
    </div>
  );
};

export default Chat;
