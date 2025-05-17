using UnityEngine;
using UnityEngine.UI;
using TMPro;
using System;
using System.Collections.Generic;

/// <summary>
/// Manages theme and styling for UI components across the application.
/// This is equivalent to a CSS theme or styled-components in React.
/// </summary>
[CreateAssetMenu(fileName = "UITheme", menuName = "Visual_DM/UI Theme")]
public class UIThemeManager : ScriptableObject
{
    // Color palette
    [Header("Color Palette")]
    public Color primaryColor = new Color(0.11f, 0.11f, 0.11f); // #232323
    public Color secondaryColor = new Color(0.27f, 0.27f, 0.27f); // #444444
    public Color accentColor = new Color(0.12f, 0.53f, 0.9f); // #1E88E5
    public Color textPrimaryColor = Color.white;
    public Color textSecondaryColor = new Color(0.7f, 0.7f, 0.7f);
    public Color backgroundPrimaryColor = new Color(0.11f, 0.11f, 0.11f); // #232323
    public Color backgroundSecondaryColor = new Color(0.15f, 0.15f, 0.15f); // #262626
    
    // Typography
    [Header("Typography")]
    public TMP_FontAsset primaryFont;
    public float headerFontSize = 18f;
    public float bodyFontSize = 14f;
    public float smallFontSize = 12f;
    
    // Spacing
    [Header("Spacing")]
    public float spacingSmall = 8f;
    public float spacingMedium = 16f;
    public float spacingLarge = 24f;
    
    // Border radius
    [Header("Style")]
    public float borderRadius = 4f;
    public float borderWidth = 1f;
    
    // Singleton instance
    private static UIThemeManager _instance;
    public static UIThemeManager Instance
    {
        get
        {
            if (_instance == null)
            {
                _instance = Resources.Load<UIThemeManager>("UITheme");
                if (_instance == null)
                {
                    Debug.LogWarning("UITheme not found in Resources folder. Creating a default theme.");
                    _instance = CreateInstance<UIThemeManager>();
                }
            }
            return _instance;
        }
    }
    
    /// <summary>
    /// Applies theme styles to a button
    /// </summary>
    public void ApplyButtonStyle(Button button, ButtonStyle style = ButtonStyle.Primary)
    {
        if (button == null) return;
        
        // Get or add required components
        Image backgroundImage = button.GetComponent<Image>();
        if (backgroundImage == null) backgroundImage = button.gameObject.AddComponent<Image>();
        
        TextMeshProUGUI text = button.GetComponentInChildren<TextMeshProUGUI>();
        
        // Apply appropriate style based on type
        switch (style)
        {
            case ButtonStyle.Primary:
                backgroundImage.color = accentColor;
                if (text != null) text.color = textPrimaryColor;
                break;
            case ButtonStyle.Secondary:
                backgroundImage.color = secondaryColor;
                if (text != null) text.color = textPrimaryColor;
                break;
            case ButtonStyle.Transparent:
                backgroundImage.color = new Color(0, 0, 0, 0);
                if (text != null) text.color = textPrimaryColor;
                break;
            case ButtonStyle.Selected:
                backgroundImage.color = secondaryColor;
                if (text != null) text.color = accentColor;
                break;
        }
        
        // Round corners if possible
        if (backgroundImage != null)
        {
            // Unity doesn't support border-radius directly in Image
            // For production, you would use a custom image with rounded corners
            // or a custom shader
        }
    }
    
    /// <summary>
    /// Applies theme styles to a panel
    /// </summary>
    public void ApplyPanelStyle(Image panel, PanelStyle style = PanelStyle.Primary)
    {
        if (panel == null) return;
        
        switch (style)
        {
            case PanelStyle.Primary:
                panel.color = backgroundPrimaryColor;
                break;
            case PanelStyle.Secondary:
                panel.color = backgroundSecondaryColor;
                break;
            case PanelStyle.Accent:
                panel.color = accentColor;
                break;
        }
    }
    
    /// <summary>
    /// Applies theme styles to text
    /// </summary>
    public void ApplyTextStyle(TextMeshProUGUI text, TextStyle style = TextStyle.Body)
    {
        if (text == null) return;
        
        text.font = primaryFont;
        
        switch (style)
        {
            case TextStyle.Header:
                text.fontSize = headerFontSize;
                text.color = textPrimaryColor;
                text.fontStyle = FontStyles.Bold;
                break;
            case TextStyle.Subheader:
                text.fontSize = bodyFontSize;
                text.color = textPrimaryColor;
                text.fontStyle = FontStyles.Bold;
                break;
            case TextStyle.Body:
                text.fontSize = bodyFontSize;
                text.color = textPrimaryColor;
                break;
            case TextStyle.Small:
                text.fontSize = smallFontSize;
                text.color = textSecondaryColor;
                break;
        }
    }
    
    // Enum types for different style variations
    public enum ButtonStyle
    {
        Primary,
        Secondary,
        Transparent,
        Selected
    }
    
    public enum PanelStyle
    {
        Primary,
        Secondary,
        Accent
    }
    
    public enum TextStyle
    {
        Header,
        Subheader,
        Body,
        Small
    }
} 