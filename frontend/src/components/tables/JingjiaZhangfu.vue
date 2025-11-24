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
  { title: '板块', key: 'plate', width: 150 },
  { title: '竞价涨幅', key: 'jjzf', width: 100 },
  { title: '实际涨幅', key: 'sjzf', width: 100 },
  { title: '竞价金额', key: 'jjje', width: 120 },
  { title: '实际市值', key: 'sjsz', width: 120 },
]
</script>

