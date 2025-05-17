// MaterialTooltip.tsx
import React from 'react';
import { Material } from './types';

interface MaterialTooltipProps {
    material: Material;
}

export const MaterialTooltip: React.FC<MaterialTooltipProps> = ({ material }) => {
    return (
        <div style={{
            background: 'rgba(40,40,40,0.95)',
            color: '#fff',
            borderRadius: 8,
            padding: 12,
            minWidth: 180,
            boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
            fontSize: 14
        }}>
            <div style={{ fontWeight: 'bold', marginBottom: 6 }}>{material.name}</div>
            <div>Durability: {material.durability}</div>
            <div>Cost: {material.cost}</div>
            <div>Aesthetics: {material.aesthetics}</div>
            {material.specialProperties && material.specialProperties.length > 0 && (
                <div style={{ marginTop: 8 }}>
                    <div style={{ fontWeight: 'bold' }}>Special Properties:</div>
                    <ul style={{ margin: 0, paddingLeft: 16 }}>
                        {material.specialProperties.map((prop) => (
                            <li key={prop.name}>
                                {prop.name}: {prop.value}
                                {prop.description ? ` – ${prop.description}` : ''}
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}; 