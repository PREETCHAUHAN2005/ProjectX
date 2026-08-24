export type LoadState<T> = {
  status: 'loading' | 'empty' | 'ready' | 'error'
  data: T | null
  error: string | null
}

export function initialLoad<T>(): LoadState<T> {
  return { status: 'loading', data: null, error: null }
}

export function fromResult<T>(data: T, isEmpty: boolean): LoadState<T> {
  if (isEmpty) {
    return { status: 'empty', data, error: null }
  }
  return { status: 'ready', data, error: null }
}
