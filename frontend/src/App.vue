<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import MatrixInput from './components/MatrixInput.vue';
import MathRenderer from './components/MathRenderer.vue';
import InlineMathText from './components/InlineMathText.vue';

const isDarkMode = ref(true);

const operations = [
  { id: 'gauss', name: 'Eliminación Gaussiana', requiresTwo: false, endpoint: '/api/solve/gaussian-elimination' },
  { id: 'cramer', name: 'Método de Cramer', requiresTwo: false, endpoint: '/api/solve/cramer' },
  { id: 'inverse-gauss', name: 'Inversa (Gauss-Jordan)', requiresTwo: false, endpoint: '/api/solve/inverse-gauss' },
  { id: 'inverse-adj', name: 'Inversa (Adjunta)', requiresTwo: false, endpoint: '/api/solve/inverse-adj' },
  { id: 'lu', name: 'Factorización LU', requiresTwo: false, endpoint: '/api/solve/lu' },
  { id: 'add', name: 'Suma de Matrices', requiresTwo: true, endpoint: '/api/solve/matrix-algebra/add' },
  { id: 'subtract', name: 'Resta de Matrices', requiresTwo: true, endpoint: '/api/solve/matrix-algebra/subtract' },
  { id: 'multiply', name: 'Multiplicación de Matrices', requiresTwo: true, endpoint: '/api/solve/matrix-algebra/multiply' },
  { id: 'transpose', name: 'Traspuesta', requiresTwo: false, endpoint: '/api/solve/matrix-algebra/transpose' },
  { id: 'linear-dep', name: 'Dependencia Lineal', requiresTwo: false, endpoint: '/api/solve/vector-spaces/dependence' },
  { id: 'distance', name: 'Longitud y Distancia', requiresTwo: true, endpoint: '/api/solve/vector-spaces/distance' },
  { id: 'angle', name: 'Ángulo entre Vectores', requiresTwo: true, endpoint: '/api/solve/vector-spaces/angle' },
  { id: 'least-squares', name: 'Mínimos Cuadrados', requiresTwo: false, endpoint: '/api/solve/vector-spaces/least-squares' }
];

const selectedOperationId = ref('gauss');
const selectedOperation = computed(() => operations.find(o => o.id === selectedOperationId.value));

const isAugmentedOperation = computed(() => {
  return ['gauss', 'cramer', 'least-squares'].includes(selectedOperationId.value);
});

// Matriz A
const matrixA = ref([
  ['2', '1', '-1'],
  ['-3', '-1', '2'],
  ['-2', '1', '2']
]);

// Vector B (términos independientes para sistemas)
const vectorB = ref([
  ['8'],
  ['-11'],
  ['-3']
]);

// Sincronizar filas de vectorB con matrixA
watch(() => matrixA.value.length, (newVal) => {
  const currentRows = vectorB.value.length;
  if (currentRows < newVal) {
    const diff = newVal - currentRows;
    const newVector = [...vectorB.value];
    for (let i = 0; i < diff; i++) {
      newVector.push(['0']);
    }
    vectorB.value = newVector;
  } else if (currentRows > newVal) {
    vectorB.value = vectorB.value.slice(0, newVal);
  }
}, { immediate: true });

// Métodos para cambiar dimensiones de la matriz A (para sistema Ax = b)
const addRowA = () => {
  const cols = matrixA.value[0]?.length || 0;
  const newRow = Array(cols).fill('0');
  matrixA.value = [...matrixA.value, newRow];
};

const removeRowA = () => {
  if (matrixA.value.length > 1) {
    matrixA.value = matrixA.value.slice(0, -1);
  }
};

const addColA = () => {
  matrixA.value = matrixA.value.map(row => [...row, '0']);
};

const removeColA = () => {
  if (matrixA.value[0]?.length > 1) {
    matrixA.value = matrixA.value.map(row => row.slice(0, -1));
  }
};

const varNames = ['x', 'y', 'z', 'w', 'u', 'v'];
const getVarName = (idx) => {
  if (idx < varNames.length) return varNames[idx];
  return `x_{${idx + 1}}`;
};

