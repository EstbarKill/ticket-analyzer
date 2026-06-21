/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "#F6F5F1",
        surface: "#FFFFFF",
        ink: "#1E1C1A",
        muted: "#6B6862",
        line: "#E6E3DC",
        accent: {
          DEFAULT: "#B5502E",
          soft: "#F1DCD2",
        },
        priority: {
          low: "#5B7A6B",
          medium: "#3E6FA3",
          high: "#C2792B",
          critical: "#B5502E",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
      borderRadius: {
        sm: "4px",
        md: "6px",
        lg: "10px",
      },
    },
  },
  plugins: [],
};
