import React from 'react';

export type CustomizationSection = 'appearance' | 'armor' | 'presets' | 'randomizer';

export interface NavigationSidebarProps {
    section: CustomizationSection;
    setSection: (section: CustomizationSection) => void;
}

/**
 * NavigationSidebar provides navigation between customization categories.
 */
export const NavigationSidebar: React.FC<NavigationSidebarProps> = ({ section, setSection }) => (
    <nav style={{ width: 200, background: '#232323', color: '#fff', padding: 16 }}>
        <h2 style={{ fontSize: 18, marginBottom: 24 }}>Customize</h2>
        <ul style={{ listStyle: 'none', padding: 0 }}>
            <li style={{ marginBottom: 12 }}>
                <button aria-label="Appearance" style={{ width: '100%', background: section === 'appearance' ? '#444' : 'none', color: '#fff', border: 'none', padding: 8, borderRadius: 4 }} onClick={() => setSection('appearance')}>Appearance</button>
            </li>
            <li style={{ marginBottom: 12 }}>
                <button aria-label="Armor" style={{ width: '100%', background: section === 'armor' ? '#444' : 'none', color: '#fff', border: 'none', padding: 8, borderRadius: 4 }} onClick={() => setSection('armor')}>Armor</button>
            </li>
            <li style={{ marginBottom: 12 }}>
                <button aria-label="Presets" style={{ width: '100%', background: section === 'presets' ? '#444' : 'none', color: '#fff', border: 'none', padding: 8, borderRadius: 4 }} onClick={() => setSection('presets')}>Presets</button>
            </li>
            <li>
                <button aria-label="Randomizer" style={{ width: '100%', background: section === 'randomizer' ? '#444' : 'none', color: '#fff', border: 'none', padding: 8, borderRadius: 4 }} onClick={() => setSection('randomizer')}>Randomizer</button>
            </li>
        </ul>
    </nav>
);

export default NavigationSidebar; 