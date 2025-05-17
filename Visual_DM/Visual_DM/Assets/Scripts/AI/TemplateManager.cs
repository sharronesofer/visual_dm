using System.Collections.Generic;

namespace AI
{
    public class TemplateManager
    {
        private readonly Dictionary<string, PromptTemplate> _templateCache = new Dictionary<string, PromptTemplate>();

        public TemplateManager()
        {
            // Register default templates
            AddTemplate("combat", new CombatQuestTemplate());
            AddTemplate("exploration", new ExplorationQuestTemplate());
            AddTemplate("collection", new CollectionQuestTemplate());
        }

        public void AddTemplate(string type, PromptTemplate template)
        {
            _templateCache[type] = template;
        }

        public PromptTemplate GetTemplate(string type)
        {
            if (_templateCache.TryGetValue(type, out var template))
                return template;
            return null;
        }

        public bool IsVersionCompatible(string type, string version)
        {
            var template = GetTemplate(type);
            if (template == null) return false;
            // Simple version check (can be extended)
            return template.Version == version;
        }

        public void MigrateTemplate(string type, string targetVersion)
        {
            // Stub for migration logic
            // In a real system, would handle migration paths
        }

        public void AddContextToTemplate(string type, string message)
        {
            var template = GetTemplate(type);
            template?.AddContext(message);
        }

        public void ClearTemplateContext(string type)
        {
            var template = GetTemplate(type);
            template?.ClearContext();
        }
    }
} 