using UnityEngine;

/// <summary>
/// Optimized 2D renderer for runtime-generated sprites. Uses SpriteRenderer and supports batching and dynamic updates.
/// </summary>
[RequireComponent(typeof(SpriteRenderer))]
public class OptimizedMeshRenderer : MonoBehaviour
{
    private SpriteRenderer spriteRenderer;

    /// <summary>
    /// The current sprite being rendered.
    /// </summary>
    public Sprite Sprite
    {
        get => spriteRenderer.sprite;
        set => spriteRenderer.sprite = value;
    }

    /// <summary>
    /// The color tint of the sprite.
    /// </summary>
    public Color Color
    {
        get => spriteRenderer.color;
        set => spriteRenderer.color = value;
    }

    void Awake()
    {
        spriteRenderer = GetComponent<SpriteRenderer>();
    }

    /// <summary>
    /// Update the sprite at runtime.
    /// </summary>
    public void SetSprite(Sprite newSprite)
    {
        Sprite = newSprite;
    }

    /// <summary>
    /// Set the color tint at runtime.
    /// </summary>
    public void SetColor(Color newColor)
    {
        Color = newColor;
    }
} 