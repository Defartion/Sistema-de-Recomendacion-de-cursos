const PLATFORM_LINKS = {
  "Udemy": "https://www.udemy.com",
  "Coursera": "https://www.coursera.org",
  "Platzi": "https://platzi.com",
  "edX": "https://www.edx.org",
  "Skillshare": "https://www.skillshare.com",
  "DataCamp": "https://www.datacamp.com",
  "freeCodeCamp": "https://www.freecodecamp.org",
  "Udacity": "https://www.udacity.com",
  "LinkedIn Learning": "https://www.linkedin.com/learning",
};

function openModal(id) {
  const curso = COURSES[id];
  if (!curso) return;

  document.getElementById('modalNombre').textContent = curso.nombre;
  document.getElementById('modalCategoria').textContent = curso.categoria;
  document.getElementById('modalNivel').textContent = curso.nivel;
  document.getElementById('modalDuracion').textContent = curso.duracion + ' horas';
  document.getElementById('modalModalidad').textContent = curso.modalidad;
  document.getElementById('modalPlataforma').textContent = curso.plataforma;
  document.getElementById('modalPrecio').textContent = curso.precio == 0 ? 'Gratis' : '$' + curso.precio.toFixed(2) + ' USD';

  let starsHtml = '';
  for (let i = 0; i < 5; i++) {
    starsHtml += i < curso.rating
      ? '<i class="fa-solid fa-star"></i>'
      : '<i class="fa-regular fa-star"></i>';
  }
  document.getElementById('modalRating').innerHTML = starsHtml + ' <span class="text-slate-400 text-xs ml-1">' + curso.rating.toFixed(1) + ' / 5.0</span>';

  const tagsHtml = (curso.tags || []).map(t =>
    '<span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold bg-brand-500/10 text-brand-300 border border-brand-500/20"><i class="fa-solid fa-check text-[10px]"></i> ' + t + '</span>'
  ).join('');
  document.getElementById('modalTags').innerHTML = tagsHtml || '<p class="text-slate-500 text-sm">Curso especializado en ' + curso.categoria + '</p>';

  document.getElementById('modalLink').href = curso.url || PLATFORM_LINKS[curso.plataforma] || '#';

  document.getElementById('modalOverlay').classList.add('active');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('active');
  document.body.style.overflow = '';
}

document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });
