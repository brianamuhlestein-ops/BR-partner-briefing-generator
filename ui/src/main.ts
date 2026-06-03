import { createApp } from 'vue'
import VueKonva from 'vue-konva'

import '@mdi/font/css/materialdesignicons.css'
import './styles.css'
import App from './App.vue'
import vuetify from './vuetify'

createApp(App).use(VueKonva).use(vuetify).mount('#app')
