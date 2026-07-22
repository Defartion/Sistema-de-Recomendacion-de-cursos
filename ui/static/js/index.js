const TOTAL_STEPS = 7; // Número total de pasos del formulario; se usa como límite en los bucles y cálculos de progreso
const multiSelections = { categorias: [] }; // Almacena las selecciones múltiples; categorias es un arreglo porque el usuario puede elegir más de una
const singleSelections = {}; // Almacena las selecciones únicas (sexo, nivel, modalidad, categoria); un objeto vacío que se va llenando conforme el usuario hace clic

function showStep(n) {
  // Oculta todos los pasos y muestra solo el paso número n
  for (let i = 1; i <= TOTAL_STEPS; i++) {
    const el = document.getElementById('step-' + i); // Busca el elemento HTML con id "step-1", "step-2", etc.
    if (el) el.classList.add('hidden'); // Si el elemento existe, lo oculta con la clase Tailwind "hidden" (display: none)
  }
  const active = document.getElementById('step-' + n); // Busca el paso que se quiere mostrar
  if (active) {
    active.classList.remove('hidden');   // Lo hace visible quitando la clase "hidden"
    void active.offsetWidth;             // Fuerza al navegador a recalcular el layout antes de añadir la animación
                                         // Sin esta línea, el navegador podría ignorar la animación porque añade y quita clases demasiado rápido
    active.classList.add('animate-fade-up'); // Añade la animación de entrada definida en base.html
  }
  const bar = document.getElementById('progressBar');
  if (bar) bar.style.width = (n / TOTAL_STEPS * 100) + '%'; // Calcula el porcentaje de avance y actualiza el ancho de la barra de progreso visualmente
  const text = document.getElementById('progressText');
  if (text) text.textContent = 'Paso ' + n + ' de ' + TOTAL_STEPS; // Actualiza el texto "Paso 1 de 7", "Paso 2 de 7", etc.
  window.scrollTo(0, 0); // Lleva la página al inicio para que el usuario siempre vea el nuevo paso desde arriba
}

function selectSingle(card, group, value) {
  // Maneja la selección de tarjetas de opción única (solo se puede elegir una a la vez por grupo)
  const grid = card.closest('.grid') || card.parentElement; // Busca el contenedor de tarjetas subiendo en el DOM; .closest() busca el ancestro más cercano con clase "grid"
  grid.querySelectorAll('.select-card-tw').forEach(c => c.classList.remove('selected')); // Quita la clase "selected" de TODAS las tarjetas del grupo para deseleccionar la anterior
  card.classList.add('selected');      // Marca visualmente como seleccionada solo la tarjeta que el usuario acaba de elegir
  singleSelections[group] = value;     // Guarda la elección en el objeto global; ej: singleSelections['nivel'] = 'Intermedio'
  const map = { sexo: 'hiddenSexo', nivel: 'hiddenNivel', modalidad: 'hiddenModalidad' };
  // Diccionario que conecta cada grupo con su campo oculto correspondiente en el formulario
  // Nota: 'categoria' no está aquí porque se actualiza manualmente en nextStep(4)
  if (map[group]) {
    document.getElementById(map[group]).value = value; // Escribe el valor seleccionado en el input hidden para que llegue al controller cuando se envíe el formulario
  }
}

function selectMulti(card, group, value, maxSelect) {
  // Maneja la selección de tarjetas de opción múltiple (el usuario puede elegir varias hasta un límite)
  const arr = multiSelections[group] || []; // Obtiene el arreglo de selecciones actuales del grupo; si no existe aún, usa un arreglo vacío
  const idx = arr.indexOf(value);           // Busca si el valor ya estaba seleccionado; devuelve -1 si no está
  if (idx > -1) {
    arr.splice(idx, 1);              // Si ya estaba seleccionado, lo elimina del arreglo (deselección)
    card.classList.remove('selected'); // Y quita el estilo visual de seleccionado
  } else {
    if (arr.length >= maxSelect) {   // Si ya se alcanzó el límite máximo de selecciones permitidas
      alert('Puedes seleccionar maximo ' + maxSelect + ' opciones.'); // Avisa al usuario que no puede seleccionar más
      return;                        // Sale de la función sin añadir nada
    }
    arr.push(value);                 // Si hay espacio, añade el nuevo valor al arreglo
    card.classList.add('selected');  // Y marca visualmente la tarjeta como seleccionada
  }
  if (group === 'categorias') {
    document.getElementById('catCount').textContent = arr.length; // Actualiza el contador visual que muestra cuántas categorías lleva seleccionadas el usuario
    document.getElementById('hiddenCategoria').value = arr[0] || ''; // Escribe la primera categoría seleccionada en el input hidden
                                                                       // Si el usuario deselecciona todo, queda vacío ('')
  }
}

