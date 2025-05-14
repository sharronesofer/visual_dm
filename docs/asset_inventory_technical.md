# Hex-Based Asset Management System - Technical Documentation

## Asset Structure

### Base Directory
```
assets/terrain/
├── base/          # Base terrain sprites
├── features/      # Terrain features (trees, rocks, etc.)
├── overlay/       # Elevation and highlight overlays
├── variations/    # Seasonal and weather variations
├── test_overlays/ # Test results for overlay blending
└── test_all/     # Comprehensive variation tests
```

### Asset Specifications

#### Common Specifications
- Dimensions: 64x64 pixels
- Format: PNG with transparency (RGBA)
- Color Depth: 32-bit (8 bits per channel)

#### Base Terrain Types
- Grass
- Water
- Forest
- Desert
- Snow
- Mountain

Each base terrain has 4 variations (00-03) for visual diversity.

#### Terrain Features
- Trees (4 variations)
- Rocks (4 variations)
- Bushes (4 variations)
- Flowers (4 variations)

#### Terrain Overlays
- Elevation highlights
- Shadow effects
- Edge blending masks

#### Weather/Seasonal Variations

1. Snow Variations
   - White overlay (#FFFFFF)
   - Alpha: 178 (70% opacity)
   - 4 patterns: light dusting to heavy snow

2. Autumn Variations
   - Orange tint (#FFA500)
   - Alpha: 153 (60% opacity)
   - 4 patterns: scattered to dense leaves

3. Rain Variations
   - Droplet color: #1E88E5
   - Puddle color: #1565C0
   - 4 patterns: light to heavy rain

4. Fog Variations
   - Gray color: #B0BEC5
   - Alpha range: 51-153 (20-60% opacity)
   - 4 patterns: light to dense fog

## Technical Implementation

### Image Generation
- Uses Python's Pillow library for image processing
- Implements procedural generation for consistent results
- Maintains alpha channel throughout processing

### Blending System
- Multiplicative blending for color variations
- Additive blending for highlights
- Alpha compositing for overlays

### File Naming Convention
- Base terrains: `terrain_[type]_[variation].png`
- Features: `feature_[type]_[variation].png`
- Overlays: `overlay_[type]_[variation].png`
- Variations: `variation_[type]_[variation].png`

### Performance Considerations
- Optimized PNG compression
- Pre-generated variations to reduce runtime overhead
- Efficient alpha channel handling

## Quality Assurance

### Automated Tests
- Overlay blending verification
- Variation compatibility testing
- Alpha channel validation

### Visual Verification Points
- Proper transparency
- Consistent color palettes
- Smooth blending between elements
- Correct variation patterns

## Asset Usage Guidelines

### Integration
1. Load base terrain first
2. Apply feature overlays
3. Add elevation/shadow effects
4. Apply weather/seasonal variations

### Optimization Tips
- Cache frequently used combinations
- Use sprite batching when possible
- Consider texture atlasing for performance

### Extension Points
- New terrain types can be added following the established pattern
- Additional variations can be implemented using the existing framework
- Custom overlays can be created using the standard specifications 