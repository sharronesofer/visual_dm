import React from 'react';
import { useCharacterStore } from '../../store/core/characterStore';
import { CharacterPresetManager } from '../../animation/CharacterPresetManager';

/**
 * PresetsPanel provides controls for managing character presets (save, load, delete, list).
 * Props will support preset list, onSelect, onSave, onDelete, etc. in the future.
 */
export interface PresetsPanelProps {
    // TODO: Add props for preset list, onSelect, onSave, onDelete, etc.
}

// Stub: In a real app, presets would be loaded from CharacterPresetManager and persisted
const stubPresets = [
    { id: '1', name: 'Dwarf Warrior', customization: {} },
    { id: '2', name: 'Elven Mage', customization: {} },
];

export const PresetsPanel: React.FC<PresetsPanelProps> = (props) => {
    const customization = useCharacterStore(s => s.customization);
    const setCustomization = useCharacterStore(s => s.setCustomization);

    // Example: load a preset (stub logic)
    const handleLoadPreset = (preset: any) => {
        setCustomization(preset.customization);
    };

    // Example: save current customization as a new preset (stub logic)
    const handleSavePreset = () => {
        // In a real app, use CharacterPresetManager.savePreset(...)
        alert('Preset saved! (stub)');
    };

    return (
        <div>
            <h2 style={{ fontSize: 20, marginBottom: 16 }}>Presets</h2>
            <button onClick={handleSavePreset} style={{ marginBottom: 16 }}>Save Current as Preset</button>
            <div>
                <strong>Available Presets:</strong>
                <ul>
                    {stubPresets.map(preset => (
                        <li key={preset.id} style={{ margin: '8px 0' }}>
                            <button onClick={() => handleLoadPreset(preset)}>{preset.name}</button>
                        </li>
                    ))}
                </ul>
            </div>
            <div>More preset management features coming soon...</div>
        </div>
    );
};

export default PresetsPanel; 