namespace VisualDM.Entities
{
    // TODO: Add using statement for PersonalityProfile if not in VisualDM.Entities
    public interface INPCTemplate
    {
        string TemplateName { get; }
        PersonalityProfile GetDefaultPersonality();
    }
} 