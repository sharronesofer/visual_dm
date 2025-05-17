// RandomCharacterGenerator.ts
// Generates random, coherent character customizations with weighted feature selection and feature locking.

import {
    BodyType,
    SkinTone,
    HairStyle,
    HairColor,
    EyeType,
    EyeColor,
    MouthType,
    ClothingType,
    EquipmentType,
    ExtendedCharacterCustomization,
} from './CharacterCustomization';

/**
 * Type for feature weights (probability distribution for each option).
 */
export type FeatureWeights<T extends string | number> = Record<T, number>;

/**
 * Randomization profile: defines weights and constraints for each feature.
 */
export interface RandomizationProfile {
    name: string;
    featureWeights: {
        bodyType?: FeatureWeights<BodyType>;
        skinTone?: FeatureWeights<SkinTone>;
        hairStyle?: FeatureWeights<HairStyle>;
        hairColor?: FeatureWeights<HairColor>;
        eyeType?: FeatureWeights<EyeType>;
        eyeColor?: FeatureWeights<EyeColor>;
        mouthType?: FeatureWeights<MouthType>;
        clothingType?: FeatureWeights<ClothingType>;
        equipmentType?: FeatureWeights<EquipmentType>;
        // Extend for modular/mesh features as needed
    };
    constraints?: RandomizationConstraints;
}

/**
 * Constraints for randomization (e.g., race, gender, cultural limits).
 */
export interface RandomizationConstraints {
    allowedBodyTypes?: BodyType[];
    allowedSkinTones?: SkinTone[];
    allowedHairStyles?: HairStyle[];
    allowedHairColors?: HairColor[];
    allowedEyeTypes?: EyeType[];
    allowedEyeColors?: EyeColor[];
    allowedMouthTypes?: MouthType[];
    allowedClothingTypes?: ClothingType[];
    allowedEquipmentTypes?: EquipmentType[];
    // Extend for modular/mesh features as needed
    // Add inter-feature dependencies (e.g., beard only for certain genders)
}

/**
 * Options for feature locking: specify which features to keep fixed.
 */
export type FeatureLock = Partial<Omit<ExtendedCharacterCustomization, 'meshSlots' | 'blendShapes' | 'materials' | 'scale'>>;

/**
 * Utility: weighted random selection from a feature weight map.
 */
export function weightedRandom<T extends string | number>(weights: FeatureWeights<T>, allowed?: T[]): T {
    const entries = Object.entries(weights) as [T, number][];
    const filtered = allowed ? entries.filter(([k]) => allowed.includes(k)) : entries;
    const total = filtered.reduce((sum, [, w]) => sum + w, 0);
    let r = Math.random() * total;
    for (const [value, weight] of filtered) {
        if (r < weight) return value;
        r -= weight;
    }
    // Fallback: return first allowed value
    return filtered[0][0];
}

/**
 * Main class for random character generation.
 */
export class RandomCharacterGenerator {
    private profiles: Record<string, RandomizationProfile>;

    constructor(profiles: RandomizationProfile[]) {
        this.profiles = Object.fromEntries(profiles.map(p => [p.name, p]));
    }

    /**
     * Generate a random character customization, respecting feature locks and profile constraints.
     * @param profileName Name of the randomization profile to use
     * @param locked Partial customization object specifying locked features
     */
    generateRandomCustomization(
        profileName: string,
        locked: FeatureLock = {}
    ): ExtendedCharacterCustomization {
        const profile = this.profiles[profileName];
        if (!profile) throw new Error(`Profile not found: ${profileName}`);
        const { featureWeights, constraints } = profile;
        // Helper to pick a feature value with fallback
        const pick = <T extends string | number>(
            feature: keyof typeof featureWeights,
            allowed: T[] | undefined,
            fallback: T
        ): T => {
            const weights = featureWeights[feature] as FeatureWeights<T> | undefined;
            if (!weights) return fallback;
            const value = weightedRandom(weights, allowed);
            return value ?? fallback;
        };
        // Fallbacks for each feature (use first enum value)
        const fallbackBodyType = Object.values(BodyType)[0] as BodyType;
        const fallbackSkinTone = Object.values(SkinTone)[0] as SkinTone;
        const fallbackHairStyle = Object.values(HairStyle)[0] as HairStyle;
        const fallbackHairColor = Object.values(HairColor)[0] as HairColor;
        const fallbackEyeType = Object.values(EyeType)[0] as EyeType;
        const fallbackEyeColor = Object.values(EyeColor)[0] as EyeColor;
        const fallbackMouthType = Object.values(MouthType)[0] as MouthType;
        const fallbackClothingType = Object.values(ClothingType)[0] as ClothingType;
        const fallbackEquipmentType = Object.values(EquipmentType)[0] as EquipmentType;
        // Build the customization object
        return {
            ...locked,
            bodyType:
                locked.bodyType ?? pick('bodyType', constraints?.allowedBodyTypes, fallbackBodyType),
            skinTone:
                locked.skinTone ?? pick('skinTone', constraints?.allowedSkinTones, fallbackSkinTone),
            hair: locked.hair ?? {
                style: pick('hairStyle', constraints?.allowedHairStyles, fallbackHairStyle),
                color: pick('hairColor', constraints?.allowedHairColors, fallbackHairColor),
            },
            eyes: locked.eyes ?? {
                type: pick('eyeType', constraints?.allowedEyeTypes, fallbackEyeType),
                color: pick('eyeColor', constraints?.allowedEyeColors, fallbackEyeColor),
            },
            mouth: locked.mouth ?? {
                type: pick('mouthType', constraints?.allowedMouthTypes, fallbackMouthType),
            },
            clothing: locked.clothing ?? {
                type: pick('clothingType', constraints?.allowedClothingTypes, fallbackClothingType),
                color: '#888', // Optionally randomize color
            },
            equipment: locked.equipment ?? [
                {
                    type: pick('equipmentType', constraints?.allowedEquipmentTypes, fallbackEquipmentType),
                },
            ],
            // Extend for modular/mesh features as needed
        };
    }

    /**
     * Get a random value for a specific feature using a profile.
     */
    getRandomFeatureValue<T extends string | number>(
        profileName: string,
        feature: keyof RandomizationProfile['featureWeights'],
        allowed?: T[]
    ): T | undefined {
        const profile = this.profiles[profileName];
        if (!profile) throw new Error(`Profile not found: ${profileName}`);
        const weights = profile.featureWeights[feature] as FeatureWeights<T> | undefined;
        if (!weights) return undefined;
        return weightedRandom(weights, allowed);
    }
} 