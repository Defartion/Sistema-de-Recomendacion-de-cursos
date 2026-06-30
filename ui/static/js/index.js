const TOTAL_STEPS = 7;
const multiSelections = { categorias: [] };
const singleSelections = {};

function showStep(n) {
  for (let i = 1; i <= TOTAL_STEPS; i++) {
    const el = document.getElementById('step-' + i);
    if (el) el.classList.add('hidden');
  }
  const active = document.getElementById('step-' + n);
  if (active) {
    active.classList.remove('hidden');
    void active.offsetWidth;
    active.classList.add('animate-fade-up');
  }
  const bar = document.getElementById('progressBar');
  if (bar) bar.style.width = (n / TOTAL_STEPS * 100) + '%';
  const text = document.getElementById('progressText');
  if (text) text.textContent = 'Paso ' + n + ' de ' + TOTAL_STEPS;
  window.scrollTo(0, 0);
}

function selectSingle(card, group, value) {
  const grid = card.closest('.grid') || card.parentElement;
  grid.querySelectorAll('.select-card-tw').forEach(c => c.classList.remove('selected'));
  card.classList.add('selected');
  singleSelections[group] = value;
  const map = { sexo: 'hiddenSexo', nivel: 'hiddenNivel', modalidad: 'hiddenModalidad' };
  if (map[group]) {
    document.getElementById(map[group]).value = value;
  }
}

function selectMulti(card, group, value, maxSelect) {
  const arr = multiSelections[group] || [];
  const idx = arr.indexOf(value);
  if (idx > -1) {
    arr.splice(idx, 1);
    card.classList.remove('selected');
  } else {
    if (arr.length >= maxSelect) {
      alert('Puedes seleccionar maximo ' + maxSelect + ' opciones.');
      return;
    }
    arr.push(value);
    card.classList.add('selected');
  }
  if (group === 'categorias') {
    document.getElementById('catCount').textContent = arr.length;
    document.getElementById('hiddenCategoria').value = arr[0] || '';
  }
}

function nextStep(from) {
  if (from === 1) {
    if (!document.getElementById('nombre').value.trim()) {
      alert('Por favor escribe tu nombre.');
      return;
    }
  }
  if (from === 2) {
    const edadVal = document.getElementById('edad').value;
    const edad = Number(edadVal);
    if (!edadVal || !Number.isInteger(edad) || edad < 10 || edad > 100) {
      alert('Por favor ingresa una edad valida entre 10 y 100 anos (sin decimales).');
      return;
    }
    if (!singleSelections['sexo']) {
      alert('Por favor selecciona una opcion de genero.');
      return;
    }
  }
  if (from === 4) {
    if (!singleSelections['categoria']) {
      alert('Por favor selecciona una categoria.');
      return;
    }
    document.getElementById('hiddenCategoria').value = singleSelections['categoria'];
  }
  if (from === 5) {
    if (!singleSelections['nivel']) {
      alert('Por favor selecciona tu nivel.');
      return;
    }
    document.getElementById('hiddenNivel').value = singleSelections['nivel'];
  }
  if (from === 6) {
    const tiempoVal = document.getElementById('tiempo').value;
    const tiempo = Number(tiempoVal);
    if (!tiempoVal || !Number.isInteger(tiempo) || tiempo < 1) {
      alert('Por favor ingresa un numero de horas valido (sin decimales, minimo 1).');
      return;
    }
    const presupuestoVal = document.getElementById('presupuesto').value;
    const presupuesto = parseFloat(presupuestoVal);
    if (presupuestoVal.trim() === '' || isNaN(presupuesto) || presupuesto < 0) {
      alert('Por favor ingresa un presupuesto valido (0 o mayor).');
      return;
    }
  }
  showStep(from + 1);
}

function prevStep(from) {
  if (from > 1) showStep(from - 1);
}

document.getElementById('onboardingForm').addEventListener('submit', function(e) {
  if (!singleSelections['modalidad']) {
    e.preventDefault();
    alert('Por favor selecciona como prefieres estudiar.');
    return;
  }
  document.getElementById('hiddenModalidad').value = singleSelections['modalidad'];
  document.getElementById('hiddenNivel').value = singleSelections['nivel'] || '';

  // If "solo gratuitos" is checked, set presupuesto to 0
  const checkboxGratuitos = document.getElementById('soloGratuitos');
  if (checkboxGratuitos && checkboxGratuitos.checked) {
    document.getElementById('presupuesto').value = '0';
  }
});

// Handle "solo cursos gratuitos" checkbox
document.addEventListener('DOMContentLoaded', function() {
  const checkbox = document.getElementById('soloGratuitos');
  const presupuestoInput = document.getElementById('presupuesto');
  if (checkbox && presupuestoInput) {
    checkbox.addEventListener('change', function() {
      if (this.checked) {
        presupuestoInput.value = '0';
        presupuestoInput.disabled = true;
        presupuestoInput.classList.add('opacity-50');
      } else {
        presupuestoInput.disabled = false;
        presupuestoInput.classList.remove('opacity-50');
        presupuestoInput.value = '';
      }
    });
  }
});

showStep(1);
