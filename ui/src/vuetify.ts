import 'vuetify/styles'
import { createVuetify } from 'vuetify'

export default createVuetify({
  theme: {
    defaultTheme: 'swpcOps',
    themes: {
      swpcOps: {
        dark: true,
        colors: {
          background: '#060b13',
          surface: '#0b1320',
          'surface-bright': '#152236',
          'surface-variant': '#11263d',
          primary: '#5fc7ff',
          secondary: '#3ed19f',
          info: '#89bfff',
          success: '#6cd3a4',
          warning: '#f0c66b',
          error: '#ff8e83',
          'on-background': '#e8eff8',
          'on-surface': '#e8eff8',
        },
      },
    },
  },
  defaults: {
    global: {
      ripple: false,
      style: {
        fontFamily: '"Aptos", "Segoe UI", "DejaVu Sans", sans-serif',
      },
    },
    VCard: {
      elevation: 0,
    },
  },
})
