from typing import Dict, List, Optional, Any, Union

    Region,
    RegionCell,
    RegionGeneratorOptions,
    TerrainType,
    POI,
    Resource,
    RegionTemplate
} from './RegionGeneratorInterfaces';
/**
 * Extended options for hand-crafted region generation
 */
class HandcraftedRegionGeneratorOptions:
    /** ID of the template to use */
    templateId?: str
/**
 * Implementation of a hand-crafted region generator that uses predefined templates
 */
class HandcraftedRegionGenerator extends BaseRegionGenerator {
    /** The templates available for this generator */
    private templates: Map<string, RegionTemplate> = new Map();
    /**
     * Create a new hand-crafted region generator
     * @param templates Optional array of templates to initialize with
     */
    constructor(templates: RegionTemplate[] = []) {
        super(GeneratorType.HAND_CRAFTED);
        for (const template of templates) {
            this.registerTemplate(template);
        }
    }
    /**
     * Register a new template
     * @param template The template to register
     */
    public registerTemplate(template: RegionTemplate): void {
        if (this.templates.has(template.id)) {
            throw new Error(`Template with ID '${template.id}' already exists`);
        }
        this.templates.set(template.id, template);
    }
    /**
     * Get all registered templates
     * @returns A map of all registered templates
     */
    public getTemplates(): Map<string, RegionTemplate> {
        return new Map(this.templates);
    }
    /**
     * Generate a region from a template
     * @param options The generation options
     * @param random The random number generator
     * @returns The generated region
     */
    protected generateRegion(options: RegionGeneratorOptions, random: IRandomGenerator): Region {
        const handcraftedOptions = options as HandcraftedRegionGeneratorOptions;
        const templateId = handcraftedOptions.templateId || this.selectRandomTemplate(random);
        const template = this.templates.get(templateId);
        if (!template) {
            throw new Error(`No template found with ID '${templateId}'`);
        }
        const width = options.width || template.width;
        const height = options.height || template.height;
        const cells = this.generateCellsFromTemplate(template, width, height, random);
        const pointsOfInterest = this.generatePOIsFromTemplate(template, random);
        const resources = this.generateResourcesFromTemplate(template, random);
        return {
            id: options.id || template.id,
            name: options.name || template.name,
            description: template.description,
            width,
            height,
            cells,
            pointsOfInterest,
            resources,
            metadata: {
                seed: random.getSeedConfig().seed,
                generatorType: this.generatorType,
                parameters: {
                    templateId,
                    width,
                    height
                }
            }
        };
    }
    /**
     * Select a random template if none is specified
     * @param random The random number generator
     * @returns A template ID
     */
    private selectRandomTemplate(random: IRandomGenerator): string {
        if (this.templates.size === 0) {
            throw new Error('No templates registered with the generator');
        }
        const templateIds = Array.from(this.templates.keys());
        return random.randomElement(templateIds);
    }
    /**
     * Generate cells from a template
     * @param template The template to use
     * @param width The width of the region
     * @param height The height of the region
     * @param random The random number generator
     * @returns An array of cells
     */
    private generateCellsFromTemplate(
        template: RegionTemplate,
        width: number,
        height: number,
        random: IRandomGenerator
    ): RegionCell[] {
        const cells: RegionCell[] = [];
        for (let y = 0; y < height; y++) {
            for (let x = 0; x < width; x++) {
                cells.push({
                    x,
                    y,
                    terrain: 'plains',
                    elevation: 0.5,
                    moisture: 0.5
                });
            }
        }
        for (const templateCell of template.cells) {
            if (templateCell.x >= width || templateCell.y >= height) {
                continue; 
            }
            const cellIndex = templateCell.y * width + templateCell.x;
            if (cellIndex >= 0 && cellIndex < cells.length) {
                cells[cellIndex] = {
                    ...cells[cellIndex],
                    ...templateCell
                };
            }
        }
        return cells;
    }
    /**
     * Generate POIs from a template
     * @param template The template to use
     * @param random The random number generator
     * @returns An array of POIs
     */
    private generatePOIsFromTemplate(
        template: RegionTemplate,
        random: IRandomGenerator
    ): POI[] {
        return template.pointsOfInterest.map((poi, index) => ({
            id: `poi-${index}`,
            templateId: poi.templateId,
            x: poi.x,
            y: poi.y,
            discovered: false
        }));
    }
    /**
     * Generate resources from a template
     * @param template The template to use
     * @param random The random number generator
     * @returns An array of resources
     */
    private generateResourcesFromTemplate(
        template: RegionTemplate,
        random: IRandomGenerator
    ): Resource[] {
        return template.resources.map((resource, index) => ({
            id: `resource-${index}`,
            templateId: resource.templateId,
            x: resource.x,
            y: resource.y,
            amount: resource.amount,
            harvested: false
        }));
    }
} 