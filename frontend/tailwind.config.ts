import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
  	extend: {
  		colors: {
  			background: 'hsl(var(--background))',
  			surface: '#0f172a',
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				glow: '#7c3aed',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			'text-main': '#f8fafc',
  			'text-muted': '#94a3b8',
  			foreground: 'hsl(var(--foreground))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  			chart: {
  				'1': 'hsl(var(--chart-1))',
  				'2': 'hsl(var(--chart-2))',
  				'3': 'hsl(var(--chart-3))',
  				'4': 'hsl(var(--chart-4))',
  				'5': 'hsl(var(--chart-5))'
  			}
  		},
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
  		fontSize: {
  			'lyrics-current': [
  				'48px',
  				{
  					lineHeight: '1.2',
  					fontWeight: '700'
  				}
  			],
  			'lyrics-next': [
  				'24px',
  				{
  					lineHeight: '1.4',
  					fontWeight: '400'
  				}
  			],
  			'page-title': [
  				'30px',
  				{
  					lineHeight: '1.3',
  					fontWeight: '700'
  				}
  			],
  			'song-title': [
  				'20px',
  				{
  					lineHeight: '1.4',
  					fontWeight: '500'
  				}
  			],
  			'song-meta': [
  				'16px',
  				{
  					lineHeight: '1.5',
  					fontWeight: '400'
  				}
  			]
  		},
  		backdropBlur: {
  			glass: '12px'
  		},
  		keyframes: {
  			'fade-in': {
  				'0%': {
  					opacity: '0'
  				},
  				'100%': {
  					opacity: '1'
  				}
  			},
  			'scale-in': {
  				'0%': {
  					transform: 'scale(0.95)',
  					opacity: '0'
  				},
  				'100%': {
  					transform: 'scale(1)',
  					opacity: '1'
  				}
  			},
  			'press': {
  				'0%': {
  					transform: 'scale(1)'
  				},
  				'50%': {
  					transform: 'scale(0.95)'
  				},
  				'100%': {
  					transform: 'scale(1)'
  				}
  			}
  		},
  		animation: {
  			'fade-in': 'fade-in 0.3s ease-out',
  			'scale-in': 'scale-in 0.2s ease-out',
  			press: 'press 0.15s ease-out'
  		}
  	}
  },
  plugins: [require("tailwindcss-animate")],
};
export default config;
