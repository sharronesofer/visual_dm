from typing import Any, List



  CharacterSpriteLayerType,
  CharacterSpriteLayer,
} from '../CharacterSprite'
describe('CharacterSprite', () => {
  it('constructs with initial layers and orders by z', () => {
    const layers: List[CharacterSpriteLayer] = [
      { type: CharacterSpriteLayerType.Body, z: 0, asset: 'body.png' },
      { type: CharacterSpriteLayerType.Hair, z: 2, asset: 'hair.png' },
      { type: CharacterSpriteLayerType.Clothing, z: 1, asset: 'shirt.png' },
    ]
    const sprite = new CharacterSprite(layers)
    const ordered = sprite.getOrderedLayers()
    expect(ordered.map(l => l.type)).toEqual([
      CharacterSpriteLayerType.Body,
      CharacterSpriteLayerType.Clothing,
      CharacterSpriteLayerType.Hair,
    ])
  })
  it('adds and removes layers', () => {
    const sprite = new CharacterSprite()
    sprite.addLayer({
      type: CharacterSpriteLayerType.Body,
      z: 0,
      asset: 'body.png',
    })
    expect(sprite.getLayer(CharacterSpriteLayerType.Body)).toBeDefined()
    sprite.removeLayer(CharacterSpriteLayerType.Body)
    expect(sprite.getLayer(CharacterSpriteLayerType.Body)).toBeUndefined()
  })
  it('throws on duplicate z-order', () => {
    const sprite = new CharacterSprite()
    sprite.addLayer({
      type: CharacterSpriteLayerType.Body,
      z: 0,
      asset: 'body.png',
    })
    sprite.addLayer({
      type: CharacterSpriteLayerType.Hair,
      z: 1,
      asset: 'hair.png',
    })
    expect(() =>
      sprite.addLayer({
        type: CharacterSpriteLayerType.Clothing,
        z: 1,
        asset: 'shirt.png',
      })
    ).toThrow(/Duplicate z-order/)
  })
  it('getLayer returns correct layer', () => {
    const sprite = new CharacterSprite()
    sprite.addLayer({
      type: CharacterSpriteLayerType.Equipment,
      z: 3,
      asset: 'sword.png',
    })
    expect(sprite.getLayer(CharacterSpriteLayerType.Equipment)?.asset).toBe(
      'sword.png'
    )
  })
  it('handles all standard layer types', () => {
    const sprite = new CharacterSprite()
    Object.values(CharacterSpriteLayerType).forEach((type, i) => {
      sprite.addLayer({ type, z: i, asset: `${type}.png` })
    })
    expect(sprite.getOrderedLayers().length).toBe(
      Object.keys(CharacterSpriteLayerType).length
    )
  })
  it('can set, get, and clear layer tints', () => {
    const sprite = new CharacterSprite()
    sprite.addLayer({
      type: CharacterSpriteLayerType.Body,
      z: 0,
      asset: 'body.png',
    })
    sprite.setLayerTint(CharacterSpriteLayerType.Body, 'rgba(255,0,0,0.5)')
    expect(sprite.getLayerTint(CharacterSpriteLayerType.Body)).toBe(
      'rgba(255,0,0,0.5)'
    )
    sprite.setLayerTint(CharacterSpriteLayerType.Body, {
      r: 0,
      g: 255,
      b: 0,
      a: 0.8,
    })
    expect(sprite.getLayerTint(CharacterSpriteLayerType.Body)).toEqual({
      r: 0,
      g: 255,
      b: 0,
      a: 0.8,
    })
    sprite.clearLayerTint(CharacterSpriteLayerType.Body)
    expect(sprite.getLayerTint(CharacterSpriteLayerType.Body)).toBeUndefined()
  })
})