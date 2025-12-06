export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        glow: {
          '0%': {
            boxShadow: '0 0 20px rgba(168, 85, 247, 0.4)',
            filter: 'brightness(1)'
          },
          '100%': {
            boxShadow: '0 0 40px rgba(168, 85, 247, 0.8)',
            filter: 'brightness(1.2)'
          },
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],

      }
    },
  },
  plugins: [],
}