/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  colorDefaults: {
    // Organization branding colors
    'primary': 'var(--primary)', // #428CE2 - Medium Blue
    'primary-dark': 'var(--primary-dark)', // #102F76 - Dark Blue
    'secondary': 'var(--secondary)', // #EEC21D - Gold
    'accent': 'var(--accent)', // #EEC21D - Gold
    'background': 'var(--background)',
    'foreground': 'var(--foreground)',
    
    // Direct color values for easier usage
    'blue': {
      light: '#5a9de8',
      DEFAULT: '#428CE2',
      dark: '#102F76'
    },
    'gold': {
      light: '#f8d248',
      DEFAULT: '#EEC21D',
      dark: '#d9b118'
    }
  },
  darkMode: 'media', // 'media' (system preference) or 'class' (manual toggle)
}
