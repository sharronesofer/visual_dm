import { IValidationRule } from '../core/IWorldGenerator';
import { Region, TerrainType } from '../region/RegionGeneratorInterfaces';

/**
 * Result of a region validation
 */
export interface RegionValidationResult {
    /** Whether the validation passed */
    isValid: boolean;
    /** Error message if validation failed */
    errorMessage?: string;
    /** Additional details about the validation */
    details?: any;
}

/**
 * Base class for region validation rules
 */
export abstract class RegionValidationRule implements IValidationRule<Region> {
    /** The name of the rule */
    protected ruleName: string;
    /** The error message template */
    protected errorMessageTemplate: string;
    /** Last validation details */
    protected lastValidationDetails: any;

    /**
     * Create a new region validation rule
     * @param ruleName The name of the rule
     * @param errorMessageTemplate The error message template
     */
    constructor(ruleName: string, errorMessageTemplate: string) {
        this.ruleName = ruleName;
        this.errorMessageTemplate = errorMessageTemplate;
        this.lastValidationDetails = null;
    }

    /**
     * Get the name of the rule
     * @returns The rule name
     */
    public getName(): string {
        return this.ruleName;
    }

    /**
     * Validate a region
     * @param region The region to validate
     * @returns Whether the region is valid
     */
    public abstract validate(region: Region): boolean;

    /**
     * Get the error message for a failed validation
     * @returns The error message
     */
    public getErrorMessage(): string {
        return this.errorMessageTemplate.replace('{details}',
            this.lastValidationDetails ? JSON.stringify(this.lastValidationDetails) : '');
    }

    /**
     * Get the details of the last validation
     * @returns The validation details
     */
    public getDetails(): any {
        return this.lastValidationDetails;
    }
}

/**
 * Validates that a region has all required fields
 */
export class RegionStructureValidationRule extends RegionValidationRule {
    constructor() {
        super(
            'RegionStructureValidation',
            'Region structure is invalid: {details}'
        );
    }

    public validate(region: Region): boolean {
        const requiredFields = ['id', 'name', 'width', 'height', 'cells'];
        const missingFields: string[] = [];

        for (const field of requiredFields) {
            if (!region[field as keyof Region]) {
                missingFields.push(field);
            }
        }

        if (missingFields.length > 0) {
            this.lastValidationDetails = { missingFields };
            return false;
        }

        // Check that cells array has the right length
        if (region.cells.length !== region.width * region.height) {
            this.lastValidationDetails = {
                expectedCellCount: region.width * region.height,
                actualCellCount: region.cells.length
            };
            return false;
        }

        return true;
    }
}

/**
 * Validates that a region's cells have valid coordinates
 */
export class CellCoordinatesValidationRule extends RegionValidationRule {
    constructor() {
        super(
            'CellCoordinatesValidation',
            'Region cells have invalid coordinates: {details}'
        );
    }

    public validate(region: Region): boolean {
        const invalidCells = [];

        for (const cell of region.cells) {
            if (cell.x < 0 || cell.x >= region.width || cell.y < 0 || cell.y >= region.height) {
                invalidCells.push(`Cell at (${cell.x}, ${cell.y})`);
            }
        }

        if (invalidCells.length > 0) {
            this.lastValidationDetails = { invalidCells };
            return false;
        }

        return true;
    }
}

/**
 * Validates that a region has appropriate biome adjacency
 */
export class BiomeAdjacencyValidationRule extends RegionValidationRule {
    /** Map of incompatible terrain adjacencies */
    private incompatibleAdjacencies: Record<TerrainType, TerrainType[]> = {
        'desert': ['water', 'mountain'],
        'water': ['desert'],
        'mountain': ['desert'],
        'forest': [],
        'plains': [],
        'urban': []
    };

    constructor() {
        super(
            'BiomeAdjacencyValidation',
            'Region has incompatible biome adjacencies: {details}'
        );
    }

