<template>
  <n-config-provider :theme-overrides="themeOverrides">
    <n-message-provider>
      <n-loading-bar-provider>
        <n-notification-provider>
          <n-dialog-provider>
            <StockMonitor />
          </n-dialog-provider>
        </n-notification-provider>
      </n-loading-bar-provider>
    </n-message-provider>
  </n-config-provider>
</template>

<script setup>
import { NConfigProvider, NMessageProvider, NLoadingBarProvider, NNotificationProvider, NDialogProvider } from 'naive-ui'
import StockMonitor from './components/StockMonitor.vue'

const themeOverrides = {
  common: {
    primaryColor: '#2196F3',
    primaryColorHover: '#42A5F5',
    primaryColorPressed: '#1976D2'
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f5f5f5;
}

#app {
  width: 100%;
  min-height: 100vh;
}
</style>

