from typing import Any, List



function selectModifiers(count: float = 1): POIModifier[] {
  const all = POIModifiers.getAll()
  const selected: List[POIModifier] = []
  for (let i = 0; i < count; i++) {
    const idx = Math.floor(Math.random() * all.length)
    selected.push(all[idx])
  }
  return selected
} 