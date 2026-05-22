<script setup>
import { onMounted, ref, watch } from 'vue';
import katex from 'katex';
import 'katex/dist/katex.min.css';

const props = defineProps({
  latex: {
    type: String,
    required: true
  },
  displayMode: {
    type: Boolean,
    default: true
  }
});

const mathContainer = ref(null);

const renderMath = () => {
  if (mathContainer.value && props.latex) {
    try {
      katex.render(props.latex, mathContainer.value, {
        throwOnError: false,
        displayMode: props.displayMode,
      });
    } catch (e) {
      console.error("KaTeX Error:", e);
    }
  }
};

onMounted(renderMath);
watch(() => props.latex, renderMath);
</script>

<template>
  <div ref="mathContainer" class="math-content overflow-x-auto py-2"></div>
</template>

<style scoped>
.math-content {
  /* Scrollbar estético para fórmulas largas */
  scrollbar-width: thin;
  scrollbar-color: rgba(156, 163, 175, 0.5) transparent;
}
.math-content::-webkit-scrollbar {
  height: 6px;
}
.math-content::-webkit-scrollbar-track {
  background: transparent;
}
.math-content::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.5);
  border-radius: 10px;
}
</style>
