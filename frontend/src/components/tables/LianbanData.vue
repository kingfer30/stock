<template>
  <div class="lianban-data">
    <div class="lianban-controls">
      <n-select
        v-model:value="selectedDate"
        :options="dateOptions"
        placeholder="选择查询日期"
        style="width: 200px"
        @update:value="handleDateChange"
      />
      <n-button 
        type="primary" 
        @click="exportToExcel"
        :disabled="data.length === 0 || loading || hasLoadingData"
        style="margin-left: 12px"
      >
        {{ hasLoadingData ? '⏳ 数据加载中...' : '📊 导出表格' }}
      </n-button>
    </div>
    
    <n-data-table
      v-if="data.length > 0"
      :columns="columns"
      :data="data"
      :loading="loading"
      :pagination="{ pageSize: 50 }"
      :bordered="false"
      size="small"
      :scroll-x="2000"
      :row-props="rowProps"
    />
    <n-empty 
      v-else-if="!loading"
      description="暂无连板数据"
      style="margin: 40px 0"
    >
      <template #extra>
        <p>该日期可能没有符合条件的股票</p>
        <p>💡 提示：请尝试选择其他交易日期或等待市场开盘后查看数据</p>
      </template>
    </n-empty>
  </div>
</template>

<script setup>
import { ref, computed, h } from 'vue'
import { NDataTable, NSelect, NEmpty, NSpin, NIcon, NButton, useMessage } from 'naive-ui'
import { CheckmarkCircle, CloseCircle } from '@vicons/ionicons5'

const message = useMessage()

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  tradeDates: {
    type: Array,
    default: () => []
  },
  selectedDate: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:selectedDate', 'dateChange'])

const selectedDate = computed({
  get: () => props.selectedDate,
  set: (value) => emit('update:selectedDate', value)
})

const dateOptions = computed(() => {
  const options = []
  props.tradeDates.forEach(d => {
    // 如果是当前交易日，加上标记
    const label = d.is_current ? `${d.display} (当前)` : d.display
    options.push({ label, value: d.raw })
  })
  return options
})

// 检查是否有正在加载的数据
const hasLoadingData = computed(() => {
  if (!props.data || props.data.length === 0) {
    return false
  }
  
  return props.data.some(row => {
    return row['最大1分钟成交量'] === 'loading' ||
           row['次日竞价涨幅(%)'] === 'loading' ||
           row['次日竞价成交额(亿元)'] === 'loading' ||
           row['次日竞价成交量'] === 'loading' ||
           row['是否晋级'] === 'loading'
  })
})

const handleDateChange = () => {
  emit('dateChange')
}

// 表格列定义
const columns = [
  { title: '连板数', key: '连板数', width: 80, fixed: 'left' },
  { title: '代码', key: '股票代码', width: 100, fixed: 'left' },
  { title: '名称', key: '股票简称', width: 120, fixed: 'left' },
  { title: '成交额(亿元)', key: '成交额(亿元)', width: 120 },
  { title: '封板资金(亿元)', key: '封板资金(亿元)', width: 130 },
  { title: '收盘价(元)', key: '收盘价(元)', width: 110 },
  { title: '成交量(股)', key: '成交量(股)', width: 130 },
  { 
    title: '最大1分钟成交量(万)', 
    key: '最大1分钟成交量', 
    width: 160,
    render(row) {
      if (row['最大1分钟成交量'] === 'loading') {
        return h(NSpin, { size: 'small' })
      }
      return row['最大1分钟成交量']
    }
  },
  { 
    title: '次日竞价涨幅(%)', 
    key: '次日竞价涨幅(%)', 
    width: 140,
    render(row) {
      if (row['次日竞价涨幅(%)'] === 'loading') {
        return h(NSpin, { size: 'small' })
      }
      return row['次日竞价涨幅(%)']
    }
  },
  { 
    title: '次日竞价成交额(亿元)', 
    key: '次日竞价成交额(亿元)', 
    width: 170,
    render(row) {
      if (row['次日竞价成交额(亿元)'] === 'loading') {
        return h(NSpin, { size: 'small' })
      }
      return row['次日竞价成交额(亿元)']
    }
  },
  { 
    title: '次日竞价成交量', 
    key: '次日竞价成交量', 
    width: 140,
    render(row) {
      if (row['次日竞价成交量'] === 'loading') {
        return h(NSpin, { size: 'small' })
      }
      return row['次日竞价成交量']
    }
  },
  { title: '自由流通股本', key: '自由流通股本', width: 140 },
  { title: '自由流通市值(亿)', key: '自由流通市值(亿)', width: 150 },
  { title: '真实换手率%', key: '真实换手率%', width: 120 },
  { title: '量比', key: '量比', width: 100 },
  { 
    title: '是否晋级', 
    key: '是否晋级', 
    width: 100, 
    fixed: 'right',
    render(row) {
      const value = row['是否晋级']
      if (value === 'loading') {
        return h(NSpin, { size: 'small' })
      }
      if (value === '是') {
        return h(NIcon, { 
          size: 20,
          color: '#52c41a'
        }, {
          default: () => h(CheckmarkCircle)
        })
      }
      if (value === '否') {
        return h(NIcon, { 
          size: 20,
          color: '#ff4d4f'
        }, {
          default: () => h(CloseCircle)
        })
      }
      return value
    }
  },
]

