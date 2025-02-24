// errorHandler.js

/**
 * Maneja errores de respuestas HTTP, detectando distintos tipos de fallos.
 * @param {Response} response - Respuesta del `fetch()`
 * @returns {Promise<any>} - Devuelve el JSON si la respuesta es exitosa.
 * @throws {Error} - Lanza un error con un mensaje detallado si falla.
 */
export async function handleFetchErrors(response) {
  if (!response.ok) {
    let errorMessage = `Error ${response.status}: ${response.statusText}`;

    try {
      // Intentamos obtener el mensaje de error en formato JSON
      const errorData = await response.json();
      if (errorData && errorData.detail) {
        errorMessage += ` - ${errorData.detail}`;
      }
    } catch {
      // Si no se puede parsear como JSON, intentamos obtener el texto plano
      const errorText = await response.text();
      if (errorText) {
        errorMessage += ` - ${errorText}`;
      }
    }

    throw new Error(errorMessage);
  }

  // Si la respuesta es OK, intentamos devolver JSON
  try {
    return await response.json();
  } catch {
    throw new Error(
      "Error al procesar la respuesta del servidor (JSON inválido)"
    );
  }
}

/**
 * Muestra un mensaje de error y lo imprime en la consola con formato detallado.
 * @param {Error} error - Objeto de error a manejar.
 * @param {boolean} showAlert - Define si se debe mostrar un alert (true por defecto).
 */
export function showErrorMessage(error, showAlert = true) {
  console.error("❌ Error capturado:", {
    message: error.message || "Error desconocido",
    stack: error.stack || "No disponible",
  });

  if (showAlert) {
    alert(`⚠️ Ocurrió un error: ${error.message || "Error desconocido"}`);
  }
}
