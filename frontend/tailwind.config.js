/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#090D16',
        surface: {
          50: '#1A2234',
          100: '#141B2B',
          200: '#0F1523',
          300: '#0B101C',
          border: '#222F49',
          borderLight: '#2C3E61',
        },
        risk: {
          low: '#10B981',        // Emerald
          lowBg: 'rgba(16, 185, 129, 0.12)',
          medium: '#F59E0B',     // Amber
          mediumBg: 'rgba(245, 158, 11, 0.12)',
          high: '#F97316',       // Orange
          highBg: 'rgba(249, 115, 22, 0.12)',
          critical: '#EF4444',   // Crimson
          criticalBg: 'rgba(239, 68, 68, 0.15)',
        },
        accent: {
          cyan: '#06B6D4',
          cyanBg: 'rgba(6, 182, 212, 0.12)',
          indigo: '#6366F1',
          indigoBg: 'rgba(99, 102, 241, 0.12)',
          purple: '#A855F7',
          purpleBg: 'rgba(168, 85, 247, 0.12)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      animation: {
        'pulse-subtle': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
