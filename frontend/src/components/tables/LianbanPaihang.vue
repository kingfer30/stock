<template>
  <n-data-table
    :columns="columns"
    :data="data"
    :loading="loading"
    :pagination="{ pageSize: 20 }"
    :bordered="false"
    size="small"
  />
</template>

<script setup>
import { NDataTable } from 'naive-ui'

defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const columns = [
  { title: '代码', key: 'code', width: 100 },
  { title: '名称', key: 'name', width: 120 },
  { title: '涨幅', key: 'change', width: 100 },
  { title: '天数', key: 'days', width: 80 },
  { title: '类型', key: 'type', width: 100 },
  { title: '概念', key: 'concept', width: 200 },
]
</script>

