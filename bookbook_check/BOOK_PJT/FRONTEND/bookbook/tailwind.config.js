/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#FAFAFA',
      },
      fontFamily: {
        sans: ['ptd', '맑은 고딕', 'Malgun Gothic', 'Helvetica', 'AppleSDGothicNeo', 'sans-serif'],
      },
    },
  },
  plugins: [],
}