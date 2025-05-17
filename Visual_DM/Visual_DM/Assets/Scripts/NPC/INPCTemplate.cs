namespace VisualDM.NPC
{
    public interface INPCTemplate
    {
        string TemplateName { get; }
        PersonalityProfile GetDefaultPersonality();
    }
} 