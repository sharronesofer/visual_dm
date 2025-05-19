using System;
using UnityEngine;

namespace VisualDM.Entities
{
    /// <summary>
    /// Implementation of the INPCTemplate interface that provides a template for NPC creation.
    /// </summary>
    [Serializable]
    public class NPCTemplate : INPCTemplate
    {
        [SerializeField] private string _templateName;
        [SerializeField] private PersonalityProfile _defaultPersonality;
        
        /// <summary>
        /// Name of the template.
        /// </summary>
        public string TemplateName => _templateName;

        /// <summary>
        /// Creates a new NPCTemplate with the specified name and personality.
        /// </summary>
        /// <param name="templateName">Name of the template</param>
        /// <param name="defaultPersonality">Default personality profile for NPCs created from this template</param>
        public NPCTemplate(string templateName, PersonalityProfile defaultPersonality)
        {
            _templateName = templateName ?? throw new ArgumentNullException(nameof(templateName));
            _defaultPersonality = defaultPersonality ?? new PersonalityProfile();
        }

        /// <summary>
        /// Creates a new NPCTemplate with the specified name and default personality traits.
        /// </summary>
        /// <param name="templateName">Name of the template</param>
        /// <param name="friendliness">Default friendliness value (0-1)</param>
        /// <param name="aggression">Default aggression value (0-1)</param>
        /// <param name="curiosity">Default curiosity value (0-1)</param>
        /// <param name="discipline">Default discipline value (0-1)</param>
        /// <param name="optimism">Default optimism value (0-1)</param>
        /// <param name="sociability">Default sociability value (0-1)</param>
        /// <param name="intelligence">Default intelligence value (0-1)</param>
        public NPCTemplate(
            string templateName,
            float friendliness = 0.5f,
            float aggression = 0.5f,
            float curiosity = 0.5f,
            float discipline = 0.5f,
            float optimism = 0.5f,
            float sociability = 0.5f,
            float intelligence = 0.5f)
        {
            _templateName = templateName ?? throw new ArgumentNullException(nameof(templateName));
            _defaultPersonality = new PersonalityProfile(
                friendliness, 
                aggression, 
                curiosity, 
                discipline, 
                optimism, 
                sociability, 
                intelligence
            );
        }

        /// <summary>
        /// Gets the default personality profile for this template.
        /// </summary>
        /// <returns>A copy of the default personality profile</returns>
        public PersonalityProfile GetDefaultPersonality()
        {
            return new PersonalityProfile(
                _defaultPersonality.Friendliness,
                _defaultPersonality.Aggression,
                _defaultPersonality.Curiosity,
                _defaultPersonality.Discipline,
                _defaultPersonality.Optimism,
                _defaultPersonality.Sociability,
                _defaultPersonality.Intelligence
            );
        }
    }
} 