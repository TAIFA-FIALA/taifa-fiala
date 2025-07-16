/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    colors: {
    // Professional modern color palette
    'primary': 'var(--primary)', // #3D84C5 - Professional light blue
    'primary-dark': 'var(--primary-dark)', // #0F1E36 - Deep thoughtful navy
    'secondary': 'var(--secondary)', // #E6B325 - Golden sunshine
    'accent': 'var(--accent)', // #E6B325 - Golden sunshine
    'background': 'var(--background)',
    'foreground': 'var(--foreground)',
    
    // Direct color values for easier usage
    'navy': {
      light: '#1A3559',
      DEFAULT: '#0F1E36',
      dark: '#091528'
    },
    'blue': {
      light: '#5A9BD2',
      DEFAULT: '#3D84C5',
      dark: '#2A6DA8'
    },
    'gold': {
      light: '#F1C54C',
      DEFAULT: '#E6B325',
      dark: '#C99B1D'
    },
    'grey': {
      light: '#A7B5C5',
      DEFAULT: '#8A9BAE',
      dark: '#6E7F92'
    }
    },
  },
  darkMode: 'media', // 'media' (system preference) or 'class' (manual toggle)
}
