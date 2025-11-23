<template>
  <div class="stock-monitor">
    <!-- 头部 -->
    <div class="header">
      <div class="header-content">
        <h1 class="title">📈 股市实时监控看板【{{ mainData.day || '-' }}】</h1>
        <div class="update-time">更新于@ {{ mainData.update_time || '-' }}</div>
      </div>
      <div class="header-actions">
        <n-switch v-model:value="autoRefresh" size="large">
          <template #checked>自动刷新</template>
          <template #unchecked>自动刷新</template>
        </n-switch>
        <span v-if="autoRefresh" class="countdown">{{ countdown }}秒后更新</span>
      </div>
    </div>

    <!-- 关键指标卡片 -->
    <div class="metrics-cards">
      <MetricCard 
        title="今涨停/昨涨停" 
        :value="mainData.da_ban_stats?.zhangting || '-'" 
        color="#F44336"
      />
      <MetricCard 
        title="今跌停/昨跌停" 
        :value="mainData.da_ban_stats?.dieting || '-'" 
        color="#4CAF50"
      />
      <MetricCard 
        title="今封板/昨封板" 
        :value="mainData.da_ban_stats?.fengban || '-'" 
        color="#2196F3"
      />
      <MetricCard 
        title="炸板率/连板率" 
        :value="`${mainData.da_ban_stats?.poban_rate || '-'} / ${mainData.da_ban_stats?.zrlb_jin || '-'}`" 
        color="#2196F3"
      />
      <MetricCard 
        title="上涨/平盘/下跌" 
        :value="mainData.da_ban_stats?.zhangdie || '-'" 
        color="#FF9800"
      />
      <MetricCard 
        title="市场热度" 
        :value="mainData.da_ban_stats?.heat_index || '-'" 
        color="#FF00D4"
      />
    </div>

    <!-- 数据表格 -->
    <n-card class="data-card">
      <n-tabs type="line" animated>
        <!-- 竞价涨幅 -->
        <n-tab-pane name="jingjia-up" tab="📈 竞价涨幅(一进二)">
          <n-data-table
            :columns="jingjiaZhangfuColumns"
            :data="jingjiaZhangfuData"
            :loading="loading"
            :pagination="{ pageSize: 20 }"
            :bordered="false"
            size="small"
          />
        </n-tab-pane>

        <!-- 竞价跌幅 -->
        <n-tab-pane name="jingjia-down" tab="📉 竞价跌幅">
          <n-data-table
            :columns="jingjiaDiefuColumns"
            :data="jingjiaDiefuData"
            :loading="loading"
            :pagination="{ pageSize: 20 }"
            :bordered="false"
            size="small"
          />
        </n-tab-pane>

        <!-- 连板排行 -->
        <n-tab-pane name="lianban-rank" tab="🏆 连板排行">
          <n-data-table
            :columns="lianbianPaihangColumns"
            :data="mainData.phb_list || []"
            :loading="loading"
            :pagination="{ pageSize: 20 }"
            :bordered="false"
            size="small"
          />
        </n-tab-pane>

        <!-- 热门概念 -->
        <n-tab-pane name="hot-concept" tab="🔥 热门概念">
          <div class="concept-list">
            <div 
              v-for="item in mainData.bace_face_list || []" 
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
        </n-tab-pane>

        <!-- 连板数据 -->
        <n-tab-pane name="lianban-data" tab="📊 连板数据">
          <div class="lianban-controls">
            <n-select
              v-model:value="selectedDate"
              :options="dateOptions"
              placeholder="选择查询日期"
              style="width: 200px"
              @update:value="handleDateChange"
            />
          </div>
          
          <n-data-table
            v-if="lianbanData.length > 0"
            :columns="lianbanColumns"
            :data="lianbanData"
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
        </n-tab-pane>
      </n-tabs>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, h } from 'vue'
import { 
  NCard, NTabs, NTabPane, NDataTable, NSwitch, NProgress, 
  NSelect, NEmpty, NSpin, NIcon, useMessage 
} from 'naive-ui'
import { CheckmarkCircle, CloseCircle } from '@vicons/ionicons5'
import axios from 'axios'
import MetricCard from './MetricCard.vue'

const message = useMessage()