    public validate(region: Region): boolean {
        const incompatiblePairs: string[] = [];

        // Check each cell
        for (const cell of region.cells) {
            const terrain = cell.terrain;
            const incompatibleTypes = this.incompatibleAdjacencies[terrain];

            // Get adjacent cells
            const adjacentCells = this.getAdjacentCells(cell.x, cell.y, region);

            // Check for incompatible adjacencies
            for (const adjacentCell of adjacentCells) {
                if (incompatibleTypes.includes(adjacentCell.terrain)) {
                    incompatiblePairs.push(
                        `${terrain} at (${cell.x}, ${cell.y}) adjacent to ` +
                        `${adjacentCell.terrain} at (${adjacentCell.x}, ${adjacentCell.y})`
                    );
                }
            }
        }

        if (incompatiblePairs.length > 0) {
            this.lastValidationDetails = { incompatiblePairs };
            return false;
        }

        return true;
    }

    /**
     * Get adjacent cells for a given position
     * @param x X coordinate
     * @param y Y coordinate
     * @param region The region
     * @returns Array of adjacent cells
     */
    private getAdjacentCells(x: number, y: number, region: Region) {
        const adjacentPositions = [
            { x: x - 1, y: y },
            { x: x + 1, y: y },
            { x: x, y: y - 1 },
            { x: x, y: y + 1 }
        ];

        return adjacentPositions
            .filter(pos => pos.x >= 0 && pos.x < region.width && pos.y >= 0 && pos.y < region.height)
            .map(pos => region.cells.find(cell => cell.x === pos.x && cell.y === pos.y))
            .filter(cell => cell !== undefined) as RegionCell[];
    }
}

/**
 * Validates that a region has a reasonable distribution of terrain types
 */
export class TerrainDistributionValidationRule extends RegionValidationRule {
    /** Maximum percentage of a single terrain type */
    private maxTerrainPercentage = 0.6;

    constructor() {
        super(
            'TerrainDistributionValidation',
            'Region has unbalanced terrain distribution: {details}'
        );
    }

    public validate(region: Region): boolean {
        // Count occurrences of each terrain type
        const terrainCounts: Record<TerrainType, number> = {
            'water': 0,
            'mountain': 0,
            'forest': 0,
            'desert': 0,
            'urban': 0,
            'plains': 0
        };

        for (const cell of region.cells) {
            terrainCounts[cell.terrain]++;
        }

        // Calculate total cells
        const totalCells = region.cells.length;

        // Check if any terrain type exceeds the maximum percentage
        const unbalancedTerrains: string[] = [];

        for (const [terrain, count] of Object.entries(terrainCounts)) {
            const percentage = count / totalCells;
            if (percentage > this.maxTerrainPercentage) {
                unbalancedTerrains.push(`${terrain} (${Math.round(percentage * 100)}%)`);
            }
        }

        if (unbalancedTerrains.length > 0) {
            this.lastValidationDetails = {
                unbalancedTerrains,
                terrainCounts,
                maxAllowedPercentage: Math.round(this.maxTerrainPercentage * 100) + '%'
            };
            return false;
        }

        return true;
    }
}

/**
 * Combines multiple validation rules into a single rule
 */
export class CompositeRegionValidationRule extends RegionValidationRule {
    /** The rules to validate */
    private rules: RegionValidationRule[];

    /**
     * Create a new composite validation rule
     * @param rules The rules to validate
     */
    constructor(rules: RegionValidationRule[]) {
        super(
            'CompositeRegionValidation',
            'Region validation failed: {details}'
        );
        this.rules = rules;
    }

    public validate(region: Region): boolean {
        const failedRules: string[] = [];

        for (const rule of this.rules) {
            if (!rule.validate(region)) {
                failedRules.push(`${rule.getName()}: ${rule.getErrorMessage()}`);
            }
        }

        if (failedRules.length > 0) {
            this.lastValidationDetails = { failedRules };
            return false;
        }

        return true;
    }
}

/**
 * Creates a standard validation rule set for regions
 * @returns A composite validation rule
 */
export function createStandardRegionValidationRules(): CompositeRegionValidationRule {
    return new CompositeRegionValidationRule([
        new RegionStructureValidationRule(),
        new CellCoordinatesValidationRule(),
        new BiomeAdjacencyValidationRule(),
        new TerrainDistributionValidationRule()
    ]);
} 