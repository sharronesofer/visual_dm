import { BaseEntity } from './BaseEntity';

/**
 * Weather condition options for the world
 */
export enum WeatherCondition {
    CLEAR = 'clear',
    CLOUDY = 'cloudy',
    RAIN = 'rain',
    STORM = 'storm',
    SNOW = 'snow',
    FOG = 'fog',
    WINDY = 'windy'
}

/**
 * Season options for the world
 */
export enum Season {
    SPRING = 'spring',
    SUMMER = 'summer',
    AUTUMN = 'autumn',
    WINTER = 'winter'
}

/**
 * World interface representing the game world state
 */
export interface World extends BaseEntity {
    name: string;
    description?: string;

    // Time tracking
    currentTime: Date;
    timeScale: number; // How fast game time passes relative to real time

    // Season and weather tracking
    currentSeason: Season;
    currentWeather: WeatherCondition;
    weatherDuration: number; // How long the current weather will last

    // World settings
    mapSize: { width: number, height: number };
    worldSeed: number; // Seed for procedural generation

    // Additional properties
    activeEvents: string[]; // IDs of active world events
    globalFlags: Record<string, boolean>; // Flags for world state
    globalVariables: Record<string, number>; // Numeric variables for world state
} 