// 响应式数据
const mainData = ref({
  bace_face_list: [],
  da_ban_stats: {},
  phb_list: [],
  update_time: '',
  day: ''
})
const jingjiaZhangfuData = ref([])
const jingjiaDiefuData = ref([])
const lianbanData = ref([])
const loading = ref(false)
const autoRefresh = ref(true)
const countdown = ref(20)
const selectedDate = ref(null)
const tradeDates = ref([])
const queryDate = ref('')
const loadingMaxVolume = ref(false)
const maxVolumeLoadedCount = ref(0)

let refreshTimer = null
let countdownTimer = null

// 日期选项
const dateOptions = computed(() => {
  const options = [{ label: '当前交易日', value: null }]
  tradeDates.value.forEach(d => {
    options.push({ label: d.display, value: d.raw })
  })
  return options
})

// 表格列定义
const jingjiaZhangfuColumns = [
  { title: '代码', key: 'code', width: 100 },
  { title: '名称', key: 'name', width: 120 },
  { title: '板块', key: 'plate', width: 150 },
  { title: '竞价涨幅', key: 'jjzf', width: 100 },
  { title: '实际涨幅', key: 'sjzf', width: 100 },
  { title: '竞价金额', key: 'jjje', width: 120 },
  { title: '实际市值', key: 'sjsz', width: 120 },
]

const jingjiaDiefuColumns = [
  { title: '代码', key: 'code', width: 100 },
  { title: '名称', key: 'name', width: 120 },
  { title: '板块', key: 'plate', width: 150 },
  { title: '竞价涨幅', key: 'jjzf', width: 100 },
  { title: '实际涨幅', key: 'sjzf', width: 100 },
]

const lianbianPaihangColumns = [
  { title: '代码', key: 'code', width: 100 },
  { title: '名称', key: 'name', width: 120 },
  { title: '涨幅', key: 'change', width: 100 },
  { title: '天数', key: 'days', width: 80 },
  { title: '类型', key: 'type', width: 100 },
  { title: '概念', key: 'concept', width: 200 },
]

const lianbanColumns = [
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
  const jinjieValue = row['是否晋级']
  console.log('股票:', row['股票简称'], '是否晋级:', jinjieValue, '类型:', typeof jinjieValue)
  
  // 只有当值明确为"是"时才应用绿色背景
  if (jinjieValue === '是') {
    console.log('✓ 应用绿色背景')
    return {
      style: {
        backgroundColor: '#f6ffed',
        transition: 'background-color 0.3s'
      }
    }
  }
  return {
    style: {}
  }
}

// 获取交易日期
const fetchTradeDates = async () => {
  try {
    const response = await axios.get('/api/trade-dates')
    if (response.data.success) {
      tradeDates.value = response.data.data
    }
  } catch (error) {
    console.error('获取交易日期失败:', error)
  }
}

