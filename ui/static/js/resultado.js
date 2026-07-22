// Diccionario de URLs base de cada plataforma como fallback
// Se usa cuando un curso no tiene URL propia en el JSON pero sí tiene plataforma registrada
// El orden no importa; se accede por clave exacta (ej: PLATFORM_LINKS["Udemy"])
const PLATFORM_LINKS = {
  "Udemy":            "https://www.udemy.com",
  "Coursera":         "https://www.coursera.org",
  "Platzi":           "https://platzi.com",
  "edX":              "https://www.edx.org",
  "Skillshare":       "https://www.skillshare.com",
  "DataCamp":         "https://www.datacamp.com",
  "freeCodeCamp":     "https://www.freecodecamp.org",
  "Udacity":          "https://www.udacity.com",
  "LinkedIn Learning":"https://www.linkedin.com/learning",
};

function openModal(id) {
  // Se ejecuta cuando el usuario hace clic en cualquier tarjeta de curso
  // Busca el curso en el diccionario COURSES que Jinja2 generó al renderizar resultado.html
  const curso = COURSES[id];
  if (!curso) return; // Si el id no existe en COURSES (no debería ocurrir), sale silenciosamente sin romper la página

  // ── Llenar los campos de texto del modal con los datos del curso ──
  document.getElementById('modalNombre').textContent    = curso.nombre;
  document.getElementById('modalCategoria').textContent = curso.categoria;
  document.getElementById('modalNivel').textContent     = curso.nivel;
  document.getElementById('modalDuracion').textContent  = curso.duracion + ' horas'; // Concatena el número con la unidad para mostrar "30 horas"
  document.getElementById('modalModalidad').textContent = curso.modalidad;
  document.getElementById('modalPlataforma').textContent= curso.plataforma;
  document.getElementById('modalPrecio').textContent    = curso.precio == 0
    ? 'Gratis'                                     // Si el precio es exactamente 0, muestra "Gratis" en lugar de "$0.00 USD"
    : '$' + curso.precio.toFixed(2) + ' USD';      // toFixed(2) formatea el número con siempre 2 decimales: 49.9 → "49.90"

  // ── Generar las estrellas de rating dinámicamente ──
  let starsHtml = '';
  for (let i = 0; i < 5; i++) {                    // Itera 5 veces, una por cada estrella posible
    starsHtml += i < curso.rating                  // Si la posición actual (0,1,2...) es menor que el rating del curso
      ? '<i class="fa-solid fa-star"></i>'         // Estrella llena (Font Awesome solid)
      : '<i class="fa-regular fa-star"></i>';      // Estrella vacía (Font Awesome regular)
  }                                                // Ej: rating 4.5 → 4 estrellas llenas + 1 vacía (el .5 se trunca porque i es entero)
  document.getElementById('modalRating').innerHTML = starsHtml
    + ' <span class="text-slate-400 text-xs ml-1">' + curso.rating.toFixed(1) + ' / 5.0</span>';
    // Añade el número exacto del rating al lado de las estrellas: "★★★★☆ 4.5 / 5.0"
    // Se usa innerHTML (no textContent) porque starsHtml contiene etiquetas HTML de Font Awesome

  // ── Generar los chips de tags del curso ──
  const tagsHtml = (curso.tags || []).map(t =>     // curso.tags || [] evita error si el curso no tiene tags en el JSON
    '<span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-brand-500/10 text-brand-300 border border-brand-500/20">'
    + '<i class="fa-solid fa-check text-[10px]"></i> ' + t + '</span>'
    // Cada tag se convierte en un chip con ícono de check y estilos Tailwind
  ).join('');                                       // .join('') une todos los chips en una sola cadena de HTML sin separadores
  document.getElementById('modalTags').innerHTML = tagsHtml
    || '<p class="text-slate-500 text-sm">Curso especializado en ' + curso.categoria + '</p>';
    // Si el curso no tiene tags (tagsHtml es cadena vacía, que es falsy), muestra un texto genérico con la categoría como fallback

  // ── Asignar el enlace del botón "Ver curso" ──
  document.getElementById('modalLink').href =
    curso.url                        // Primera prioridad: URL específica del curso en el JSON
    || PLATFORM_LINKS[curso.plataforma] // Segunda prioridad: URL base de la plataforma del diccionario de arriba
    || '#';                          // Última opción: '#' (enlace vacío) si no hay ninguna URL disponible

  // ── Mostrar el modal ──
  document.getElementById('modalOverlay').classList.add('active'); // La clase 'active' activa la visibilidad del modal definida en style.css
  document.body.style.overflow = 'hidden'; // Desactiva el scroll de la página mientras el modal está abierto para que el usuario no pueda desplazarse detrás del modal
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('active'); // Quita la clase 'active' para ocultar el modal con su animación de salida
  document.body.style.overflow = ''; // Restaura el scroll de la página; '' (cadena vacía) le devuelve el valor por defecto al navegador
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal(); // Permite cerrar el modal presionando la tecla Escape, además del botón de cerrar
                                        // Es una mejora de accesibilidad: los usuarios no siempre buscan el botón X para cerrar
});