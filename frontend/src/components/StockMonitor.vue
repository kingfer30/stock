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
import { ref, onMounted, onUnmounted, watch } from 'vue'
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

// 自动刷新间隔时间（秒），默认20秒，将从后端配置接口获取
let REFRESH_INTERVAL = Number(import.meta.env.VITE_AUTO_REFRESH_INTERVAL) || 20
const countdown = ref(REFRESH_INTERVAL)

const selectedDate = ref('')
const tradeDates = ref([])
const queryDate = ref('')

let countdownTimer = null

// 获取配置
const fetchConfig = async () => {
  try {
    const response = await axios.get('/api/config')
    if (response.data.success) {
      const config = response.data.config
      // 更新刷新间隔时间
      if (config.auto_refresh_interval) {
        REFRESH_INTERVAL = config.auto_refresh_interval
        countdown.value = REFRESH_INTERVAL
        console.log(`✅ 已加载配置: 自动刷新间隔 ${REFRESH_INTERVAL} 秒`)
      }
    }
  } catch (error) {
    console.warn('⚠️ 获取配置失败，使用默认配置:', error.message)
  }
}

// 监听自动刷新开关变化
watch(autoRefresh, (newValue) => {
  if (newValue) {
    // 开启自动刷新，重新启动定时器
    startAutoRefresh()
  } else {
    // 关闭自动刷新，清除定时器
    if (countdownTimer) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
  }
})

// 获取交易日期
const fetchTradeDates = async () => {
  try {
    const response = await axios.get('/api/trade-dates')
    if (response.data.success) {
      tradeDates.value = response.data.data
      // 默认选择当前交易日
      if (response.data.current_date && !selectedDate.value) {
        selectedDate.value = response.data.current_date
        queryDate.value = response.data.current_date
      }
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
  
  // tradeDates数组是从新到旧排序（降序），所以下一交易日在前面（index - 1）
  // 例如: [20251124(新), 20251122, 20251121(旧)]
  // 选择20251121(index=2)，下一交易日是20251122(index=1)
  if (currentIndex > 0) {
    return tradeDates.value[currentIndex - 1].raw
  }
  
  // 如果是最新的交易日(index=0)，则没有下一交易日
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
          lianbanData.value[i]['次日竞价涨幅(%)'] = response.data.jingjiaZhangfu ?? ''
          lianbanData.value[i]['次日竞价成交额(亿元)'] = response.data.jingjiaChengjiaoE ?? ''
          lianbanData.value[i]['次日竞价成交量'] = response.data.jingjiaChengjiaoL ?? ''
          lianbanData.value[i]['是否晋级'] = response.data.shifoujinjie ?? ''
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
  
  // 连板数据不自动刷新，只在用户手动切换日期时更新
  // 如果需要加载连板数据，请在 onMounted 中单独调用 fetchLianbanData()
}

// 启动自动刷新和倒计时
const startAutoRefresh = () => {
  // 清除旧的定时器
  if (countdownTimer) clearInterval(countdownTimer)
  
  // 重置倒计时
  countdown.value = REFRESH_INTERVAL
  
  // 启动倒计时（每秒更新一次）
  countdownTimer = setInterval(() => {
    if (autoRefresh.value) {
      countdown.value--
      
      // 倒计时到0时刷新数据
      if (countdown.value <= 0) {
        countdown.value = REFRESH_INTERVAL
        initData()
      }
    }
  }, 1000)
}

// 组件挂载
onMounted(async () => {
  // 检查运行期限
  const now = new Date()
  const expireDate = new Date('2026-12-31T23:59:59')
  if (now > expireDate) {
    message.error('程序已过期，请联系开发者更新')
    throw new Error('Program expired')
  }
  
  // 首先获取配置
  await fetchConfig()
  // 然后初始化数据
  await initData()
  // 首次加载时获取一次连板数据，之后自动刷新不再获取
  await fetchLianbanData()
  // 启动自动刷新
  startAutoRefresh()
})

// 组件卸载
onUnmounted(() => {
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

