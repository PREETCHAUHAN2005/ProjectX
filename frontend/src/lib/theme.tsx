import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

export type Theme = 'light' | 'dark'

const STORAGE_KEY = 'projectx-theme'

function readStoredTheme(): Theme | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored === 'light' || stored === 'dark') {
      return stored
    }
  } catch {
    return null
  }
  return null
}

/** First visit is light; later visits use `projectx-theme` in localStorage. */
function preferredTheme(): Theme {
  return 'light'
}

export function applyTheme(theme: Theme): void {
  const root = document.documentElement
  root.classList.toggle('dark', theme === 'dark')
  root.style.colorScheme = theme
}

type ThemeContextValue = {
  theme: Theme
  setTheme: (theme: Theme) => void
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextValue | null>(null)

export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => {
    if (typeof window === 'undefined') {
      return 'light'
    }
    const initial = readStoredTheme() ?? preferredTheme()
    applyTheme(initial)
    return initial
  })

  useEffect(() => {
    applyTheme(theme)
    try {
      localStorage.setItem(STORAGE_KEY, theme)
    } catch {
      // private mode — theme still applies for the session
    }
  }, [theme])

  const value = useMemo(
    () => ({
      theme,
      setTheme: setThemeState,
      toggleTheme: () => {
        setThemeState((current) => (current === 'dark' ? 'light' : 'dark'))
      },
    }),
    [theme],
  )

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
}

export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext)
  if (context === null) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}

export function useChartColors(): {
  grid: string
  tick: string
  legend: string
  canvas: string
  ink: string
  link: string
  nodeStroke: string
  mapFill: string
} {
  const { theme } = useTheme()
  if (theme === 'dark') {
    return {
      grid: '#2d3340',
      tick: '#9aa3b2',
      legend: '#e8edf5',
      canvas: '#161920',
      ink: '#e8edf5',
      link: 'rgba(232,237,245,0.16)',
      nodeStroke: '#1e222b',
      mapFill: '#161920',
    }
  }
  return {
    grid: '#ece7df',
    tick: '#6b645c',
    legend: '#1c1917',
    canvas: '#f7f4ee',
    ink: '#1c1917',
    link: 'rgba(28,25,23,0.16)',
    nodeStroke: '#ffffff',
    mapFill: '#efebe3',
  }
}
