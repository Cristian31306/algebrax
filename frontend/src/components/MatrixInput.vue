<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  modelValue: {
    type: Array,
    required: true
  },
  hideControls: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['update:modelValue']);

const rows = computed(() => props.modelValue.length);
const cols = computed(() => props.modelValue[0]?.length || 0);

const addRow = () => {
  const newRow = Array(cols.value).fill('0');
  emit('update:modelValue', [...props.modelValue, newRow]);
};

const removeRow = () => {
  if (rows.value > 1) {
    const newMatrix = props.modelValue.slice(0, -1);
    emit('update:modelValue', newMatrix);
  }
};

const addCol = () => {
  const newMatrix = props.modelValue.map(row => [...row, '0']);
  emit('update:modelValue', newMatrix);
};

const removeCol = () => {
  if (cols.value > 1) {
    const newMatrix = props.modelValue.map(row => row.slice(0, -1));
    emit('update:modelValue', newMatrix);
  }
};

const updateCell = (rIndex, cIndex, value) => {
  // Crear una copia profunda
  const newMatrix = props.modelValue.map(row => [...row]);
  newMatrix[rIndex][cIndex] = value;
  emit('update:modelValue', newMatrix);
};

const isValidCell = (val) => {
  if (val === undefined || val === null) return false;
  const clean = val.toString().trim().replace(/\s+/g, '');
  if (clean === '') return false;
  
  const numRegex = /^-?\d+(\.\d+)?$/;
  const fracRegex = /^-?\d+(\.\d+)?\/-?\d+(\.\d+)?$/;
  
  if (numRegex.test(clean)) return true;
  if (fracRegex.test(clean)) {
    const parts = clean.split('/');
    const den = parseFloat(parts[1]);
    return den !== 0;
  }
  return false;
};
</script>

<template>
  <div class="flex flex-col items-center gap-4">
    <!-- Controles de dimensión -->
    <div v-if="!hideControls" class="flex flex-wrap items-center justify-center gap-4 mb-4">
      <div class="flex items-center gap-2 glass-panel px-3 py-1">
        <span class="text-sm font-semibold text-slate-500 dark:text-slate-400">Filas:</span>
        <button @click="removeRow" class="text-slate-400 hover:text-indigo-500 font-bold px-2 py-1 transition-colors" :disabled="rows <= 1">-</button>
        <span class="font-mono w-4 text-center">{{ rows }}</span>
        <button @click="addRow" class="text-slate-400 hover:text-indigo-500 font-bold px-2 py-1 transition-colors">+</button>
      </div>

      <div class="flex items-center gap-2 glass-panel px-3 py-1">
        <span class="text-sm font-semibold text-slate-500 dark:text-slate-400">Columnas:</span>
        <button @click="removeCol" class="text-slate-400 hover:text-indigo-500 font-bold px-2 py-1 transition-colors" :disabled="cols <= 1">-</button>
        <span class="font-mono w-4 text-center">{{ cols }}</span>
        <button @click="addCol" class="text-slate-400 hover:text-indigo-500 font-bold px-2 py-1 transition-colors">+</button>
      </div>
    </div>

    <!-- Grid de la matriz -->
    <div class="relative inline-block border-l-2 border-r-2 border-slate-300 dark:border-slate-600 px-4 py-3 bg-slate-50/50 dark:bg-slate-900/20 rounded-2xl shadow-inner">
      <div class="grid gap-3 justify-center" :style="{ gridTemplateColumns: `repeat(${cols}, max-content)` }">
        <template v-for="(row, rIndex) in modelValue" :key="`row-${rIndex}`">
          <div v-for="(cell, cIndex) in row" :key="`cell-${rIndex}-${cIndex}`" class="flex items-center justify-center">
            <input 
              type="text" 
              :value="cell" 
              @input="e => updateCell(rIndex, cIndex, e.target.value)"
              class="glass-input w-16 sm:w-20 h-12 sm:h-14 text-base sm:text-lg font-mono text-center placeholder:text-slate-400 focus:bg-white dark:focus:bg-slate-800 transition-all duration-200 shadow-sm" 
              :class="{ '!border-red-500/80 !focus:ring-red-500/50 bg-red-500/5 dark:bg-red-500/10 text-red-600 dark:text-red-400': !isValidCell(cell) }"
              @focus="$event.target.select()"
            />
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Bordes curvos tipo corchete de matriz */
.border-l-2 {
  border-top-left-radius: 16px;
  border-bottom-left-radius: 16px;
}
.border-r-2 {
  border-top-right-radius: 16px;
  border-bottom-right-radius: 16px;
}
</style>
