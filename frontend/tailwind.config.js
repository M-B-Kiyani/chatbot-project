/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        "metalogics-primary": "#6366f1",
        "metalogics-secondary": "#8b5cf6",
        "metalogics-accent": "#06b6d4",
        "metalogics-dark": "#1e1b4b",
        "metalogics-light": "#f8fafc",
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
