using System.Collections.Generic;
using System.Text.RegularExpressions;

namespace VisualDM.Core
{
    public enum ContentFilterLevel
    {
        None,
        Warn,
        Flag,
        Block
    }

    public class ContentFilterResult
    {
        public ContentFilterLevel Level { get; set; }
        public List<string> Issues { get; set; } = new List<string>();
        public string SanitizedText { get; set; }
    }

    public class ContentFilter
    {
        private readonly List<string> _blockKeywords = new List<string> { "badword1", "badword2" };
        private readonly List<string> _warnKeywords = new List<string> { "mildword1", "mildword2" };
        private readonly List<Regex> _blockPatterns = new List<Regex> { new Regex(@"offensive\\d+", RegexOptions.IgnoreCase) };

        public ContentFilterResult Scan(string text)
        {
            var result = new ContentFilterResult { Level = ContentFilterLevel.None, SanitizedText = text };

            foreach (var keyword in _blockKeywords)
            {
                if (text.ToLower().Contains(keyword))
                {
                    result.Level = ContentFilterLevel.Block;
                    result.Issues.Add($"Blocked keyword: {keyword}");
                }
            }
            foreach (var regex in _blockPatterns)
            {
                if (regex.IsMatch(text))
                {
                    result.Level = ContentFilterLevel.Block;
                    result.Issues.Add($"Blocked pattern: {regex}");
                }
            }
            foreach (var keyword in _warnKeywords)
            {
                if (text.ToLower().Contains(keyword))
                {
                    if (result.Level < ContentFilterLevel.Warn)
                        result.Level = ContentFilterLevel.Warn;
                    result.Issues.Add($"Warning keyword: {keyword}");
                }
            }
            // Add more sophisticated logic as needed
            return result;
        }

        public string Sanitize(string text)
        {
            // Simple replacement for blocked keywords
            foreach (var keyword in _blockKeywords)
            {
                text = Regex.Replace(text, keyword, "***", RegexOptions.IgnoreCase);
            }
            foreach (var regex in _blockPatterns)
            {
                text = regex.Replace(text, "***");
            }
            return text;
        }
    }
} 