// Matriz B
const matrixB = ref([
  ['1', '0', '0'],
  ['0', '1', '0'],
  ['0', '0', '1']
]);

const loading = ref(false);
const error = ref(null);
const resultSteps = ref(null);

// Historial LocalStorage
const history = ref([]);

const loadHistory = () => {
  const stored = localStorage.getItem('algebrax_history');
  if (stored) {
    try {
      history.value = JSON.parse(stored);
    } catch (e) {
      history.value = [];
    }
  }
};

const saveHistoryItem = (opId, opName, matA, matB) => {
  const vecB = ['gauss', 'cramer', 'least-squares'].includes(opId) ? JSON.parse(JSON.stringify(vectorB.value)) : null;
  const itemKey = JSON.stringify({ opId, matA, matB, vecB });
  const existingIndex = history.value.findIndex(item => 
    JSON.stringify({ opId: item.opId, matA: item.matrixA, matB: item.matrixB, vecB: item.vectorB }) === itemKey
  );
  
  if (existingIndex !== -1) {
    history.value.splice(existingIndex, 1);
  }
  
  history.value.unshift({
    id: Date.now().toString(),
    opId,
    opName,
    matrixA: JSON.parse(JSON.stringify(matA)),
    matrixB: JSON.parse(JSON.stringify(matB)),
    vectorB: vecB
  });
  
  if (history.value.length > 5) {
    history.value.pop();
  }
  
  localStorage.setItem('algebrax_history', JSON.stringify(history.value));
};

const loadHistoryItem = (item) => {
  selectedOperationId.value = item.opId;
  resultSteps.value = null;
  error.value = null;

  let loadedMatrixA = JSON.parse(JSON.stringify(item.matrixA));
  let loadedVectorB = item.vectorB ? JSON.parse(JSON.stringify(item.vectorB)) : null;

  // Soporte para historial antiguo sin vectorB separado
  const systemOps = ['gauss', 'cramer', 'least-squares'];
  if (systemOps.includes(item.opId) && !loadedVectorB) {
    if (loadedMatrixA.length > 0 && loadedMatrixA[0].length > 1) {
      loadedVectorB = loadedMatrixA.map(row => [row[row.length - 1]]);
      loadedMatrixA = loadedMatrixA.map(row => row.slice(0, -1));
    }
  }

  matrixA.value = loadedMatrixA;
  matrixB.value = JSON.parse(JSON.stringify(item.matrixB));
  if (loadedVectorB) {
    vectorB.value = loadedVectorB;
  }
};

const clearHistory = () => {
  history.value = [];
  localStorage.removeItem('algebrax_history');
};

// Visualizador de ecuaciones
const equationsPreview = computed(() => {
  const systemOps = ['gauss', 'cramer', 'least-squares'];
  if (!systemOps.includes(selectedOperationId.value)) return null;
  
  const mat = matrixA.value;
  if (!mat || mat.length === 0 || mat[0].length < 1) return null;
  
  const rows = mat.length;
  const cols = mat[0].length;
  
  let latexLines = [];
  for (let r = 0; r < rows; r++) {
    let lineTerms = [];
    for (let c = 0; c < cols; c++) {
      const val = mat[r][c]?.trim() || '0';
      if (val === '0' || val === '') continue;
      
      let term = '';
      const isNegative = val.startsWith('-');
      const absVal = isNegative ? val.substring(1) : val;
      
      let coef = '';
      if (absVal !== '1') {
        if (absVal.includes('/')) {
          const parts = absVal.split('/');
          coef = `\\frac{${parts[0] || '0'}}{${parts[1] || '1'}}`;
        } else {
          coef = absVal;
        }
      }
      
      const varName = getVarName(c);
      term = `${coef}${varName}`;
      
      if (lineTerms.length > 0) {
        lineTerms.push(isNegative ? ` - ${term}` : ` + ${term}`);
      } else {
        lineTerms.push(isNegative ? `-${term}` : term);
      }
    }
    
    const constant = vectorB.value[r]?.[0]?.trim() || '0';
    let constLatex = constant;
    if (constant.includes('/')) {
      const parts = constant.split('/');
      constLatex = `\\frac{${parts[0] || '0'}}{${parts[1] || '1'}}`;
    }
    
    const leftSide = lineTerms.length > 0 ? lineTerms.join('') : '0';
    latexLines.push(`${leftSide} &= ${constLatex}`);
  }
  
  return `\\begin{aligned}\n${latexLines.join('\\\\\n')}\n\\end{aligned}`;
});

