import React from 'react';
import { useCharacterStore } from '../../store/core/characterStore';
import { MeshSlot } from '../../animation/CharacterCustomization';

/**
 * ArmorPanel provides controls for customizing character armor (slots, colors, materials, etc.).
 * Props will support current values, onChange, and material selection in the future.
 */
export interface ArmorPanelProps {
    // TODO: Add props for current values, onChange, material selection, etc.
}

export const ArmorPanel: React.FC<ArmorPanelProps> = (props) => {
    const customization = useCharacterStore(s => s.customization);
    const updateCustomization = useCharacterStore(s => s.updateCustomization);

    // Helper: update a specific mesh slot
    const handleMeshSlotChange = (index: number, field: keyof MeshSlot, value: string) => {
        if (!customization?.meshSlots) return;
        const updatedSlots = customization.meshSlots.map((slot, i) =>
            i === index ? { ...slot, [field]: value } : slot
        );
        updateCustomization({ meshSlots: updatedSlots });
    };

    return (
        <div>
            <h2 style={{ fontSize: 20, marginBottom: 16 }}>Armor</h2>
            {customization?.meshSlots?.length ? (
                <div>
                    {customization.meshSlots.map((slot, i) => (
                        <div key={i} style={{ marginBottom: 16, padding: 8, background: '#292929', borderRadius: 6 }}>
                            <div><strong>Slot:</strong> {slot.slot}</div>
                            <div style={{ marginTop: 4 }}>
                                <label style={{ marginRight: 8 }}>Mesh Asset:</label>
                                <input
                                    type="text"
                                    value={slot.meshAsset}
                                    onChange={e => handleMeshSlotChange(i, 'meshAsset', e.target.value)}
                                    style={{ width: 200 }}
                                />
                            </div>
                            <div style={{ marginTop: 4 }}>
                                <label style={{ marginRight: 8 }}>Material:</label>
                                <input
                                    type="text"
                                    value={slot.material || ''}
                                    onChange={e => handleMeshSlotChange(i, 'material', e.target.value)}
                                    style={{ width: 120 }}
                                />
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div>No armor slots configured.</div>
            )}
            <div>More armor controls coming soon...</div>
        </div>
    );
};

export default ArmorPanel; 