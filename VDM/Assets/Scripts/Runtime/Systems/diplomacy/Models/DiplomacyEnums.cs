using System;

namespace VDM.Systems.Diplomacy.Models
{

    public enum DiplomaticStatus
    {
        Alliance,
        Neutral,
        Friendly,
        Rivalry,
        War,
        Truce,
        Hostile,
    }

    public enum TreatyType
    {
        Trade,
        Alliance,
        NonAggression,
        Ceasefire,
        MutualDefense,
        Custom,
    }

    public enum NegotiationStatus
    {
        Pending,
        Active,
        Accepted,
        Rejected,
        CounterOffered,
        Completed,
        Expired,
        Breakdown,
    }

    public enum DiplomaticEventType
    {
        TreatySigned,
        TreatyExpired,
        TreatyTerminated,
        TreatyBreach,
        TreatyViolation,
        NegotiationStarted,
        NegotiationEnded,
        NegotiationOffer,
        AllianceFormed,
        WarDeclaration,
        PeaceDeclaration,
        DiplomaticIncident,
        DiplomaticIncidentResolved,
        UltimatumIssued,
        UltimatumAccepted,
        UltimatumRejected,
        UltimatumExpired,
        StatusChange,
        TensionChange,
        Other,
    }

    public enum TreatyViolationType
    {
        TerritorialIntrusion,
        TradeEmbargo,
        TradeRestriction,
        MilitaryBuildup,
        MilitaryAggression,
        BrokenPromise,
        AttackedAlly,
        Espionage,
        SupportedEnemy,
        RefusedTribute,
        BrokenTerms,
        Other,
    }

    public enum DiplomaticIncidentType
    {
        BorderDispute,
        Espionage,
        Insult,
        VerbalInsult,
        Assassination,
        Kidnapping,
        TradeDispute,
        MilitaryThreat,
        Sabotage,
        PopulationInterference,
        TreatyViolation,
        ProxyConflict,
        ReligiousDispute,
        CulturalOffense,
        TerritoryClaim,
        ResourceDispute,
        RefusedDemand,
        Piracy,
        Theft,
        Other,
    }

    public enum DiplomaticIncidentSeverity
    {
        Minor,
        Moderate,
        Major,
        Critical,
    }

    public enum UltimatumStatus
    {
        Pending,
        Accepted,
        Rejected,
        Expired,
    }

    public enum SanctionType
    {
        TradeEmbargo,
        Economic,
        Diplomatic,
        TravelBan,
        AssetFreeze,
        MilitaryEmbargo,
        ResourceRestriction,
        DiplomaticExpulsion,
        TechnologyRestriction,
        EconomicBlockade,
        TreatySuspension,
        Custom,
    }

    public enum SanctionStatus
    {
        Active,
        Paused,
        Lifted,
        Expired,
        Violated,
    }
}
