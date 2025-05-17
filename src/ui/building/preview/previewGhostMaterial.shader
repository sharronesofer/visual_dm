// previewGhostMaterial.shader
// Pseudocode for a ghosted building preview material
// Replace with engine-specific shader code (GLSL, HLSL, ShaderLab, etc.)

// Uniforms:
//   uniform vec4 previewColor; // RGBA color (set by validation status)
//   uniform float pulseTime;   // For pulsing animation

void main() {
    // Base color with alpha for transparency
    vec4 color = previewColor;
    // Pulse effect: modulate alpha with sine wave
    float pulse = 0.85 + 0.15 * sin(pulseTime * 6.2831); // 0.7-1.0 range
    color.a *= pulse;
    // Output color
    gl_FragColor = color;
    // Optionally add edge highlighting here
} 