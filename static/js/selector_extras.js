// static/js/selector_extras.js
// Mejora de usabilidad para el widget de permisos (dos listas) del admin.
// Ultra-seguro: si no existen los selectores, NO hace nada (no toca el login).

(() => {
  "use strict";

  const onReady = (fn) =>
    document.readyState === "loading"
      ? document.addEventListener("DOMContentLoaded", fn, { once: true })
      : fn();

  onReady(() => {
    // Salir si no hay ningún selector de permisos
    const wrappers = Array.from(document.querySelectorAll("div.selector"));
    if (!wrappers.length) return;

    wrappers.forEach((wrapper) => {
      try {
        const left  = wrapper.querySelector(".selector-available select");
        const right = wrapper.querySelector(".selector-chosen select");
        if (!left || !right) return;

        const addBtn = wrapper.querySelector(".selector-chooser .selector-add");
        const remBtn = wrapper.querySelector(".selector-chooser .selector-remove");

        const moveSelected = (fromSel, toSel) => {
          const moved = Array.from(fromSel.selectedOptions);
          if (!moved.length) return;
          moved.forEach((opt) => toSel.appendChild(opt));
          // Mantener enfoque/selección en destino para feedback
          toSel.focus();
          moved.forEach((o) => (o.selected = true));
          // Disparar change por si el tema escucha eventos
          toSel.dispatchEvent(new Event("change", { bubbles: true }));
        };

        const selectAll = (sel) => Array.from(sel.options).forEach((o) => (o.selected = true));

        // Click en flechas (si existen)
        addBtn && addBtn.addEventListener("click", () => moveSelected(left, right));
        remBtn && remBtn.addEventListener("click", () => moveSelected(right, left));

        // Doble clic en opciones
        left.addEventListener("dblclick", () => moveSelected(left, right));
        right.addEventListener("dblclick", () => moveSelected(right, left));

        // Atajos de teclado
        left.addEventListener("keydown", (e) => {
          if (e.key === "Enter" || e.key === "ArrowRight") { e.preventDefault(); moveSelected(left, right); }
          if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "a") { e.preventDefault(); selectAll(left); }
        });
        right.addEventListener("keydown", (e) => {
          if (e.key === "Backspace" || e.key === "ArrowLeft") { e.preventDefault(); moveSelected(right, left); }
          if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "a") { e.preventDefault(); selectAll(right); }
        });

        // Filtros en vivo (no invasivos: usan .hidden)
        const leftFilter = wrapper.querySelector(
          ".selector-available input[type='text'], .selector-available input[type='search']"
        );
        const rightFilter = wrapper.querySelector(
          ".selector-chosen input[type='text'], .selector-chosen input[type='search']"
        );
        const hookFilter = (input, sel) => {
          if (!input || !sel) return;
          input.setAttribute("autocomplete", "off");
          const doFilter = () => {
            const q = input.value.trim().toLowerCase();
            Array.from(sel.options).forEach((o) => (o.hidden = !!q && !o.text.toLowerCase().includes(q)));
          };
          input.addEventListener("input", doFilter);
        };
        hookFilter(leftFilter, left);
        hookFilter(rightFilter, right);

        // Tooltips con el texto completo
        const setTitles = (sel) =>
          Array.from(sel.options).forEach((o) => { if (!o.title) o.title = o.textContent.trim(); });
        setTitles(left); setTitles(right);

        const obs = new MutationObserver(() => { setTitles(left); setTitles(right); });
        obs.observe(left,  { childList: true });
        obs.observe(right, { childList: true });
      } catch (_) {
        // Silencioso: nunca romper el admin si algo cambia
      }
    });
  });
})();
