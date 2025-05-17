// CustomizationUI.tsx
import React, { useState } from 'react';
import { PreviewPanel } from './PreviewPanel';
import { NavigationSidebar, CustomizationSection } from './NavigationSidebar';
import { UndoRedoBar } from './UndoRedoBar';
import { AppearancePanel } from './AppearancePanel';
import { ArmorPanel } from './ArmorPanel';
import { PresetsPanel } from './PresetsPanel';
import { RandomizerPanel } from './RandomizerPanel';

/**
 * Main entry point for the character customization UI.
 * Layout: NavigationSidebar | MainPanel | PreviewPanel | UndoRedoBar
 */
export const CustomizationUI: React.FC = () => {
    // State for current section (appearance, armor, presets, randomizer, etc.)
    const [section, setSection] = useState<CustomizationSection>('appearance');

    // Undo/redo handlers (stub)
    const handleUndo = () => { /* TODO: implement undo logic */ };
    const handleRedo = () => { /* TODO: implement redo logic */ };

    return (
        <div style={{ display: 'flex', height: '100vh', width: '100vw', background: '#181818' }}>
            {/* Navigation Sidebar */}
            <NavigationSidebar section={section} setSection={setSection} />

            {/* Main Customization Panel */}
            <main style={{ flex: 1, padding: 32, background: '#20232a', color: '#fff', display: 'flex', flexDirection: 'column' }}>
                <h1 style={{ fontSize: 24, marginBottom: 16 }}>Character Customization</h1>
                {/* Section content placeholder */}
                <div style={{ flex: 1, background: '#222', borderRadius: 8, padding: 24, marginBottom: 24 }}>
                    {section === 'appearance' && <AppearancePanel />}
                    {section === 'armor' && <ArmorPanel />}
                    {section === 'presets' && <PresetsPanel />}
                    {section === 'randomizer' && <RandomizerPanel />}
                </div>
                {/* Undo/Redo Bar */}
                <UndoRedoBar onUndo={handleUndo} onRedo={handleRedo} />
            </main>

            {/* Preview Window */}
            <aside style={{ width: 340, background: '#191c1f', display: 'flex', alignItems: 'center', justifyContent: 'center', borderLeft: '1px solid #222' }}>
                {/* Character PreviewPanel integration (TODO: pass model/props) */}
                <PreviewPanel />
            </aside>
        </div>
    );
};

export default CustomizationUI; 