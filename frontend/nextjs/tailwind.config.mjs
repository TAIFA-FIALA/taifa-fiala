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
        // TAIFA-FIALA official color palette from provided scheme
        'taifa': {
          primary: '#3E4B59',    // Dark blue-gray
          secondary: '#F0A621',  // Orange/yellow
          accent: '#007A56',     // Teal green
          light: '#F9FAFB',      // Very light gray
          dark: '#3E4B59',       // Dark blue-gray
          muted: '#6B7280',      // Muted gray
          border: '#F2F2F2',     // Light gray border
          olive: '#5F763B',      // Olive green
          orange: '#BA4D00',     // Dark orange
          yellow: '#F0E68C',     // Light yellow
          red: '#A62E2E',        // Dark red
          white: '#FFFFFF',      // Pure white
        },
        'chart': {
          primary: '#3E4B59',    // Dark blue-gray
          secondary: '#F0A621',  // Orange/yellow
          accent: '#007A56',     // Teal green
          neutral: '#6B7280',    // Gray
          light: '#F9FAFB',      // Very light gray
          success: '#007A56',    // Teal green
          olive: '#5F763B',      // Olive green
          orange: '#BA4D00',     // Dark orange
          yellow: '#F0E68C',     // Light yellow
          red: '#A62E2E',        // Dark red
        },
      },
      typography: {
        DEFAULT: {
          css: {
            h1: {
              fontFamily: 'Inter, system-ui, sans-serif',
              color: '#3E4B59',
              fontWeight: '600',
            },
            h2: {
              fontFamily: 'Inter, system-ui, sans-serif',
              color: '#3E4B59',
              fontWeight: '600',
            },
            h3: {
              fontFamily: 'Inter, system-ui, sans-serif',
              color: '#3E4B59',
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
