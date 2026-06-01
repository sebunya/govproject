/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: '#1F3864',
          50: '#E8EEF7',
          100: '#C5D2E8',
          700: '#1F3864',
          900: '#0F1D38',
        },
        gold: {
          DEFAULT: '#BF8F00',
          50: '#FFF5DC',
          100: '#FFE89A',
          500: '#BF8F00',
        },
        status: {
          green: '#1F6F3F',
          orange: '#B85800',
          red: '#C00000',
          greenBg: '#E8F5EE',
          orangeBg: '#FFF0E0',
          redBg: '#FAEAEA',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
