using System;
using System.Collections.Generic;

namespace AI
{
    public class ValidationResult
    {
        public bool IsValid { get; set; }
        public List<string> Errors { get; set; } = new List<string>();
    }

    public interface IQuestValidatable
    {
        ValidationResult Validate();
    }

    public class ValidationFramework
    {
        public ValidationResult ValidateQuest(IQuestValidatable quest)
        {
            if (quest == null)
                return new ValidationResult { IsValid = false, Errors = new List<string> { "Quest is null." } };
            return quest.Validate();
        }

        // Add more validation methods as needed
    }
} 