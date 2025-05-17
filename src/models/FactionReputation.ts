export type MoralStanding = -100 | -99 | -98 | ... | 0 | ... | 98 | 99 | 100; // For brevity, use number in implementation
export type FameLevel = number; // 0-100

export interface FactionReputationData {
  factionId: string;
  moral: number; // -100 to +100
  fame: number; // 0 to 100
  lastUpdated: Date;
  legendaryAchievements?: string[];
}

export class FactionReputation {
  public factionId: string;
  private _moral: number;
  private _fame: number;
  public lastUpdated: Date;
  public legendaryAchievements: string[];

  constructor(data: FactionReputationData) {
    this.factionId = data.factionId;
    this._moral = this.clampMoral(data.moral);
    this._fame = this.clampFame(data.fame);
    this.lastUpdated = data.lastUpdated || new Date();
    this.legendaryAchievements = data.legendaryAchievements || [];
  }

  get moral(): number {
    return this._moral;
  }

  set moral(value: number) {
    this._moral = this.clampMoral(value);
    this.lastUpdated = new Date();
  }

  get fame(): number {
    return this._fame;
  }

  set fame(value: number) {
    this._fame = this.clampFame(value);
    this.lastUpdated = new Date();
  }

  private clampMoral(value: number): number {
    return Math.max(-100, Math.min(100, value));
  }

  private clampFame(value: number): number {
    return Math.max(0, Math.min(100, value));
  }

  public toJSON(): FactionReputationData {
    return {
      factionId: this.factionId,
      moral: this._moral,
      fame: this._fame,
      lastUpdated: this.lastUpdated,
      legendaryAchievements: this.legendaryAchievements,
    };
  }

  public static fromJSON(data: FactionReputationData): FactionReputation {
    return new FactionReputation(data);
  }
} 