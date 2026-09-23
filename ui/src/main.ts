import './swift-hazard-services'
import { createApp } from 'vue'

import '@mdi/font/css/materialdesignicons.css'
import './styles.css'
import App from './App.vue'
import { initializeUiDensity } from './utils/uiDensity'
import vuetify from './vuetify'

initializeUiDensity()

createApp(App).use(vuetify).mount('#app')
import './swift-primary-tabs.css'

import './typography.css'
