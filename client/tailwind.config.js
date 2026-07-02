/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#ff2d55',
        dark: '#121212',
        card: '#1a1a1a',
        surface: '#242424',
      },
      animation: {
        'swipe-right': 'swipeRight 0.3s ease-out forwards',
        'swipe-left': 'swipeLeft 0.3s ease-out forwards',
        'swipe-up': 'swipeUp 0.3s ease-out forwards',
        'swipe-down': 'swipeDown 0.3s ease-out forwards',
      },
      keyframes: {
        swipeRight: {
          '0%': { transform: 'translateX(0) rotate(0deg)', opacity: '1' },
          '100%': { transform: 'translateX(150%) rotate(20deg)', opacity: '0' },
        },
        swipeLeft: {
          '0%': { transform: 'translateX(0) rotate(0deg)', opacity: '1' },
          '100%': { transform: 'translateX(-150%) rotate(-20deg)', opacity: '0' },
        },
        swipeUp: {
          '0%': { transform: 'translateY(0) scale(1)', opacity: '1' },
          '100%': { transform: 'translateY(-150%) scale(0.8)', opacity: '0' },
        },
        swipeDown: {
          '0%': { transform: 'translateY(0) scale(1)', opacity: '1' },
          '100%': { transform: 'translateY(150%) scale(0.8)', opacity: '0' },
        },
      },
    },
  },
  plugins: [],
}