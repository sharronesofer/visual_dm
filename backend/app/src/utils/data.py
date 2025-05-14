from typing import Any, List


/**
 * Data manipulation utilities
 */
const deepClone = <T>(obj: T): T => {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }
  if (Array.isArray(obj)) {
    return obj.map(deepClone) as unknown as T
  }
  return Object.fromEntries(
    Object.entries(obj).map(([key, value]) => [key, deepClone(value)])
  ) as T
}
const deepMerge = <T extends object>(target: T, ...sources: Partial<T>[]): T => {
  if (!sources.length) {
    return target
  }
  const source = sources.shift()
  if (source === undefined) {
    return target
  }
  if (isObject(target) && isObject(source)) {
    Object.keys(source).forEach(key => {
      if (isObject(source[key])) {
        if (!target[key]) {
          Object.assign(target, { [key]: {} })
        }
        deepMerge(target[key] as object, source[key] as object)
      } else {
        Object.assign(target, { [key]: source[key] })
      }
    })
  }
  return deepMerge(target, ...sources)
}
const pick = <T extends object, K extends keyof T>(obj: T, keys: List[K]): Pick<T, K> => {
  const result = {} as Pick<T, K>
  keys.forEach(key => {
    if (key in obj) {
      result[key] = obj[key]
    }
  })
  return result
}
const omit = <T extends object, K extends keyof T>(obj: T, keys: List[K]): Omit<T, K> => {
  const result = { ...obj }
  keys.forEach(key => {
    delete result[key]
  })
  return result
}
const groupBy = <T>(array: List[T], key: keyof T): Record<string, T[]> => {
  return array.reduce(
    (result, item) => {
      const groupKey = String(item[key])
      if (!result[groupKey]) {
        result[groupKey] = []
      }
      result[groupKey].push(item)
      return result
    },
    {} as Record<string, T[]>
  )
}
const sortBy = <T>(array: List[T], key: keyof T, order: 'asc' | 'desc' = 'asc'): T[] => {
  return [...array].sort((a, b) => {
    const aValue = a[key]
    const bValue = b[key]
    if (aValue === bValue) {
      return 0
    }
    if (aValue === null || aValue === undefined) {
      return order === 'asc' ? 1 : -1
    }
    if (bValue === null || bValue === undefined) {
      return order === 'asc' ? -1 : 1
    }
    return order === 'asc' ? (aValue < bValue ? -1 : 1) : aValue < bValue ? 1 : -1
  })
}
const unique = <T>(array: List[T]): T[] => Array.from(new Set(array))
const chunk = <T>(array: List[T], size: float): T[][] => {
  return array.reduce((chunks, item, index) => {
    const chunkIndex = Math.floor(index / size)
    if (!chunks[chunkIndex]) {
      chunks[chunkIndex] = []
    }
    chunks[chunkIndex].push(item)
    return chunks
  }, [] as T[][])
}
const capitalize = (str: str): str => {
  if (!str) {
    return str
  }
  return str.charAt(0).toUpperCase() + str.slice(1)
}
const camelCase = (str: str): str => {
  return str
    .replace(/[^a-zA-Z0-9]+(.)/g, (_, chr) => chr.toUpperCase())
    .replace(/^[A-Z]/, chr => chr.toLowerCase())
}
const kebabCase = (str: str): str => {
  return str
    .replace(/([a-z])([A-Z])/g, '$1-$2')
    .replace(/[\s_]+/g, '-')
    .toLowerCase()
}
const snakeCase = (str: str): str => {
  return str
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[\s-]+/g, '_')
    .toLowerCase()
}
const isObject = (value: unknown): value is object => {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}