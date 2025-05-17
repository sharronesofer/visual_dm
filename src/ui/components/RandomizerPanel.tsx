import React, { useState } from 'react';
import { useCharacterStore } from '../../store/core/characterStore';
import { RandomCharacterGenerator, RandomizationProfile } from '../../animation/RandomCharacterGenerator';

/**
 * RandomizerPanel provides controls for random character generation and feature locking.
 * Props will support onRandomize, feature locks, and current values in the future.
 */
export interface RandomizerPanelProps {
    // TODO: Add props for onRandomize, feature locks, current values, etc.
}

// Example: realistic randomization profile for demonstration
const defaultProfile: RandomizationProfile = {
    name: 'default',
    featureWeights: {
        bodyType: {
            human_male_slim: 0.01,
            human_male_medium: 1,
            human_male_large: 0.01,
            human_female_slim: 0.01,
            human_female_medium: 1,
            human_female_large: 0.01,
        },
        skinTone: {
            light: 1,
            medium: 2,
            dark: 1,
        },
        hairStyle: {
            short: 2,
            medium: 0.5,
            long: 1,
            bald: 0.1,
        },
        hairColor: {
            black: 1,
            brown: 1,
            blonde: 1,
            red: 0.1,
            gray: 0.1,
            white: 0.1,
        },
        eyeType: {
            round: 1,
            almond: 1,
            narrow: 0.1,
        },
        eyeColor: {
            brown: 2,
            blue: 1,
            green: 0.5,
            hazel: 0.2,
            gray: 0.1,
        },
        mouthType: {
            neutral: 1,
            smile: 1,
            frown: 0.1,
        },
        clothingType: {
            shirt: 1,
            tunic: 1,
            robe: 0.2,
            armor: 0.2,
        },
        equipmentType: {
            sword: 1,
            staff: 1,
            bow: 0.5,
            shield: 0.5,
        },
    },
    constraints: {},
};

export const RandomizerPanel: React.FC<RandomizerPanelProps> = (props) => {
    const customization = useCharacterStore(s => s.customization);
    const setCustomization = useCharacterStore(s => s.setCustomization);
    const [lockBodyType, setLockBodyType] = useState(false);

    // Instantiate the generator with the default profile
    const generator = new RandomCharacterGenerator([defaultProfile]);

    // Randomize character, respecting feature locks
    const handleRandomize = () => {
        const locked = lockBodyType && customization?.bodyType ? { bodyType: customization.bodyType } : {};
        const randomCustomization = generator.generateRandomCustomization('default', locked);
        setCustomization(randomCustomization);
    };

    return (
        <div>
            <h2 style={{ fontSize: 20, marginBottom: 16 }}>Randomizer</h2>
            <div style={{ marginBottom: 12 }}>
                <label>
                    <input
                        type="checkbox"
                        checked={lockBodyType}
                        onChange={e => setLockBodyType(e.target.checked)}
                        style={{ marginRight: 8 }}
                    />
                    Lock Body Type
                </label>
            </div>
            <button onClick={handleRandomize} style={{ marginBottom: 16 }}>Randomize Character</button>
            <div>Feature locking and advanced randomization coming soon...</div>
        </div>
    );
};

export default RandomizerPanel; 