function nextStep(from) {
  // Valida el paso actual y avanza al siguiente; cada bloque if corresponde a un paso específico
  if (from === 1) { // Validación del paso 1: Nombre
    const nombreVal = document.getElementById('nombre').value.trim(); // Lee el nombre y elimina espacios al inicio y al final
    if (!nombreVal) {
      alert('Por favor escribe tu nombre.');
      return; // Sale de la función sin avanzar si el campo está vacío
    }
    const regexNombre = /^[A-Za-zÁáÉéÍíÓóÚúÑñÜü\s]{2,40}$/;
    // Expresión regular que acepta solo letras (incluyendo acentos y ñ) y espacios, entre 2 y 40 caracteres
    // El ^ indica inicio y $ indica fin, asegurando que toda la cadena cumpla la regla
    if (!regexNombre.test(nombreVal)) {
      alert('El nombre solo puede contener letras y espacios (sin numeros, puntos, guiones ni simbolos).');
      return;
    }
    document.getElementById('nombre').value = nombreVal; // Guarda el nombre ya limpiado (sin espacios extra) de vuelta en el input
  }

  if (from === 2) { // Validación del paso 2: Edad y género
    const edadVal = document.getElementById('edad').value;
    const edad = Number(edadVal);                                           // Convierte el texto del input a número para poder compararlo
    if (!edadVal || !Number.isInteger(edad) || edad < 10 || edad > 100) {  // Verifica que no esté vacío, que sea entero (sin decimales) y que esté en rango válido
      alert('Por favor ingresa una edad valida entre 10 y 100 años (sin decimales).');
      return;
    }
    if (!singleSelections['sexo']) { // Verifica que el usuario haya elegido una opción de género haciendo clic en alguna tarjeta
      alert('Por favor selecciona una opcion de genero.');
      return;
    }
  }

  if (from === 4) { // Validación del paso 4: Categoría
    if (!singleSelections['categoria']) { // Verifica que el usuario haya hecho clic en al menos una tarjeta de categoría
      alert('Por favor selecciona una categoria.');
      return;
    }
    document.getElementById('hiddenCategoria').value = singleSelections['categoria'];
    // Escribe la categoría en el input hidden aquí (y no en selectSingle) porque 'categoria'
    // no está en el map de selectSingle; este es el momento seguro para confirmarlo antes de avanzar
  }

  if (from === 5) { // Validación del paso 5: Nivel
    if (!singleSelections['nivel']) { // Verifica que el usuario haya seleccionado un nivel de dificultad
      alert('Por favor selecciona tu nivel.');
      return;
    }
    document.getElementById('hiddenNivel').value = singleSelections['nivel']; // Confirma el valor en el input hidden antes de avanzar
  }

  if (from === 6) { // Validación del paso 6: Tiempo y presupuesto
    const tiempoVal = document.getElementById('tiempo').value;
    const tiempo = Number(tiempoVal);
    if (!tiempoVal || !Number.isInteger(tiempo) || tiempo < 10 || tiempo > 720) {
      // Valida que las horas sean un entero entre 10 y 720 (máximo 30 días × 24 horas)
      alert('Por favor ingresa un numero de horas valido (entre 10 y 720, sin decimales).');
      return;
    }
    const presupuestoVal = document.getElementById('presupuesto').value;
    const presupuesto = parseFloat(presupuestoVal); // parseFloat porque el presupuesto puede tener decimales (ej: 49.99)
    if (presupuestoVal.trim() === '' || isNaN(presupuesto) || presupuesto < 0) {
      // Verifica que no esté vacío, que sea un número válido y que no sea negativo
      // isNaN() detecta si parseFloat no pudo convertir el texto a número (ej: "abc" → NaN)
      alert('Por favor ingresa un presupuesto valido (0 o mayor).');
      return;
    }
  }

  showStep(from + 1); // Si todas las validaciones del paso actual pasaron, avanza al siguiente paso
}

function prevStep(from) {
  if (from > 1) showStep(from - 1); // Retrocede al paso anterior; la condición evita intentar ir al "paso 0" desde el primer paso
}

document.getElementById('onboardingForm').addEventListener('submit', function(e) {
  // Se ejecuta justo antes de que el formulario se envíe al servidor
  if (!singleSelections['modalidad']) { // Última validación: verifica que el usuario haya elegido modalidad en el paso 7
    e.preventDefault();                 // Cancela el envío del formulario si falta la modalidad
    alert('Por favor selecciona como prefieres estudiar.');
    return;
  }
  document.getElementById('hiddenModalidad').value = singleSelections['modalidad']; // Confirma la modalidad en el input hidden justo antes del envío
  document.getElementById('hiddenNivel').value = singleSelections['nivel'] || '';   // Confirma el nivel; el '' evita que llegue "undefined" al controller si por alguna razón no fue seleccionado

  const checkboxGratuitos = document.getElementById('soloGratuitos');
  if (checkboxGratuitos && checkboxGratuitos.checked) { // Si el checkbox de "solo gratuitos" está marcado al momento de enviar
    document.getElementById('presupuesto').value = '0'; // Fuerza el presupuesto a 0 para que el controller filtre solo cursos gratuitos
  }
});

document.addEventListener('DOMContentLoaded', function() {
  // DOMContentLoaded se dispara cuando el HTML terminó de cargarse pero antes de que imágenes y estilos estén listos
  // Es el momento correcto para añadir listeners a elementos que ya existen en el DOM
  const checkbox = document.getElementById('soloGratuitos');
  const presupuestoInput = document.getElementById('presupuesto');
  if (checkbox && presupuestoInput) { // Verifica que ambos elementos existan antes de añadir el listener para evitar errores si cambia el HTML
    checkbox.addEventListener('change', function() {
      // Se ejecuta cada vez que el usuario marca o desmarca el checkbox
      if (this.checked) {                              // Si el usuario marcó el checkbox de "solo gratuitos"
        presupuestoInput.value = '0';                  // Pone el presupuesto en 0 automáticamente
        presupuestoInput.disabled = true;              // Deshabilita el input para que el usuario no pueda escribir otro valor
        presupuestoInput.classList.add('opacity-50');  // Oscurece visualmente el input para indicar que está deshabilitado
      } else {                                         // Si el usuario desmarcó el checkbox
        presupuestoInput.disabled = false;             // Reactiva el input de presupuesto
        presupuestoInput.classList.remove('opacity-50'); // Quita el efecto visual de deshabilitado
        presupuestoInput.value = '';                   // Limpia el valor para que el usuario ingrese su presupuesto real
      }
    });
  }
});

showStep(1); // Muestra el primer paso al cargar la página; sin esta línea todos los pasos estarían ocultos desde el inicio