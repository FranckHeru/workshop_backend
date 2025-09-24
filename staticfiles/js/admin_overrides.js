// JS de overrides del admin (intencionalmente mínimo)
document.addEventListener("DOMContentLoaded", () => {
  // Si necesitas algo luego, aquí es el lugar.
});

// --- Cargar extras del selector SOLO cuando hace falta ---
(function () {
  // si no hay selector de dos listas, no cargamos nada
  if (!document.querySelector("div.selector")) return;

  var s = document.createElement("script");
  s.src = "/static/js/selector_extras.js";   // ruta real: workshop_backend/backend/static/js/selector_extras.js
  s.defer = true;
  s.onerror = function(){ console.warn("No se pudo cargar selector_extras.js"); };
  document.head.appendChild(s);
})();
