/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        surface: {
          light: '#eef2f9',
          dark: '#0f1419',
        },
        card: {
          light: 'rgba(255,255,255,0.88)',
          dark: 'rgba(26,31,40,0.82)',
        },
        accent: {
          DEFAULT: '#007AFF',
          soft: '#5AC8FA',
          glow: '#64D2FF',
        },
        ink: {
          light: '#1c1c1e',
          dark: '#f5f5f7',
        },
        muted: {
          light: '#636366',
          dark: '#98989d',
        },
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          '"SF Pro Display"',
          '"SF Pro Text"',
          'system-ui',
          'sans-serif',
        ],
      },
      borderRadius: {
        ios: '14px',
        'ios-lg': '20px',
        'ios-xl': '24px',
      },
      boxShadow: {
        soft: '0 4px 24px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.04)',
        'soft-dark': '0 8px 32px rgba(0, 0, 0, 0.45)',
        lift: '0 12px 40px rgba(0, 122, 255, 0.22)',
        ios: '0 2px 8px rgba(0, 0, 0, 0.08)',
      },
      backdropBlur: {
        glass: '24px',
      },
    },
  },
  plugins: [],
}
