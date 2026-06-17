/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  future: { hoverOnlyWhenSupported: true },
  theme: {
    screens: {
      xs: '375px',
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
      '2xl': '1536px',
    },
    extend: {
      colors: {
        // ── Uganda Black (primary UI – headers, text, dark surfaces) ──────
        navy: {
          DEFAULT: '#1A1A1A',
          50:  '#F5F5F5',
          100: '#E8E8E8',
          200: '#CCCCCC',
          600: '#2D2D2D',
          700: '#1A1A1A',   // primary dark: Uganda charcoal-black
          800: '#111111',
          900: '#050505',
        },
        // ── Uganda Yellow (accent, highlights, active states) ─────────────
        gold: {
          DEFAULT: '#F5C000',
          50:  '#FFFCE6',
          100: '#FFF3B0',
          200: '#FFE566',
          400: '#F5D000',
          500: '#F5C000',   // Uganda flag yellow
          600: '#D4A400',
        },
        // ── Uganda Red (secondary CTA, important actions, danger) ─────────
        ug: {
          red:      '#C8102E',   // Uganda flag crimson
          redDark:  '#A50D25',
          redLight: '#FDE8EB',
        },
        // ── Semantic status colours ───────────────────────────────────────
        status: {
          green:    '#1F6F3F',
          orange:   '#B85800',
          red:      '#C8102E',   // Uganda red doubles as error colour
          blue:     '#1A4F8A',
          greenBg:  '#E8F5EE',
          orangeBg: '#FFF0E0',
          redBg:    '#FDE8EB',
          blueBg:   '#E8F0F8',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
      },
      fontSize: {
        '2xs': ['0.625rem', { lineHeight: '0.875rem' }],
      },
      spacing: {
        safe: 'env(safe-area-inset-bottom)',
      },
      minHeight: {
        touch: '44px',
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        card:       '0 1px 3px 0 rgb(0 0 0 / 0.08), 0 1px 2px -1px rgb(0 0 0 / 0.05)',
        'card-hover':'0 4px 12px 0 rgb(0 0 0 / 0.12), 0 2px 4px -2px rgb(0 0 0 / 0.06)',
        nav:        '0 2px 8px 0 rgb(0 0 0 / 0.25)',
      },
      animation: {
        'fade-in':    'fadeIn 0.2s ease-out',
        'slide-up':   'slideUp 0.25s ease-out',
        'slide-down': 'slideDown 0.2s ease-out',
        'skeleton':   'skeleton 1.5s ease-in-out infinite',
        'pulse-slow': 'pulseSlow 2s ease-in-out infinite',
        'spin-slow':  'spin 3s linear infinite',
      },
      keyframes: {
        fadeIn:    { from: { opacity: '0' },             to: { opacity: '1' } },
        slideUp:   { from: { opacity: '0', transform: 'translateY(8px)' },  to: { opacity: '1', transform: 'translateY(0)' } },
        slideDown: { from: { opacity: '0', transform: 'translateY(-8px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
        skeleton:  {
          '0%, 100%': { backgroundPosition: '200% 0' },
          '50%':      { backgroundPosition: '-200% 0' },
        },
        pulseSlow: { '0%, 100%': { opacity: '1' }, '50%': { opacity: '0.5' } },
      },
      transitionDuration: { '250': '250ms' },
      zIndex: { '60': '60', '70': '70', '80': '80' },
    },
  },
  plugins: [],
};
