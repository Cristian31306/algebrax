<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import MatrixInput from './components/MatrixInput.vue';
import MathRenderer from './components/MathRenderer.vue';
import InlineMathText from './components/InlineMathText.vue';

const isDarkMode = ref(true);
const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
};

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
  const varNames = ['x', 'y', 'z', 'w', 'u', 'v'];
  
  const getVarName = (idx) => {
    if (idx < varNames.length) return varNames[idx];
    return `x_{${idx + 1}}`;
  };
  
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
  <div :class="{ 'dark': isDarkMode }" class="min-h-screen transition-colors duration-300 bg-slate-50 dark:bg-slate-950">
    <div class="container mx-auto px-4 py-12 max-w-7xl text-slate-900 dark:text-slate-50 min-h-screen flex flex-col">
      
      <!-- Header -->
      <header class="flex justify-between items-center mb-10 print:hidden">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-lg shadow-indigo-600/30">∑</div>
          <h1 class="text-3xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-600">
            AlgebraX
          </h1>
        </div>
        <button @click="toggleTheme" class="btn-secondary rounded-full p-2 w-10 h-10 flex items-center justify-center">
          <span v-if="isDarkMode">☀️</span>
          <span v-else>🌙</span>
        </button>
      </header>

      <!-- Bento Grid Layout -->
      <main class="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-grow">
        
        <!-- Panel Izquierdo: Configuración (Ocupa 5 columnas) -->
        <section class="lg:col-span-5 flex flex-col gap-6 print:hidden">
          <div class="glass-panel p-6 relative overflow-hidden">
            <h2 class="text-xl font-bold mb-4 flex items-center gap-2">
              <span class="text-indigo-500">1.</span> Configuración
            </h2>
            
            <label class="block text-sm font-medium mb-2 text-slate-600 dark:text-slate-400">Operación a realizar</label>
            <select v-model="selectedOperationId" class="w-full glass-input mb-4 text-left">
              <option v-for="op in operations" :key="op.id" :value="op.id" class="text-slate-900">
                {{ op.name }}
              </option>
            </select>
          </div>

          <!-- Matrices/Vectores de Entrada -->
          <div class="glass-panel p-6 flex flex-col items-center justify-center relative overflow-hidden flex-grow">
            <div class="absolute -top-20 -right-20 w-64 h-64 bg-indigo-500/10 dark:bg-indigo-500/20 rounded-full blur-3xl pointer-events-none"></div>
            
            <!-- Modo Sistema de Ecuaciones Aumentado -->
            <div v-if="isAugmentedOperation" class="w-full flex flex-col items-center gap-6">
              <div class="flex flex-col sm:flex-row items-center justify-center gap-6 w-full">
                <!-- Matriz A -->
                <div class="flex flex-col items-center">
                  <h3 class="text-base font-semibold mb-3 text-slate-600 dark:text-slate-400">Matriz A (Coeficientes)</h3>
                  <MatrixInput v-model="matrixA" />
                </div>
                
                <!-- Operador de ecuación -->
                <div class="hidden sm:flex flex-col items-center justify-center font-mono text-slate-400 dark:text-slate-600 select-none">
                  <span class="text-2xl font-bold">X</span>
                  <span class="text-xl font-bold">=</span>
                </div>
                
                <div class="flex sm:hidden items-center justify-center font-bold text-slate-400 dark:text-slate-600 select-none">
                  <span class="text-xl">=</span>
                </div>

                <!-- Vector b -->
                <div class="flex flex-col items-center">
                  <h3 class="text-base font-semibold mb-3 text-slate-600 dark:text-slate-400">Vector b (Resultado)</h3>
                  <MatrixInput v-model="vectorB" :hideControls="true" />
                </div>
              </div>
              
              <!-- Nota informativa sobre el sistema de ecuaciones -->
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-2 text-center w-full max-w-md flex gap-1 justify-center">
                <span>ℹ️</span>
                <span>El sistema está expresado en la forma <strong>A x = b</strong>. Las dimensiones de <strong>b</strong> se adaptan automáticamente.</span>
              </p>
            </div>

            <!-- Modo Entrada Normal (Matriz A simple) -->
            <div v-else class="w-full flex flex-col items-center">
              <h3 class="text-lg font-semibold mb-4 w-full text-left">Matriz A</h3>
              <MatrixInput v-model="matrixA" />
            </div>
            
            <!-- Matriz B Condicional -->
            <div v-if="selectedOperation?.requiresTwo" class="w-full flex flex-col items-center mt-6 pt-6 border-t border-slate-200 dark:border-slate-800">
              <h3 class="text-lg font-semibold mb-4 w-full text-left">Matriz B</h3>
              <MatrixInput v-model="matrixB" />
            </div>

            <!-- Visualizador de Ecuaciones en Tiempo Real -->
            <div v-if="equationsPreview" class="w-full mt-6 pt-6 border-t border-slate-200 dark:border-slate-800 text-left">
              <h4 class="text-sm font-bold text-slate-500 dark:text-slate-400 mb-2 uppercase tracking-wider">
                Ecuaciones Asociadas
              </h4>
              <div class="p-4 rounded-xl bg-slate-100/50 dark:bg-slate-900/30 border border-slate-200 dark:border-slate-800 overflow-x-auto">
                <MathRenderer :latex="equationsPreview" />
              </div>
            </div>
            
            <button 
              @click="solve" 
              :disabled="loading"
              class="mt-8 btn-primary w-full max-w-xs flex justify-center items-center gap-2"
            >
              <span v-if="loading" class="animate-spin h-5 w-5 border-2 border-white/30 border-t-white rounded-full"></span>
              <span v-else>Resolver</span>
            </button>
            
            <!-- Alerta de Error Premium -->
            <div v-if="error" class="mt-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400 text-sm font-medium flex items-center gap-3 shadow-lg shadow-red-500/5 backdrop-blur-sm">
              <span class="text-base">⚠️</span>
              <span>{{ error }}</span>
            </div>

          </div>

          <!-- Historial de Operaciones -->
          <div v-if="history.length > 0" class="glass-panel p-6 relative overflow-hidden">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-bold flex items-center gap-2">
                📂 Recientes
              </h3>
              <button @click="clearHistory" class="text-xs text-red-500 hover:text-red-600 dark:text-red-400 dark:hover:text-red-300 font-medium transition-colors">
                Limpiar todo
              </button>
            </div>
            <div class="space-y-2">
              <button 
                v-for="item in history" 
                :key="item.id" 
                @click="loadHistoryItem(item)"
                class="w-full text-left p-3 rounded-xl border border-slate-200/50 dark:border-slate-800/50 bg-white/20 dark:bg-slate-900/20 hover:bg-indigo-500/10 dark:hover:bg-indigo-500/20 transition-all duration-200 text-sm flex justify-between items-center group"
              >
                <div class="flex flex-col truncate pr-2">
                  <span class="font-semibold text-slate-800 dark:text-slate-200 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                    {{ item.opName }}
                  </span>
                  <span class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    Matriz {{ item.matrixA.length }}x{{ item.matrixA[0]?.length }}
                  </span>
                </div>
                <span class="text-slate-400 group-hover:text-indigo-500 transition-colors text-xs font-semibold">Cargar</span>
              </button>
            </div>
          </div>
        </section>

        <!-- Panel Derecho: Resultados y Pasos (Ocupa 7 columnas) -->
        <section class="lg:col-span-7 flex flex-col print:col-span-12 print:w-full">
          <div class="glass-panel p-6 flex-grow flex flex-col relative overflow-hidden print:shadow-none print:border-none print:bg-transparent print:p-0">
            <div class="absolute -bottom-20 -left-20 w-64 h-64 bg-purple-500/10 dark:bg-purple-500/20 rounded-full blur-3xl pointer-events-none print:hidden"></div>
            
            <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-6">
              <h2 class="text-xl font-bold flex items-center gap-2">
                <span class="text-indigo-500 print:hidden">2.</span> Procedimiento Paso a Paso
              </h2>
              <div v-if="resultSteps" class="flex gap-2 print:hidden w-full sm:w-auto">
                <button 
                  @click="copyLaTeX" 
                  class="btn-secondary text-xs px-3 py-2 rounded-lg flex items-center gap-1.5 hover:scale-105 active:scale-95 transition-all flex-grow sm:flex-grow-0 justify-center"
                >
                  <span>{{ copied ? '📋 ¡Copiado!' : '📄 LaTeX' }}</span>
                </button>
                <button 
                  @click="printReport" 
                  class="btn-primary text-xs px-3 py-2 rounded-lg flex items-center gap-1.5 hover:scale-105 active:scale-95 transition-all flex-grow sm:flex-grow-0 justify-center"
                >
                  <span>🖨️ PDF / Imprimir</span>
                </button>
              </div>
            </div>

            <div v-if="!resultSteps && !loading" class="flex-grow flex flex-col items-center justify-center text-slate-400 dark:text-slate-500">
              <div class="text-4xl mb-4 opacity-50">∫</div>
              <p>Configura las matrices y haz clic en resolver para ver la magia.</p>
            </div>

            <div v-else-if="resultSteps" class="flex-grow overflow-y-auto pr-2 space-y-8 print:overflow-visible print:max-h-none print:pr-0" style="max-height: 75vh;">
              
              <!-- Matriz Original (o Matrices Originales) -->
              <div class="p-4 rounded-xl bg-slate-100/50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-700 print:bg-slate-50 print:border-slate-300">
                <h4 class="text-sm font-bold text-slate-500 dark:text-slate-400 mb-2 uppercase tracking-wider">Entrada Original</h4>
                <MathRenderer :latex="resultSteps.original_matrix_latex" />
              </div>

              <!-- Pasos -->
              <div v-for="(step, idx) in resultSteps.steps" :key="idx" class="relative pl-6 border-l-2 border-indigo-200 dark:border-indigo-900/50 print:border-slate-300">
                <div class="absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white dark:bg-slate-900 border-2 border-indigo-400 dark:border-indigo-500 print:border-slate-400 print:bg-white"></div>
                <!-- USO DEL NUEVO COMPONENTE InlineMathText -->
                <p class="text-sm text-slate-700 dark:text-slate-300 mb-3 font-medium print:text-black">
                  <InlineMathText :text="step.description" />
                </p>
                <div v-if="step.matrix_latex" class="p-4 rounded-xl bg-white dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 shadow-sm print:bg-white print:border-slate-300 print:shadow-none">
                  <MathRenderer :latex="step.matrix_latex" />
                </div>
              </div>

              <!-- Matriz/Resultado Final -->
              <div class="p-4 rounded-xl bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800/50 shadow-sm print:bg-slate-50 print:border-slate-300 print:shadow-none">
                <h4 class="text-sm font-bold text-indigo-600 dark:text-indigo-400 mb-2 uppercase tracking-wider print:text-black">Resultado Final</h4>
                <MathRenderer :latex="resultSteps.final_matrix_latex" />
                
                <div v-if="resultSteps.solution" class="mt-4 pt-4 border-t border-indigo-200/50 dark:border-indigo-800/50 print:border-slate-300">
                  <h4 class="text-sm font-bold text-indigo-600 dark:text-indigo-400 mb-2 uppercase tracking-wider print:text-black">Solución del Sistema</h4>
                  <ul class="list-disc list-inside space-y-1">
                    <li v-for="(sol, i) in resultSteps.solution" :key="i">
                      <MathRenderer :latex="sol" :displayMode="false" class="inline print:text-black" />
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
  section.lg\:col-span-7 {
    width: 100% !important;
    max-width: 100% !important;
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
