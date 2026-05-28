/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        surface: {
          light: '#f5f7fb',
          dark: '#0f1419',
        },
        card: {
          light: 'rgba(255,255,255,0.85)',
          dark: 'rgba(28,32,40,0.75)',
        },
        accent: {
          DEFAULT: '#3b82f6',
          soft: '#60a5fa',
          glow: '#93c5fd',
        },
        ink: {
          light: '#1f2937',
          dark: '#f3f4f6',
        },
        muted: {
          light: '#6b7280',
          dark: '#9ca3af',
        },
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Display', 'Segoe UI', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 8px 32px rgba(15, 23, 42, 0.08)',
        'soft-dark': '0 8px 32px rgba(0, 0, 0, 0.35)',
        lift: '0 12px 40px rgba(59, 130, 246, 0.15)',
      },
      backdropBlur: {
        glass: '20px',
      },
    },
  },
  plugins: [],
}
