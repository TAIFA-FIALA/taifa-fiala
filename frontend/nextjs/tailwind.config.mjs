/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['var(--font-montserrat)', 'Montserrat', 'system-ui', 'sans-serif'], // More modern headline font
        sans: ['var(--font-nunito)', 'Nunito', 'system-ui', 'sans-serif'],           // Clean, friendly body font
        serif: ['var(--font-lora)', 'Georgia', 'serif'],                              // Keep serif as fallback
      },
      colors: {
        // TAIFA-FIALA official color palette
        'taifa': {
          primary: '#0C2340',    // Navy blue (from TAIFA-colour-palette.png)
          secondary: '#FFD100',  // Bright yellow (from TAIFA-colour-palette.png)
          accent: '#4B9CD3',     // Light blue (from Africa-outline-blue.png)
          light: '#F9F7F0',      // Warm light background
          dark: '#2C3E50',       // Dark slate
          lightblue: '#8BB8E8',  // Lighter blue accent (from Africa-outline-blue.png)
          grey: '#A2AAAD',       // Grey (from Africa-outline-grey.png)
        },
        'chart': {
          blue: '#3498DB',
          red: '#E74C3C',
          green: '#27AE60',
          yellow: '#F1C40F',
          purple: '#9B59B6',
          gray: '#95A5A6',
        },
      },
      typography: {
        DEFAULT: {
          css: {
            h1: {
              fontFamily: 'var(--font-lora)',
              color: '#1B365D',
            },
            h2: {
              fontFamily: 'var(--font-lora)',
              color: '#1B365D',
            },
            h3: {
              fontFamily: 'var(--font-lora)',
              color: '#1B365D',
            },
            'figure figcaption': {
              fontStyle: 'italic',
              color: '#666666',
            },
          },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
