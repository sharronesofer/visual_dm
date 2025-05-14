import CharacterSpriteAnimator from '../CharacterSpriteAnimator';
import { CharacterSpriteLayerType } from '../CharacterSprite';
import { Sprite } from '../../services/SpriteManager';
import * as SpriteManager from '../../services/SpriteManager';

describe('CharacterSpriteAnimator', () => {
  const spriteA: Sprite = {
    image: {} as any,
    width: 32,
    height: 32,
    src: 'A.png',
  };
  const spriteB: Sprite = {
    image: {} as any,
    width: 32,
    height: 32,
    src: 'B.png',
  };
  const spriteC: Sprite = {
    image: {} as any,
    width: 32,
    height: 32,
    src: 'C.png',
  };
  const spriteD: Sprite = {
    image: {} as any,
    width: 32,
    height: 32,
    src: 'D.png',
  };

  it('returns correct frame for each tick, looping as needed', () => {
    const assets = {
      [CharacterSpriteLayerType.Body]: [spriteA, spriteB, spriteC],
      [CharacterSpriteLayerType.Hair]: [spriteD],
    };
    const animator = new CharacterSpriteAnimator(assets);
    // Body has 3 frames, Hair has 1
    expect(animator.getFrameForTick(0)[CharacterSpriteLayerType.Body]).toBe(
      spriteA
    );
    expect(animator.getFrameForTick(1)[CharacterSpriteLayerType.Body]).toBe(
      spriteB
    );
    expect(animator.getFrameForTick(2)[CharacterSpriteLayerType.Body]).toBe(
      spriteC
    );
    expect(animator.getFrameForTick(3)[CharacterSpriteLayerType.Body]).toBe(
      spriteA
    );
    expect(animator.getFrameForTick(4)[CharacterSpriteLayerType.Body]).toBe(
      spriteB
    );
    // Hair always returns the only frame
    expect(animator.getFrameForTick(0)[CharacterSpriteLayerType.Hair]).toBe(
      spriteD
    );
    expect(animator.getFrameForTick(5)[CharacterSpriteLayerType.Hair]).toBe(
      spriteD
    );
  });

  it('applies tints using applyTintToSprite if provided', () => {
    const assets = {
      [CharacterSpriteLayerType.Body]: [spriteA],
      [CharacterSpriteLayerType.Hair]: [spriteD],
    };
    const animator = new CharacterSpriteAnimator(assets);
    const tintedSprite: Sprite = {
      image: {} as any,
      width: 32,
      height: 32,
      src: 'A.png#tint=red',
    };
    const spy = jest
      .spyOn(SpriteManager, 'applyTintToSprite')
      .mockReturnValue(tintedSprite);
    const tints = { [CharacterSpriteLayerType.Body]: 'red' };
    const frameMap = animator.getFrameForTick(0, tints);
    expect(spy).toHaveBeenCalledWith(spriteA, 'red');
    expect(frameMap[CharacterSpriteLayerType.Body]).toBe(tintedSprite);
    expect(frameMap[CharacterSpriteLayerType.Hair]).toBe(spriteD);
    spy.mockRestore();
  });

  it('handles empty or missing frames gracefully', () => {
    const assets = {
      [CharacterSpriteLayerType.Body]: [],
      [CharacterSpriteLayerType.Hair]: undefined,
    };
    const animator = new CharacterSpriteAnimator(assets);
    expect(
      animator.getFrameForTick(0)[CharacterSpriteLayerType.Body]
    ).toBeUndefined();
    expect(
      animator.getFrameForTick(0)[CharacterSpriteLayerType.Hair]
    ).toBeUndefined();
  });
});
