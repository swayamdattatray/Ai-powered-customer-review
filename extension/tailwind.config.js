/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/**/*.{js,ts,jsx,tsx,html}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f5ff',
          100: '#e0ecff',
          500: '#2563eb',
          600: '#1d4ed8',
          700: '#1e40af',
          900: '#102a56',
        }
      }
    },
  },
  plugins: [],
}
