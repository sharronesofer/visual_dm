import { BuildingBase, BuildingType, POICategory } from './base';

export interface SocialBuilding extends BuildingBase {
  category: POICategory.SOCIAL;
  npcCapacity: number;
  openingHours: {
    start: number; // 0-23
    end: number; // 0-23
  };
  services: SocialService[];
}

export enum SocialService {
  LODGING = 'LODGING',
  TRADING = 'TRADING',
  FOOD_DRINK = 'FOOD_DRINK',
  QUEST_GIVING = 'QUEST_GIVING',
  FACTION_SERVICES = 'FACTION_SERVICES',
  INFORMATION = 'INFORMATION'
}

export interface Inn extends SocialBuilding {
  type: BuildingType.INN;
  roomCount: number;
  roomTypes: RoomType[];
}

export interface Shop extends SocialBuilding {
  type: BuildingType.SHOP;
  shopType: ShopType;
  inventorySize: number;
}

export interface Tavern extends SocialBuilding {
  type: BuildingType.TAVERN;
  specialties: string[];
  entertainmentTypes: EntertainmentType[];
}

export interface GuildHall extends SocialBuilding {
  type: BuildingType.GUILD_HALL;
  guildType: string;
  membershipLevels: string[];
  facilities: string[];
}

export interface NPCHome extends SocialBuilding {
  type: BuildingType.NPC_HOME;
  residentCount: number;
  socialStatus: SocialStatus;
}

export enum RoomType {
  BASIC = 'BASIC',
  COMFORTABLE = 'COMFORTABLE',
  LUXURIOUS = 'LUXURIOUS'
}

export enum ShopType {
  GENERAL = 'GENERAL',
  WEAPONS = 'WEAPONS',
  ARMOR = 'ARMOR',
  MAGIC = 'MAGIC',
  ALCHEMY = 'ALCHEMY',
  SPECIALTY = 'SPECIALTY'
}

export enum EntertainmentType {
  MUSIC = 'MUSIC',
  GAMBLING = 'GAMBLING',
  STORYTELLING = 'STORYTELLING',
  PERFORMANCES = 'PERFORMANCES'
}

export enum SocialStatus {
  POOR = 'POOR',
  MODEST = 'MODEST',
  WEALTHY = 'WEALTHY',
  NOBLE = 'NOBLE'
} 