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
          <JingjiaZhangfu :data="jingjiaZhangfuData" :loading="loading" />
        </n-tab-pane>

        <!-- 竞价跌幅 -->
        <n-tab-pane name="jingjia-down" tab="📉 竞价跌幅">
          <JingjiaDiefu :data="jingjiaDiefuData" :loading="loading" />
        </n-tab-pane>

        <!-- 连板排行 -->
        <n-tab-pane name="lianban-rank" tab="🏆 连板排行">
          <LianbanPaihang :data="mainData.phb_list || []" :loading="loading" />
        </n-tab-pane>

        <!-- 热门概念 -->
        <n-tab-pane name="hot-concept" tab="🔥 热门概念">
          <HotConcept :data="mainData.bace_face_list || []" />
        </n-tab-pane>

        <!-- 连板数据 -->
        <n-tab-pane name="lianban-data" tab="📊 连板数据">
          <LianbanData 
            :data="lianbanData" 
            :loading="loading"
            :trade-dates="tradeDates"
            v-model:selected-date="selectedDate"
            @date-change="handleDateChange"
          />
        </n-tab-pane>
      </n-tabs>
    </n-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { NCard, NTabs, NTabPane, NSwitch, useMessage } from 'naive-ui'
import axios from 'axios'
import MetricCard from './MetricCard.vue'
import JingjiaZhangfu from './tables/JingjiaZhangfu.vue'
import JingjiaDiefu from './tables/JingjiaDiefu.vue'
import LianbanPaihang from './tables/LianbanPaihang.vue'
import HotConcept from './tables/HotConcept.vue'
import LianbanData from './tables/LianbanData.vue'

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

let refreshTimer = null
let countdownTimer = null

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
      
      await new Promise(resolve => setTimeout(resolve, 100))
    }
  }
}

// 获取下一交易日
const getNextTradeDate = () => {
  if (!selectedDate.value) {
    return null
  }
  
  const currentIndex = tradeDates.value.findIndex(d => d.raw === selectedDate.value)
  
  if (currentIndex > 0) {
    return tradeDates.value[currentIndex - 1].raw
  }
  
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
          lianbanData.value[i]['是否晋级'] = response.data.shifoujinjie || ''
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
</style>

