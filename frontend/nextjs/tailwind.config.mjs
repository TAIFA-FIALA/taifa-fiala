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
        serif: ['var(--font-lora)', 'Georgia', 'serif'],
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
      },
      colors: {
        // Academic color palette
        'scholarly': {
          primary: '#1B365D',    // Deep navy blue
          secondary: '#7B1F1D',  // Burgundy
          accent: '#8B7355',     // Warm brown
          light: '#F5F5F5',      // Light gray
          dark: '#2C3E50',       // Dark slate
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
