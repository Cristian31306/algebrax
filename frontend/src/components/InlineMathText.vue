<script setup>
import { computed } from 'vue';
import katex from 'katex';
import 'katex/dist/katex.min.css';

const props = defineProps({
  text: {
    type: String,
    required: true
  }
});

// Detectar bloques matemáticos usando el símbolo $
const segments = computed(() => {
  if (!props.text) return [];
  // Divide el texto por el caracter $. 
  // Ej: "A sumar $X$ con $Y$" -> ["A sumar ", "X", " con ", "Y", ""]
  const parts = props.text.split('$');
  
  return parts.map((part, index) => {
    const isMath = index % 2 !== 0; // Las partes impares estaban entre $$
    let htmlContent = '';
    
    if (isMath) {
      try {
        htmlContent = katex.renderToString(part, {
          throwOnError: false,
          displayMode: false, // Inline
        });
      } catch (e) {
        htmlContent = `<span class="text-red-500">${part}</span>`;
      }
    } else {
      // Texto normal (reemplazamos \n por <br> si los hay)
      htmlContent = part;
    }
    
    return {
      isMath,
      htmlContent
    };
  });
});
</script>

<template>
  <span class="inline-math-text">
    <template v-for="(segment, idx) in segments" :key="idx">
      <!-- Usamos v-html para inyectar KaTeX renderizado o texto normal -->
      <span v-if="segment.isMath" v-html="segment.htmlContent" class="mx-1"></span>
      <span v-else>{{ segment.htmlContent }}</span>
    </template>
  </span>
</template>
