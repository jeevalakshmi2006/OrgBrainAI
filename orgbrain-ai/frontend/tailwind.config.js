/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,jsx}", "./lib/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        navy: "#0f2942",
        steel: "#3b6ea5",
      },
    },
  },
  plugins: [],
};
