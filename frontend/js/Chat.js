import React from "react";
import { useParams } from "react-router-dom";

const Chat = () => {
  const { username } = useParams();

  return (
    <div>
      <h1>Chat con {username}</h1>
      <textarea placeholder="Escribe tu mensaje aquí"></textarea>
      <button>Enviar</button>
    </div>
  );
};

export default Chat;
