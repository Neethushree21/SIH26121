/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        oil: {
          dark: "#0b0f19",
          panel: "#111827",
          border: "#1f293d",
          accent: "#f59e0b", // Oil amber
          primary: "#0284c7", // Deep engineering blue
          success: "#10b981", // Drilling operational green
          danger: "#ef4444", // Kick / critical hazard red
          warning: "#f97316", // Loss circulation orange
          info: "#06b6d4"
        }
      },
      fontFamily: {
        mono: ["JetBrains Mono", "Fira Code", "Courier New", "monospace"],
        sans: ["Inter", "system-ui", "sans-serif"]
      }
    },
  },
  plugins: [],
}
