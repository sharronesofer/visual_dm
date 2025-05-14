from enum import Enum

class POIType(Enum):
    """Enum for different types of Points of Interest."""
    
    # Settlements (Regional Map Layer)
    CITY = "city"
    TOWN = "town"
    VILLAGE = "village"
    OUTPOST = "outpost"
    FORT = "fort"
    CAMP = "camp"
    HAMLET = "hamlet"
    COLONY = "colony"
    ENCLAVE = "enclave"
    HIDEOUT = "hideout"
    
    # Natural Features (Regional Map Layer)
    MOUNTAIN = "mountain"
    FOREST = "forest"
    LAKE = "lake"
    CAVE = "cave"
    RIVER = "river"
    VALLEY = "valley"
    CANYON = "canyon"
    VOLCANO = "volcano"
    SWAMP = "swamp"
    DESERT = "desert"
    GLACIER = "glacier"
    OASIS = "oasis"
    WATERFALL = "waterfall"
    CLIFF = "cliff"
    REEF = "reef"
    
    # Structures (POI Map Layer)
    CASTLE = "castle"
    TEMPLE = "temple"
    RUINS = "ruins"
    DUNGEON = "dungeon"
    TOWER = "tower"
    BRIDGE = "bridge"
    WALL = "wall"
    GATE = "gate"
    MONUMENT = "monument"
    MAUSOLEUM = "mausoleum"
    OBSERVATORY = "observatory"
    LIGHTHOUSE = "lighthouse"
    WINDMILL = "windmill"
    AQUEDUCT = "aqueduct"
    COLOSSEUM = "colosseum"
    
    # Buildings (Building Map Layer)
    RESIDENCE = "residence"
    MANSION = "mansion"
    APARTMENT = "apartment"
    GUARDHOUSE = "guardhouse"
    JAIL = "jail"
    BARRACKS = "barracks"
    WAREHOUSE = "warehouse"
    STABLE = "stable"
    WORKSHOP = "workshop"
    FARM = "farm"
    WINERY = "winery"
    BAKERY = "bakery"
    TANNERY = "tannery"
    MILL = "mill"
    FISHERY = "fishery"
    
    # Special Locations (POI Map Layer)
    PORTAL = "portal"
    SHRINE = "shrine"
    BATTLEFIELD = "battlefield"
    TREASURE = "treasure"
    MONSTER_LAIR = "monster_lair"
    CRYPT = "crypt"
    LABORATORY = "laboratory"
    LIBRARY = "library"
    ACADEMY = "academy"
    ARENA = "arena"
    CEMETERY = "cemetery"
    GARDEN = "garden"
    MARKET = "market"
    SQUARE = "square"
    HARBOR = "harbor"
    DOCKS = "docks"
    AIRSHIP_DOCK = "airship_dock"
    TELEPORTER = "teleporter"
    RIFT = "rift"
    NEXUS = "nexus"
    
    # Services (Building Map Layer)
    QUEST_GIVER = "quest_giver"
    MERCHANT = "merchant"
    TRAINER = "trainer"
    BLACKSMITH = "blacksmith"
    INN = "inn"
    TAVERN = "tavern"
    SHOP = "shop"
    BANK = "bank"
    GUILD_HALL = "guild_hall"
    TEMPLE_SERVICES = "temple_services"
    HOSPITAL = "hospital"
    SCHOOL = "school"
    POST_OFFICE = "post_office"
    CARAVANSARY = "caravansary"
    STAGE = "stage"
    BATHHOUSE = "bathhouse"
    RESTAURANT = "restaurant"
    THEATER = "theater"
    MUSEUM = "museum"
    ZOO = "zoo"
    
    @classmethod
    def get_category(cls, poi_type: 'POIType') -> str:
        """Get the category of a POI type."""
        categories = {
            'Settlements': [cls.CITY, cls.TOWN, cls.VILLAGE, cls.OUTPOST, cls.FORT, 
                          cls.CAMP, cls.HAMLET, cls.COLONY, cls.ENCLAVE, cls.HIDEOUT],
            'Natural Features': [cls.MOUNTAIN, cls.FOREST, cls.LAKE, cls.CAVE, cls.RIVER,
                               cls.VALLEY, cls.CANYON, cls.VOLCANO, cls.SWAMP, cls.DESERT,
                               cls.GLACIER, cls.OASIS, cls.WATERFALL, cls.CLIFF, cls.REEF],
            'Structures': [cls.CASTLE, cls.TEMPLE, cls.RUINS, cls.DUNGEON, cls.TOWER,
                         cls.BRIDGE, cls.WALL, cls.GATE, cls.MONUMENT, cls.MAUSOLEUM,
                         cls.OBSERVATORY, cls.LIGHTHOUSE, cls.WINDMILL, cls.AQUEDUCT, cls.COLOSSEUM],
            'Buildings': [cls.RESIDENCE, cls.MANSION, cls.APARTMENT, cls.GUARDHOUSE, cls.JAIL,
                        cls.BARRACKS, cls.WAREHOUSE, cls.STABLE, cls.WORKSHOP, cls.FARM,
                        cls.WINERY, cls.BAKERY, cls.TANNERY, cls.MILL, cls.FISHERY],
            'Special Locations': [cls.PORTAL, cls.SHRINE, cls.BATTLEFIELD, cls.TREASURE, cls.MONSTER_LAIR,
                                cls.CRYPT, cls.LABORATORY, cls.LIBRARY, cls.ACADEMY, cls.ARENA,
                                cls.CEMETERY, cls.GARDEN, cls.MARKET, cls.SQUARE, cls.HARBOR,
                                cls.DOCKS, cls.AIRSHIP_DOCK, cls.TELEPORTER, cls.RIFT, cls.NEXUS],
            'Services': [cls.QUEST_GIVER, cls.MERCHANT, cls.TRAINER, cls.BLACKSMITH, cls.INN,
                        cls.TAVERN, cls.SHOP, cls.BANK, cls.GUILD_HALL, cls.TEMPLE_SERVICES,
                        cls.HOSPITAL, cls.SCHOOL, cls.POST_OFFICE, cls.CARAVANSARY, cls.STAGE,
                        cls.BATHHOUSE, cls.RESTAURANT, cls.THEATER, cls.MUSEUM, cls.ZOO]
        }
        
        for category, types in categories.items():
            if poi_type in types:
                return category
        return 'Unknown'
    
    @classmethod
    def list_by_category(cls) -> dict:
        """List all POI types grouped by category."""
        return {
            'Settlements': [t for t in cls if cls.get_category(t) == 'Settlements'],
            'Natural Features': [t for t in cls if cls.get_category(t) == 'Natural Features'],
            'Structures': [t for t in cls if cls.get_category(t) == 'Structures'],
            'Buildings': [t for t in cls if cls.get_category(t) == 'Buildings'],
            'Special Locations': [t for t in cls if cls.get_category(t) == 'Special Locations'],
            'Services': [t for t in cls if cls.get_category(t) == 'Services']
        }

    @classmethod
    def values(cls) -> list[str]:
        """Get list of valid POI type values."""
        return [member.value for member in cls]
    
    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Check if a value is a valid POI type."""
        return value in cls.values()
    
    @classmethod
    def get_interaction_type(cls, poi_type: 'POIType') -> str:
        """Get the primary interaction type for a POI."""
        interaction_types = {
            'Dungeon': [cls.DUNGEON, cls.CAVE, cls.CRYPT, cls.MONSTER_LAIR, cls.RUINS],
            'Social': [cls.TAVERN, cls.INN, cls.MARKET, cls.SQUARE, cls.GUILD_HALL, 
                      cls.THEATER, cls.STAGE, cls.RESTAURANT, cls.BATHHOUSE],
            'Exploration': [cls.TEMPLE, cls.LIBRARY, cls.LABORATORY, cls.ACADEMY, 
                          cls.MUSEUM, cls.OBSERVATORY, cls.GARDEN, cls.ZOO]
        }
        
        for interaction_type, types in interaction_types.items():
            if poi_type in types:
                return interaction_type
        return 'None' 