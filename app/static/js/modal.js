function openModal(id) {
  var modal = document.getElementById("myModal");

  // Validación del ID antes de llamar al backend
  if (
    id === undefined ||
    id === null ||
    id === "" ||
    Number.isNaN(Number(id))
  ) {
    console.error("openModal llamado sin un id válido:", id);
    // No abrir el modal si el ID no es válido
    return;
  }

  // Realizar petición AJAX a la ruta correcta del blueprint
  fetch("api/operators?id=" + encodeURIComponent(id))
    .then(async (response) => {
      if (!response.ok) {
        const text = await response.text().catch(() => "");
        throw new Error(
          `Error ${response.status}: ${text || "No encontrado"}`
        );
      }
      return response.json();
    })
    .then((data) => {
      var modalContent = document.getElementById("modal-content");
      // Render sencillo de lista
      var htmlContent = "<h3>Operadores activos</h3><ul>";
      (Array.isArray(data) ? data : []).forEach((item) => {
        htmlContent += "<li><p>" + item + "</p></li>";
      });
      htmlContent += "</ul>";
      if (modalContent) modalContent.innerHTML = htmlContent;
      if (modal) modal.style.display = "block";
    })
    .catch((error) => {
      console.error("Fallo al obtener operadores:", error);
      var modalContent = document.getElementById("modal-content");
      if (modalContent) {
        modalContent.textContent =
          "Fallo al obtener operadores: " + error.message;
      }
      if (modal) modal.style.display = "block";
    });
}

function closeModal() {
  var modal = document.getElementById("myModal");
  modal.style.display = "none";
}