// 行样式设置
const rowProps = (row) => {
  if (row['是否晋级'] === '是') {
    return {
      class: 'jinjie-row'
    }
  }
  return {}
}

// 导出Excel功能
const exportToExcel = () => {
  if (!props.data || props.data.length === 0) {
    return
  }
  
  // 检查是否还有数据正在加载
  if (hasLoadingData.value) {
    message.warning('⏳ 数据正在加载中，请稍等片刻后再导出')
    return
  }

  // 定义列标题
  const headers = [
    '连板数',
    '代码',
    '名称',
    '成交额(亿元)',
    '封板资金(亿元)',
    '收盘价(元)',
    '成交量(股)',
    '最大1分钟成交量(万)',
    '次日竞价涨幅(%)',
    '次日竞价成交额(亿元)',
    '次日竞价成交量',
    '自由流通股本',
    '自由流通市值(亿)',
    '真实换手率%',
    '量比',
    '是否晋级'
  ]

  // 构建CSV内容
  let csvContent = '\ufeff' // UTF-8 BOM，确保Excel能正确识别中文
  
  // 添加表头
  csvContent += headers.join(',') + '\n'
  
  // 添加数据行
  props.data.forEach(row => {
    const rowData = [
      row['连板数'] || '',
      row['股票代码'] || '',
      row['股票简称'] || '',
      row['成交额(亿元)'] || '',
      row['封板资金(亿元)'] || '',
      row['收盘价(元)'] || '',
      row['成交量(股)'] || '',
      row['最大1分钟成交量'] === 'loading' ? '-' : (row['最大1分钟成交量'] || ''),
      row['次日竞价涨幅(%)'] === 'loading' ? '-' : (row['次日竞价涨幅(%)'] || ''),
      row['次日竞价成交额(亿元)'] === 'loading' ? '-' : (row['次日竞价成交额(亿元)'] || ''),
      row['次日竞价成交量'] === 'loading' ? '-' : (row['次日竞价成交量'] || ''),
      row['自由流通股本'] || '',
      row['自由流通市值(亿)'] || '',
      row['真实换手率%'] || '',
      row['量比'] || '',
      row['是否晋级'] === 'loading' ? '-' : (row['是否晋级'] || '')
    ]
    
    // 处理包含逗号或双引号的字段
    const processedData = rowData.map(field => {
      const fieldStr = String(field)
      if (fieldStr.includes(',') || fieldStr.includes('"') || fieldStr.includes('\n')) {
        return `"${fieldStr.replace(/"/g, '""')}"`
      }
      return fieldStr
    })
    
    csvContent += processedData.join(',') + '\n'
  })

  // 创建Blob并下载
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  
  // 生成文件名
  const dateStr = props.selectedDate 
    ? props.tradeDates.find(d => d.raw === props.selectedDate)?.display || props.selectedDate
    : '当前交易日'
  const fileName = `连板数据_${dateStr}.csv`
  
  link.setAttribute('href', url)
  link.setAttribute('download', fileName)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  // 显示成功提示
  message.success(`✅ 导出成功！文件名: ${fileName}`)
}
</script>

<style scoped>
.lianban-controls {
  margin-bottom: 16px;
  display: flex;
  align-items: center;
}

/* 晋级行样式 */
:deep(.jinjie-row) {
  background-color: #d9f7be !important;
}

:deep(.jinjie-row td) {
  background-color: #d9f7be !important;
}

:deep(.jinjie-row:hover) {
  background-color: #b7eb8f !important;
}

:deep(.jinjie-row:hover td) {
  background-color: #b7eb8f !important;
}
</style>

