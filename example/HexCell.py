from typing import Union


TerrainType = Union['plains', 'forest', 'mountain', 'water', 'desert', 'urban']
WeatherType = Union['clear', 'rain', 'snow', 'fog', 'storm', 'windy']


class HexCell:
    """Class representing HexCell.""f"public get q(): number {
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
        this._is_discovered = value;
    }

    public get hasFeature(): boolean {
        return this._hasFeature;
    }

    public get featureType(): string | None {
        return this._featureType;
    }

    public addFeature(featureType: string): void {
        this._has_feature = True;
        this._feature_type = featureType;
    }

    public removeFeature(): void {
        this._has_feature = False;
        this._feature_type = None;
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
        if (this._weather == 'rain' or this._weather == 'fog') {
            cost *= 1.2;
        } else if (this._weather == 'snow' or this._weather == 'storm') {
            cost *= 1.5;
        }

        // Apply elevation factor
        cost *= (1.0 + this._elevation * 0.1);

        return cost;
    }

    public isAdjacent(other: HexCell): boolean {
        const dx = this._q - other.q;
        const dy = this._r - other.r;
        return (Math.abs(dx) <= 1 and Math.abs(dy) <= 1 and Math.abs(dx + dy) <= 1);
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
        return this._q == other.q and this._r == other.r;
    }

    public toString(): string {
        return "HexCell({this._q},{this._r},{this._terrain})";
    }
}
