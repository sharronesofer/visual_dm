import React from 'react';
import { useCharacterStore } from '../../store/core/characterStore';
import { BodyType, SkinTone } from '../../animation/CharacterCustomization';

/**
 * AppearancePanel provides controls for customizing character appearance (face, skin, hair, etc.).
 * Props will support current values, onChange, and feature locking in the future.
 */
export interface AppearancePanelProps {
    // TODO: Add props for current values, onChange, feature locking, etc.
}

export const AppearancePanel: React.FC<AppearancePanelProps> = (props) => {
    const customization = useCharacterStore(s => s.customization);
    const updateCustomization = useCharacterStore(s => s.updateCustomization);

    // Example: handle body type change
    const handleBodyTypeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        updateCustomization({ bodyType: e.target.value as BodyType });
    };
    // Example: handle skin tone change
    const handleSkinToneChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        updateCustomization({ skinTone: e.target.value as SkinTone });
    };

    return (
        <div>
            <h2 style={{ fontSize: 20, marginBottom: 16 }}>Appearance</h2>
            <div style={{ marginBottom: 16 }}>
                <label style={{ marginRight: 8 }}>Body Type:</label>
                <select value={customization?.bodyType || ''} onChange={handleBodyTypeChange}>
                    {Object.values(BodyType).map(type => (
                        <option key={type} value={type}>{type}</option>
                    ))}
                </select>
            </div>
            <div style={{ marginBottom: 16 }}>
                <label style={{ marginRight: 8 }}>Skin Tone:</label>
                <select value={customization?.skinTone || ''} onChange={handleSkinToneChange}>
                    {Object.values(SkinTone).map(tone => (
                        <option key={tone} value={tone}>{tone}</option>
                    ))}
                </select>
            </div>
            <div>More appearance controls coming soon...</div>
        </div>
    );
};

export default AppearancePanel; 