// Copiado e Impresión
const copied = ref(false);
const copyLaTeX = () => {
  if (!resultSteps.value) return;
  let latexText = '';
  
  latexText += `% Reporte generado por AlgebraX\n`;
  latexText += `\\section*{Resolución Paso a Paso: ${selectedOperation.value.name}}\n\n`;
  
  latexText += `\\subsection*{Entrada Original}\n`;
  latexText += `\\[ ${resultSteps.value.original_matrix_latex} \\]\n\n`;
  
  latexText += `\\subsection*{Procedimiento}\n`;
  resultSteps.value.steps.forEach((step, idx) => {
    let descLaTeX = step.description.replace(/\*\*(.*?)\*\*/g, '\\textbf{$1}');
    latexText += `${idx + 1}. ${descLaTeX}\n`;
    if (step.matrix_latex) {
      latexText += `\\[ ${step.matrix_latex} \\]\n`;
    }
    latexText += `\n`;
  });
  
  latexText += `\\subsection*{Resultado Final}\n`;
  latexText += `\\[ ${resultSteps.value.final_matrix_latex} \\]\n\n`;
  
  if (resultSteps.value.solution) {
    latexText += `\\subsection*{Solución del Sistema}\n`;
    latexText += `\\begin{itemize}\n`;
    resultSteps.value.solution.forEach(sol => {
      latexText += `  \\item $${sol}$\n`;
    });
    latexText += `\\end{itemize}\n`;
  }
  
  navigator.clipboard.writeText(latexText).then(() => {
    copied.value = true;
    setTimeout(() => { copied.value = false; }, 2000);
  });
};

const printReport = () => {
  window.print();
};

