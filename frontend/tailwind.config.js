/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    colors: {
      neutral: {
        10: '#090e1a',
        20: '#161e33',
        30: '#28324d',
        40: '#3d4866',
        50: '#576280',
        60: '#717c99',
        70: '#8f98b2',
        80: '#b4bacc',
        90: '#d4d9e6',
        94: '#e1e5f0',
        98: '#f0f3fa',
        100: '#ffffff',
      },
      primary: {
        10: '#40000e',
        20: '#67001b',
        30: '#91012a',
        40: '#be003a',
        50: '#dc244c',
        60: '#ff516b',
        70: '#ff8792',
        80: '#ffb2b7',
        90: '#ffdadb',
      },
      secondary: {
        violet: {
          10: '#24005b',
          30: '#5700c9',
          50: '#8547ff',
          70: '#b99aff',
          90: '#eaddff',
        },
      },
    },
    extend: {
      keyframes: {
        shine: {
          '0%': { backgroundPosition: 'left' },
          '100%': { backgroundPosition: 'right' },
        },
      },
      animation: {
        shine: 'shine 1.5s infinite',
      },
    },
  },
  plugins: [],
};
