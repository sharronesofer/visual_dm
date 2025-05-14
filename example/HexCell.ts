export type TerrainType = 'plains' | 'forest' | 'mountain' | 'water' | 'desert' | 'urban';
export type WeatherType = 'clear' | 'rain' | 'snow' | 'fog' | 'storm' | 'windy';

export class HexCell {
    private _q: number;
    private _r: number;
    private _terrain: TerrainType;
    private _weather: WeatherType;
    private _elevation: number;
    private _moisture: number;
    private _temperature: number;
    private _isDiscovered: boolean;
    private _hasFeature: boolean;
    private _featureType: string | null;

    constructor(
        q: number,
        r: number,
        terrain: TerrainType = 'plains',
        weather: WeatherType = 'clear',
        elevation: number = 0,
        moisture: number = 0.5,
        temperature: number = 0.5
    ) {
        this._q = q;
        this._r = r;
        this._terrain = terrain;
        this._weather = weather;
        this._elevation = elevation;
        this._moisture = moisture;
        this._temperature = temperature;
        this._isDiscovered = false;
        this._hasFeature = false;
        this._featureType = null;
    }

    public get q(): number {
        return this._q;
    }

    public get r(): number {
        return this._r;
    }

    public get terrain(): TerrainType {
        return this._terrain;
    }

    public set terrain(value: TerrainType) {
        this._terrain = value;
    }

    public get weather(): WeatherType {
        return this._weather;
    }

    public set weather(value: WeatherType) {
        this._weather = value;
    }

    public get elevation(): number {
        return this._elevation;
    }

    public set elevation(value: number) {
        this._elevation = value;
    }

    public get moisture(): number {
        return this._moisture;
    }

    public set moisture(value: number) {
        this._moisture = value;
    }

    public get temperature(): number {
        return this._temperature;
    }

    public set temperature(value: number) {
        this._temperature = value;
    }

    public get isDiscovered(): boolean {
        return this._isDiscovered;
    }

    public set isDiscovered(value: boolean) {
        this._isDiscovered = value;
    }

    public get hasFeature(): boolean {
        return this._hasFeature;
    }

    public get featureType(): string | null {
        return this._featureType;
    }

    public addFeature(featureType: string): void {
        this._hasFeature = true;
        this._featureType = featureType;
    }

    public removeFeature(): void {
        this._hasFeature = false;
        this._featureType = null;
    }

    public getCost(): number {
        let cost = 1.0;

        // Apply terrain factors
        switch (this._terrain) {
            case 'plains':
                cost = 1.0;
                break;
            case 'forest':
                cost = 1.5;
                break;
            case 'mountain':
                cost = 3.0;
                break;
            case 'water':
                cost = 2.0;
                break;
            case 'desert':
                cost = 1.8;
                break;
            case 'urban':
                cost = 1.2;
                break;
        }

        // Apply weather factors
        if (this._weather === 'rain' || this._weather === 'fog') {
            cost *= 1.2;
        } else if (this._weather === 'snow' || this._weather === 'storm') {
            cost *= 1.5;
        }

        // Apply elevation factor
        cost *= (1.0 + this._elevation * 0.1);

        return cost;
    }

    public isAdjacent(other: HexCell): boolean {
        const dx = this._q - other.q;
        const dy = this._r - other.r;
        return (Math.abs(dx) <= 1 && Math.abs(dy) <= 1 && Math.abs(dx + dy) <= 1);
    }

    public getNeighborCoordinates(): Array<[number, number]> {
        return [
            [this._q + 1, this._r],
            [this._q, this._r + 1],
            [this._q - 1, this._r + 1],
            [this._q - 1, this._r],
            [this._q, this._r - 1],
            [this._q + 1, this._r - 1]
        ];
    }

    public equals(other: HexCell): boolean {
        return this._q === other.q && this._r === other.r;
    }

    public toString(): string {
        return `HexCell(${this._q},${this._r},${this._terrain})`;
    }
} 