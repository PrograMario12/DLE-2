 function openModal(id) {
    var modal = document.getElementById("myModal");

    // Realizar petición AJAX a una ruta en Flask para obtener la información
    // y mostrarla en el contenido del modal
    fetch('/get_operators_actives?id=' + id)
      .then(response => response.json())
      .then(data => {
        var modalContent = document.getElementById("modal-content");
        modalContent.innerHTML = JSON.stringify(data); // Aquí puedes personalizar cómo mostrar la información
        var htmlContent = '<ul>';
        data.forEach(item => {
          htmlContent += '<li><p>' + item + '</p></li>';
        });
        htmlContent += '</ul>';
        modalContent.innerHTML = htmlContent;
        modal.style.display = "block";
      })
      .catch(error => console.error(error));
  }

  // Función para cerrar el modal
  function closeModal() {
    var modal = document.getElementById("myModal");
    modal.style.display = "none";
  }