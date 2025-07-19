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
        display: ['Inter', 'system-ui', 'sans-serif'],        // Clean, modern headings
        body: ['Source Sans Pro', 'system-ui', 'sans-serif'], // Readable body text
        sans: ['Source Sans Pro', 'system-ui', 'sans-serif'], // Default sans-serif
        serif: ['Georgia', 'serif'],                           // Fallback serif
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
              fontFamily: 'Inter, system-ui, sans-serif',
              color: '#1B365D',
              fontWeight: '600',
            },
            h2: {
              fontFamily: 'Inter, system-ui, sans-serif',
              color: '#1B365D',
              fontWeight: '600',
            },
            h3: {
              fontFamily: 'Inter, system-ui, sans-serif',
              color: '#1B365D',
              fontWeight: '600',
            },
            'figure figcaption': {
              fontStyle: 'italic',
              color: '#666666',
              fontFamily: 'Source Sans Pro, system-ui, sans-serif',
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
