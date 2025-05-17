using System.Collections.Generic;
using System.Text.RegularExpressions;

namespace AI
{
    public class PromptTemplate
    {
        public string Template { get; protected set; }
        public string Version { get; protected set; }
        public Dictionary<string, string> Metadata { get; protected set; }
        public List<string> Context { get; protected set; } = new List<string>();

        public PromptTemplate(string template, string version = "1.0", Dictionary<string, string> metadata = null)
        {
            Template = template;
            Version = version;
            Metadata = metadata ?? new Dictionary<string, string>();
        }

        public virtual string Render(Dictionary<string, string> variables)
        {
            string result = Template;
            if (variables != null)
            {
                foreach (var kvp in variables)
                {
                    result = Regex.Replace(result, $"{{{{{kvp.Key}}}}}", kvp.Value);
                }
            }
            return result;
        }

        public virtual void AddContext(string message)
        {
            Context.Add(message);
        }

        public virtual void ClearContext()
        {
            Context.Clear();
        }
    }
} 