const solve = async () => {
  loading.value = true;
  error.value = null;
  resultSteps.value = null;
  
  try {
    let payload;
    if (selectedOperation.value.requiresTwo) {
      payload = { matrix: matrixA.value, matrix_b: matrixB.value };
    } else if (isAugmentedOperation.value) {
      // Fusionar matrixA y vectorB en una única matriz aumentada para el backend
      const augmentedMatrix = matrixA.value.map((row, rIdx) => {
        const bVal = vectorB.value[rIdx]?.[0] || '0';
        return [...row, bVal];
      });
      payload = { matrix: augmentedMatrix };
    } else {
      payload = { matrix: matrixA.value };
    }

    const apiBase = window.location.origin.includes('localhost') ? 'http://localhost:8000' : '';
    const response = await fetch(`${apiBase}${selectedOperation.value.endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });
    
    if (!response.ok) {
      const errData = await response.json();
      throw new Error(errData.detail || 'Error en el servidor');
    }
    
    resultSteps.value = await response.json();
    saveHistoryItem(
      selectedOperationId.value,
      selectedOperation.value.name,
      matrixA.value,
      matrixB.value
    );
  } catch (e) {
    error.value = e.message;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadHistory();
});
</script>

<template>
  <div class="min-h-screen bg-slate-50 transition-colors duration-300 font-sans text-slate-800 selection:bg-indigo-500/30 relative">
    
    <!-- Ambient Background Glows (Light Mode) -->
    <div class="fixed inset-0 pointer-events-none overflow-hidden z-0">
      <div class="absolute -top-[20%] -left-[10%] w-[60%] h-[60%] rounded-full bg-indigo-300/30 blur-[120px]"></div>
      <div class="absolute top-[40%] -right-[10%] w-[50%] h-[60%] rounded-full bg-purple-300/20 blur-[120px]"></div>
    </div>

    <div class="container mx-auto px-4 py-12 max-w-5xl text-slate-800 min-h-screen flex flex-col relative z-10">
      
      <!-- Header -->
      <header class="flex justify-between items-center mb-12 print:hidden">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center text-white font-bold text-2xl shadow-[0_8px_20px_rgba(99,102,241,0.25)]">∑</div>
          <h1 class="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 via-purple-600 to-indigo-600 bg-[length:200%_auto] animate-pulse">
            AlgebraX
          </h1>
        </div>
      </header>

      <!-- Layout Stacked -->
      <main class="flex flex-col gap-8 flex-grow w-full max-w-5xl mx-auto">
        
        <!-- Sección Superior: Configuración (Arriba) -->
        <section class="w-full flex flex-col gap-8 print:hidden">
          <div class="glass-panel p-6 sm:p-8 relative overflow-hidden group">
            <div class="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-indigo-500 to-purple-600 opacity-30 group-hover:opacity-100 transition-opacity"></div>
            <h2 class="text-xl sm:text-2xl font-bold mb-6 flex items-center gap-3 text-slate-800">
              <div class="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-600 flex items-center justify-center text-sm shadow-inner border border-indigo-200">1</div>
              Configuración de Operación
            </h2>
            
            <label class="block text-sm font-bold mb-3 text-slate-500 uppercase tracking-wider">Selecciona el Método</label>
            <select v-model="selectedOperationId" class="w-full glass-input mb-2 text-left font-semibold text-lg text-slate-800">
              <option v-for="op in operations" :key="op.id" :value="op.id" class="text-slate-900">
                {{ op.name }}
              </option>
            </select>
          </div>

          <!-- Matrices/Vectores de Entrada -->
          <div class="glass-panel p-6 sm:p-10 flex flex-col items-center justify-center relative overflow-hidden flex-grow shadow-[0_20px_50px_rgba(8,_112,_184,_0.04)]">
            
            <!-- Modo Sistema de Ecuaciones Aumentado -->
            <div v-if="isAugmentedOperation" class="w-full flex flex-col items-center gap-8">
              <!-- Controles de dimensiones unificados -->
              <div class="flex flex-wrap items-center justify-center gap-6">
                <div class="flex items-center gap-2 glass-panel px-5 py-2 !rounded-2xl border-slate-200 bg-white/50">
                  <span class="text-xs font-bold text-slate-500 uppercase tracking-widest mr-2">Filas</span>
                  <button @click="removeRowA" class="text-slate-400 hover:text-indigo-600 font-bold px-3 py-1 transition-colors text-xl" :disabled="matrixA.length <= 1">-</button>
                  <span class="font-mono w-6 text-center text-xl font-bold text-slate-800">{{ matrixA.length }}</span>
                  <button @click="addRowA" class="text-slate-400 hover:text-indigo-600 font-bold px-3 py-1 transition-colors text-xl">+</button>
                </div>

                <div class="flex items-center gap-2 glass-panel px-5 py-2 !rounded-2xl border-slate-200 bg-white/50">
                  <span class="text-xs font-bold text-slate-500 uppercase tracking-widest mr-2">Columnas</span>
                  <button @click="removeColA" class="text-slate-400 hover:text-indigo-600 font-bold px-3 py-1 transition-colors text-xl" :disabled="matrixA[0]?.length <= 1">-</button>
                  <span class="font-mono w-6 text-center text-xl font-bold text-slate-800">{{ matrixA[0]?.length || 0 }}</span>
                  <button @click="addColA" class="text-slate-400 hover:text-indigo-600 font-bold px-3 py-1 transition-colors text-xl">+</button>
                </div>
              </div>

              <!-- Contenedor con scroll -->
              <div class="w-full overflow-x-auto py-6 px-4">
                <!-- Ecuación Matricial A x = b (Centrado seguro) -->
                <div class="flex flex-row items-center gap-4 sm:gap-8 w-max mx-auto">
                  <!-- Matriz A -->
                  <div class="flex flex-col items-center shrink-0">
                    <div class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4 text-center select-none bg-slate-100 px-4 py-1.5 rounded-full shadow-sm border border-slate-200">
                      Matriz A
                    </div>
                    <div class="flex items-center justify-center flex-grow">
                      <MatrixInput v-model="matrixA" :hideControls="true" />
                    </div>
                  </div>
                  
                  <!-- Operador Multiplicación -->
                  <div class="flex flex-col items-center justify-center pt-8 shrink-0">
                    <div class="flex items-center justify-center flex-grow select-none text-indigo-400/50 font-light">
                      <span class="text-3xl sm:text-5xl">×</span>
                    </div>
                  </div>
                  
                  <!-- Vector de Variables X -->
                  <div class="flex flex-col items-center shrink-0">
                    <div class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4 text-center select-none bg-slate-100 px-4 py-1.5 rounded-full shadow-sm border border-slate-200">
                      Variables
                    </div>
                    <div class="flex items-center justify-center flex-grow">
                      <div class="flex flex-col gap-3 items-center justify-center select-none border-l-2 border-r-2 border-slate-300 px-5 py-4 rounded-[2rem] bg-indigo-50/50 font-mono text-indigo-600 font-bold shadow-inner min-w-max backdrop-blur-sm">
                        <div v-for="i in matrixA[0]?.length || 0" :key="i" class="w-8 h-12 sm:h-14 flex items-center justify-center text-lg sm:text-xl text-slate-800">
                          {{ getVarName(i - 1) }}
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="flex flex-col items-center justify-center pt-8 shrink-0">
                    <div class="flex items-center justify-center flex-grow select-none text-indigo-400/50 font-light">
                      <span class="text-3xl sm:text-5xl">=</span>
                    </div>
                  </div>

                  <!-- Vector b -->
                  <div class="flex flex-col items-center shrink-0">
                    <div class="text-[10px] sm:text-xs font-bold text-slate-500 uppercase tracking-widest mb-4 text-center select-none bg-slate-100 px-4 py-1.5 rounded-full shadow-sm border border-slate-200">
                      Vector b
                    </div>
                    <div class="flex items-center justify-center flex-grow">
                      <MatrixInput v-model="vectorB" :hideControls="true" />
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Nota informativa sobre el sistema de ecuaciones -->
              <div class="w-full max-w-lg bg-indigo-50/80 px-6 py-4 rounded-xl border border-indigo-100/50 text-center shadow-sm">
                <p class="text-sm text-slate-600 leading-relaxed">
                  El sistema está expresado en la forma tradicional <strong class="text-indigo-600 font-mono text-base px-1">Ax = b</strong>. La dimensión de <strong class="text-indigo-600 font-mono text-base px-1">b</strong> se sincroniza automáticamente.
                </p>
              </div>
            </div>

            <!-- Modo Entrada Normal (Matriz A simple) -->
            <div v-else class="w-full overflow-x-auto">
              <div class="flex flex-col items-center gap-4 w-max mx-auto py-4 px-2">
                <h3 class="text-xl font-bold mb-2 text-slate-800">Matriz A</h3>
                <MatrixInput v-model="matrixA" />
              </div>
            </div>
            
            <!-- Matriz B Condicional -->
            <div v-if="selectedOperation?.requiresTwo" class="w-full mt-8 pt-8 border-t border-slate-200 overflow-x-auto">
              <div class="flex flex-col items-center gap-4 w-max mx-auto py-4 px-2">
                <h3 class="text-xl font-bold mb-2 text-slate-800">Matriz B</h3>
                <MatrixInput v-model="matrixB" />
              </div>
            </div>

            <!-- Visualizador de Ecuaciones en Tiempo Real -->
            <div v-if="equationsPreview" class="w-full mt-10 pt-8 border-t border-slate-200 text-left">
              <h4 class="text-sm font-bold text-slate-500 mb-4 uppercase tracking-widest text-center">
                Ecuaciones Asociadas
              </h4>
              <div class="p-6 rounded-2xl bg-white/60 border border-slate-200 overflow-x-auto shadow-inner text-lg">
                <MathRenderer :latex="equationsPreview" />
              </div>
            </div>
            
            <button 
              @click="solve" 
              :disabled="loading"
              class="mt-10 btn-primary w-full max-w-md h-14 text-lg font-bold flex justify-center items-center gap-3 transition-transform hover:-translate-y-1"
            >
              <span v-if="loading" class="animate-spin h-6 w-6 border-4 border-white/30 border-t-white rounded-full"></span>
              <span v-else>Resolver Sistema</span>
            </button>
            
            <!-- Alerta de Error Premium -->
            <div v-if="error" class="mt-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-600 text-base font-medium flex items-center justify-center shadow-lg shadow-red-500/5 backdrop-blur-sm">
              <span class="font-bold mr-2">Error:</span>
              <span>{{ error }}</span>
            </div>

          </div>

          <!-- Historial de Operaciones -->
          <div v-if="history.length > 0" class="glass-panel p-6 sm:p-8 relative overflow-hidden group">
            <div class="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-purple-500 to-pink-600 opacity-30 group-hover:opacity-100 transition-opacity"></div>
            <div class="flex justify-between items-center mb-6">
              <h3 class="text-xl font-bold flex items-center gap-3 text-slate-800">
                <div class="w-8 h-8 rounded-lg bg-purple-100 text-purple-600 flex items-center justify-center text-sm shadow-inner border border-purple-200">H</div>
                Historial Reciente
              </h3>
              <button @click="clearHistory" class="text-sm text-red-500 hover:text-red-600 font-semibold transition-colors px-3 py-1 rounded-lg hover:bg-red-50">
                Limpiar todo
              </button>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              <button 
                v-for="item in history" 
                :key="item.id" 
                @click="loadHistoryItem(item)"
                class="text-left p-4 rounded-xl border border-slate-200 bg-white/50 hover:bg-white transition-all duration-300 flex flex-col justify-between group/btn shadow-sm hover:shadow-lg hover:shadow-indigo-500/10 hover:-translate-y-1"
              >
                <span class="font-bold text-slate-700 group-hover/btn:text-indigo-600 transition-colors text-base mb-2 truncate">
                  {{ item.opName }}
                </span>
                <div class="flex justify-between items-center w-full mt-2">
                  <span class="text-xs font-mono font-bold text-slate-500 bg-slate-100 px-2 py-1 rounded-md border border-slate-200">
                    {{ item.matrixA.length }}x{{ item.matrixA[0]?.length }}
                  </span>
                  <span class="text-indigo-600 opacity-0 group-hover/btn:opacity-100 transition-all text-sm font-bold flex items-center gap-1">Cargar <span class="text-lg leading-none">&rarr;</span></span>
                </div>
              </button>
            </div>
          </div>
        </section>

        <!-- Sección Inferior: Resultados y Pasos (Abajo) -->
        <section class="w-full flex flex-col print:w-full mt-4">
          <div class="glass-panel p-6 sm:p-10 flex-grow flex flex-col relative overflow-hidden print:shadow-none print:border-none print:bg-transparent print:p-0">
            <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 opacity-80"></div>
            
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-10 mt-2">
              <h2 class="text-2xl font-bold flex items-center gap-3 text-slate-800">
                <div class="w-10 h-10 rounded-xl bg-indigo-100 text-indigo-600 flex items-center justify-center text-lg shadow-inner border border-indigo-200">2</div>
                Desarrollo y Solución
              </h2>
              <div v-if="resultSteps" class="flex gap-3 print:hidden w-full sm:w-auto">
                <button 
                  @click="copyLaTeX" 
                  class="btn-secondary text-sm px-5 py-2.5 rounded-xl flex items-center gap-2 hover:scale-105 active:scale-95 transition-all flex-grow sm:flex-grow-0 justify-center font-bold"
                >
                  <span>{{ copied ? '¡Copiado!' : 'Copiar LaTeX' }}</span>
                </button>
                <button 
                  @click="printReport" 
                  class="btn-primary text-sm px-5 py-2.5 rounded-xl flex items-center gap-2 hover:scale-105 active:scale-95 transition-all flex-grow sm:flex-grow-0 justify-center font-bold"
                >
                  <span>PDF / Imprimir</span>
                </button>
              </div>
            </div>

            <div v-if="!resultSteps && !loading" class="flex-grow flex flex-col items-center justify-center text-slate-400 py-12 sm:py-24">
              <div class="text-6xl mb-6 opacity-30">∫</div>
              <p class="text-lg text-center px-4 font-medium">Configura las matrices arriba y haz clic en resolver para ver el procedimiento aquí.</p>
            </div>

            <div v-else-if="resultSteps" class="flex-grow space-y-10 print:overflow-visible print:pr-0 pb-8">
              
              <!-- Matriz Original (o Matrices Originales) -->
              <div class="p-6 rounded-2xl bg-slate-100/80 border border-slate-200 print:bg-slate-50 print:border-slate-300">
                <h4 class="text-sm font-bold text-slate-500 mb-4 uppercase tracking-widest text-center">Entrada Original</h4>
                <div class="text-lg">
                  <MathRenderer :latex="resultSteps.original_matrix_latex" />
                </div>
              </div>

              <!-- Pasos -->
              <div v-for="(step, idx) in resultSteps.steps" :key="idx" class="relative pl-8 sm:pl-10 border-l-4 border-indigo-200 print:border-slate-300">
                <div class="absolute -left-[14px] top-1.5 w-6 h-6 rounded-full bg-white border-4 border-indigo-400 print:border-slate-400 print:bg-white flex items-center justify-center shadow-sm">
                  <span class="text-[10px] font-bold text-indigo-600">{{ idx + 1 }}</span>
                </div>
                <p class="text-base sm:text-lg text-slate-700 mb-4 font-medium print:text-black">
                  <InlineMathText :text="step.description" />
                </p>
                <div v-if="step.matrix_latex" class="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm print:bg-white print:border-slate-300 print:shadow-none text-lg">
                  <MathRenderer :latex="step.matrix_latex" />
                </div>
              </div>

              <!-- Matriz/Resultado Final -->
              <div class="p-8 sm:p-10 rounded-[2.5rem] bg-gradient-to-br from-indigo-50/80 to-purple-50/50 border border-indigo-100 shadow-[0_10px_40px_rgba(99,102,241,0.08)] print:bg-slate-50 print:border-slate-300 print:shadow-none mt-16 relative overflow-hidden">
                <div class="absolute top-0 right-0 w-64 h-64 bg-indigo-200/40 rounded-full blur-3xl pointer-events-none"></div>
                <h4 class="text-lg font-black text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 mb-8 uppercase tracking-widest text-center print:text-black">Resultado Final</h4>
                <div class="text-2xl flex justify-center text-slate-900">
                  <MathRenderer :latex="resultSteps.final_matrix_latex" />
                </div>
                
                <div v-if="resultSteps.solution" class="mt-10 pt-10 border-t border-indigo-100 print:border-slate-300 relative">
                  <h4 class="text-base font-black text-indigo-600 mb-8 uppercase tracking-widest text-center print:text-black">Solución del Sistema</h4>
                  <ul class="flex flex-wrap justify-center gap-6">
                    <li v-for="(sol, i) in resultSteps.solution" :key="i" class="bg-white px-8 py-4 rounded-2xl shadow-[0_8px_20px_rgba(0,0,0,0.06)] border border-indigo-100 hover:border-indigo-300 transition-colors">
                      <MathRenderer :latex="sol" :displayMode="false" class="text-2xl font-bold text-slate-900 print:text-black" />
                    </li>
                  </ul>
                </div>
              </div>

            </div>
          </div>
        </section>

      </main>
    </div>
  </div>
</template>

<style>
/* Ocultar barra de desplazamiento global pero permitir scroll */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  @apply bg-slate-300 dark:bg-slate-700;
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  @apply bg-slate-400 dark:bg-slate-600;
}
select option {
  background-color: white;
  color: black;
}
.dark select option {
  background-color: #0f172a;
  color: white;
}

@media print {
  body {
    background: white !important;
    color: black !important;
  }
  .print\:hidden {
    display: none !important;
  }
  main {
    display: block !important;
  }
  .glass-panel {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
  }
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
}
</style>
