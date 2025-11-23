<template>
  <div class="metric-card" :style="{ borderLeftColor: color }">
    <div class="metric-title" :style="{ color: color }">{{ title }}</div>
    <div class="metric-value" :style="{ color: color }">{{ value }}</div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: String,
  color: String
})
</script>

<style scoped>
.metric-card {
  padding: 20px;
  background: white;
  border-radius: 10px;
  border-left: 5px solid;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.metric-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 20px;
  font-weight: 500;
}
</style>