// 获取市场数据
const fetchMarketData = async () => {
  try {
    loading.value = true
    const response = await axios.post('/api/market-data', {
      selected_date: selectedDate.value
    })
    
    if (response.data.success) {
      const data = response.data.data
      mainData.value = data.main
      jingjiaZhangfuData.value = data.jingjiaZhangfu
      jingjiaDiefuData.value = data.jingjiaDiefu
      queryDate.value = data.queryDate
      message.success('数据获取成功！')
    } else {
      message.error('数据获取失败: ' + response.data.error)
    }
  } catch (error) {
    message.error('网络请求失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 获取连板数据
const fetchLianbanData = async () => {
  try {
    loading.value = true
    const response = await axios.post('/api/lianban-data', {
      selected_date: selectedDate.value,
      query_date: queryDate.value
    })
    
    if (response.data.success) {
      lianbanData.value = response.data.data
      
      // 异步加载分时最大成交量和次日竞价数据
      if (lianbanData.value.length > 0) {
        loadMaxVolumeData()
        loadNextDayJingjiaData()
      }
    } else {
      message.error('连板数据获取失败: ' + response.data.error)
    }
  } catch (error) {
    message.error('网络请求失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

// 加载分时最大成交量数据
const loadMaxVolumeData = async () => {
  loadingMaxVolume.value = true
  maxVolumeLoadedCount.value = 0
  
  for (let i = 0; i < lianbanData.value.length; i++) {
    const item = lianbanData.value[i]
    const stockName = item['股票简称']
    
    if (stockName && queryDate.value) {
      try {
        const response = await axios.post('/api/max-volume', {
          stock_name: stockName,
          query_date: queryDate.value
        })
        
        if (response.data.success) {
          lianbanData.value[i]['最大1分钟成交量'] = response.data.volume
        } else {
          lianbanData.value[i]['最大1分钟成交量'] = '❌'
        }
      } catch (error) {
        lianbanData.value[i]['最大1分钟成交量'] = '❌'
      }
      
      maxVolumeLoadedCount.value++
      // 稍微延迟避免请求过快
      await new Promise(resolve => setTimeout(resolve, 100))
    }
  }
  
  loadingMaxVolume.value = false
}

// 获取下一交易日
const getNextTradeDate = () => {
  // 如果没有选择日期（当前交易日），返回null
  if (!selectedDate.value) {
    return null
  }
  
  // 从交易日期列表中找到下一个交易日
  const currentIndex = tradeDates.value.findIndex(d => d.raw === selectedDate.value)
  
  // 如果找到当前日期，且不是第一个（因为列表是倒序的，第一个是最新的）
  if (currentIndex > 0) {
    return tradeDates.value[currentIndex - 1].raw
  }
  
  // 如果是最新的日期或找不到，返回null
  return null
}

// 加载次日竞价数据
const loadNextDayJingjiaData = async () => {
  const nextDate = getNextTradeDate()
  
  for (let i = 0; i < lianbanData.value.length; i++) {
    const item = lianbanData.value[i]
    const stockName = item['股票简称']
    
    if (stockName) {
      try {
        const response = await axios.post('/api/next-day-jingjia', {
          stock_name: stockName,
          next_date: nextDate
        })
        
        if (response.data.success) {
          lianbanData.value[i]['次日竞价涨幅(%)'] = response.data.jingjiaZhangfu || ''
          lianbanData.value[i]['次日竞价成交额(亿元)'] = response.data.jingjiaChengjiaoE || ''
          lianbanData.value[i]['次日竞价成交量'] = response.data.jingjiaChengjiaoL || ''
          const jinjieValue = response.data.shifoujinjie || ''
          lianbanData.value[i]['是否晋级'] = jinjieValue
          console.log(`${stockName} 是否晋级更新为:`, jinjieValue)
        } else {
          lianbanData.value[i]['次日竞价涨幅(%)'] = '❌'
          lianbanData.value[i]['次日竞价成交额(亿元)'] = '❌'
          lianbanData.value[i]['次日竞价成交量'] = '❌'
          lianbanData.value[i]['是否晋级'] = '❌'
        }
      } catch (error) {
        lianbanData.value[i]['次日竞价涨幅(%)'] = '❌'
        lianbanData.value[i]['次日竞价成交额(亿元)'] = '❌'
        lianbanData.value[i]['次日竞价成交量'] = '❌'
        lianbanData.value[i]['是否晋级'] = '❌'
      }
      
      // 稍微延迟避免请求过快
      await new Promise(resolve => setTimeout(resolve, 100))
    }
  }
}

// 日期改变处理
const handleDateChange = async () => {
  await fetchMarketData()
  await fetchLianbanData()
}

// 初始化数据
const initData = async () => {
  await fetchTradeDates()
  await fetchMarketData()
  await fetchLianbanData()
}

// 启动倒计时
const startCountdown = () => {
  if (countdownTimer) clearInterval(countdownTimer)
  countdown.value = 20
  
  countdownTimer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      countdown.value = 20
    }
  }, 1000)
}

// 启动自动刷新
const startAutoRefresh = () => {
  if (refreshTimer) clearInterval(refreshTimer)
  
  refreshTimer = setInterval(() => {
    if (autoRefresh.value) {
      initData()
    }
  }, 20000)
}

// 组件挂载
onMounted(() => {
  initData()
  startCountdown()
  startAutoRefresh()
})

// 组件卸载
onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
  if (countdownTimer) clearInterval(countdownTimer)
})
</script>

<style scoped>
.stock-monitor {
  width: 100%;
  min-height: 100vh;
  padding: 20px;
  background: #f5f5f5;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  flex: 1;
}

.title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0 0 8px 0;
}

.update-time {
  color: #666;
  font-size: 14px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.countdown {
  color: #666;
  font-size: 14px;
}

.metrics-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.data-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

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

.lianban-controls {
  margin-bottom: 16px;
}
</style>


