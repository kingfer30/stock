<template>
  <div class="concept-list">
    <div 
      v-for="item in data" 
      :key="item.id"
      class="concept-item"
    >
      <div class="concept-header">
        <span class="concept-name">{{ item.name }}</span>
        <span class="concept-value">{{ item.value }}</span>
      </div>
      <n-progress 
        type="line" 
        :percentage="parseFloat(item.value)" 
        :show-indicator="false"
        color="#2196F3"
      />
    </div>
  </div>
</template>

<script setup>
import { NProgress } from 'naive-ui'

defineProps({
  data: {
    type: Array,
    default: () => []
  }
})
</script>

<style scoped>
.concept-list {
  padding: 16px 0;
}

.concept-item {
  margin-bottom: 24px;
}

.concept-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.concept-name {
  font-weight: 500;
  color: #333;
}

.concept-value {
  color: #2196F3;
  font-weight: 500;
}
</style>

