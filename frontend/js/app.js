import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import MostrarListaAmigos from "./MostrarListaAmigos";
import Chat from "./Chat";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MostrarListaAmigos />} />
        <Route path="/chat/:username" element={<Chat />} />
      </Routes>
    </Router>
  );
}

export default App;
