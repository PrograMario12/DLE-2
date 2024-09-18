let html = document.getElementById("tiempo");

setInterval(function(){
	tiempo = new Date();

	horas = tiempo.getHours();
	minutos = tiempo.getMinutes();

	//evitar los 0 o numeros individuales
	if(horas<10)
		horas = "0"+horas;
	if(minutos<10)
		minutos = "0"+minutos;

	html.innerHTML = horas+" : "+minutos;
},1000);

document.getElementById("login-form").addEventListener("submit", function(event) {
	const employeeNumberInput = document.querySelector('input[name="employee_number"]');
	if (employeeNumberInput.value.length !== 10) {
	  event.preventDefault(); // Prevenir el envío del formulario
	  alert("Por favor escanea una credencial válida");
	}
  });