import CharacterSprite, {
  CharacterSpriteLayerType,
  CharacterSpriteLayer,
} from '../CharacterSprite';
import { loadCharacterSpriteAssets } from '../characterSpriteLoader';
import SpriteManager, { Sprite } from '../../services/SpriteManager';

jest.mock('../../services/SpriteManager');

const mockSprite: Sprite = {
  image: {} as any,
  width: 32,
  height: 32,
  src: 'mock.png',
};
const mockFrames: Sprite[] = [
  { image: {} as any, width: 32, height: 32, src: 'mock1.png' },
  { image: {} as any, width: 32, height: 32, src: 'mock2.png' },
  { image: {} as any, width: 32, height: 32, src: 'mock3.png' },
];

beforeEach(() => {
  (SpriteManager.getInstance as jest.Mock).mockReturnValue({
    loadSprite: jest.fn().mockResolvedValue(mockSprite),
    loadSpriteSheet: jest.fn().mockResolvedValue(mockFrames),
  });
});

describe('loadCharacterSpriteAssets', () => {
  it('loads all assets for each layer and animation', async () => {
    const layers: CharacterSpriteLayer[] = [
      { type: CharacterSpriteLayerType.Body, z: 0, asset: 'human_male' },
      { type: CharacterSpriteLayerType.Hair, z: 1, asset: 'short_blonde' },
      { type: CharacterSpriteLayerType.Clothing, z: 2, asset: 'shirt_red' },
    ];
    const sprite = new CharacterSprite(layers);
    const loaded = await loadCharacterSpriteAssets(sprite, 'idle');
    expect(loaded[CharacterSpriteLayerType.Body]).toBeDefined();
    expect(loaded[CharacterSpriteLayerType.Hair]).toBeDefined();
    expect(loaded[CharacterSpriteLayerType.Clothing]).toBeDefined();
    expect(loaded[CharacterSpriteLayerType.Body]?.length).toBe(3);
    expect(loaded[CharacterSpriteLayerType.Hair]?.length).toBe(3);
    expect(loaded[CharacterSpriteLayerType.Clothing]?.length).toBe(3);
  });

  it('handles missing variant gracefully', async () => {
    const layers: CharacterSpriteLayer[] = [
      {
        type: CharacterSpriteLayerType.Body,
        z: 0,
        asset: 'nonexistent_variant',
      },
    ];
    const sprite = new CharacterSprite(layers);
    const loaded = await loadCharacterSpriteAssets(sprite, 'idle');
    expect(loaded[CharacterSpriteLayerType.Body]).toBeUndefined();
  });

  it('handles missing animation meta gracefully', async () => {
    const layers: CharacterSpriteLayer[] = [
      { type: CharacterSpriteLayerType.Body, z: 0, asset: 'human_male' },
    ];
    const sprite = new CharacterSprite(layers);
    const loaded = await loadCharacterSpriteAssets(sprite, 'nonexistent_anim');
    expect(loaded[CharacterSpriteLayerType.Body]).toBeUndefined();
  });
});
