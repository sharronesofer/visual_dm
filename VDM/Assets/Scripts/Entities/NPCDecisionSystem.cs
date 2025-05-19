using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Entities
{
    /// <summary>
    /// Decision type enum - represents different categories of decisions an NPC can make
    /// </summary>
    public enum DecisionType
    {
        Combat,
        Social,
        Economic,
        Movement,
        Quest
    }

    /// <summary>
    /// Decision outcome representing the result of the decision-making process
    /// </summary>
    [Serializable]
    public class DecisionOutcome
    {
        public string ActionId { get; private set; }
        public float Confidence { get; private set; }
        public Dictionary<string, float> FactorWeights { get; private set; }

        public DecisionOutcome(string actionId, float confidence, Dictionary<string, float> factorWeights)
        {
            ActionId = actionId;
            Confidence = Mathf.Clamp01(confidence);
            FactorWeights = factorWeights;
        }

        public override string ToString()
        {
            return $"Action: {ActionId}, Confidence: {Confidence:0.00}";
        }
    }

    /// <summary>
    /// Decision option representing a possible action an NPC can take
    /// </summary>
    [Serializable]
    public class DecisionOption
    {
        public string ActionId { get; private set; }
        public string Description { get; private set; }
        public Dictionary<string, float> TraitRequirements { get; private set; }
        public Dictionary<string, float> MoodModifiers { get; private set; }
        public float BaseUtility { get; private set; }

        public DecisionOption(string actionId, string description, Dictionary<string, float> traitRequirements, 
                              Dictionary<string, float> moodModifiers = null, float baseUtility = 0.5f)
        {
            ActionId = actionId;
            Description = description;
            TraitRequirements = traitRequirements;
            MoodModifiers = moodModifiers ?? new Dictionary<string, float>();
            BaseUtility = baseUtility;
        }
    }

    /// <summary>
    /// NPC decision system that uses personality traits and mood to generate decisions
    /// </summary>
    public class NPCDecisionSystem
    {
        private readonly PersonalityProfile _personality;
        private readonly NPCMood _mood;
        private readonly NPCBehaviorModifier _behaviorModifier;
        private readonly Dictionary<DecisionType, List<DecisionOption>> _decisionLibrary;
        private System.Random _random;

        /// <summary>
        /// Initialize the decision system with NPC personality and mood
        /// </summary>
        /// <param name="personality">The NPC's personality profile</param>
        /// <param name="mood">The NPC's current mood</param>
        public NPCDecisionSystem(PersonalityProfile personality, NPCMood mood)
        {
            _personality = personality ?? throw new ArgumentNullException(nameof(personality));
            _mood = mood ?? throw new ArgumentNullException(nameof(mood));
            _behaviorModifier = new NPCBehaviorModifier(personality, mood);
            _decisionLibrary = InitializeDecisionLibrary();
            _random = new System.Random();
        }

        /// <summary>
        /// Make a decision of the specified type given the current context
        /// </summary>
        /// <param name="decisionType">Type of decision to make</param>
        /// <param name="contextFactors">Additional context factors that influence the decision (optional)</param>
        /// <returns>The decision outcome with action and confidence level</returns>
        public DecisionOutcome MakeDecision(DecisionType decisionType, Dictionary<string, float> contextFactors = null)
        {
            // Default empty context if none provided
            contextFactors = contextFactors ?? new Dictionary<string, float>();

            // Get available options for this decision type
            if (!_decisionLibrary.TryGetValue(decisionType, out var options) || options.Count == 0)
            {
                return new DecisionOutcome("no_action", 0f, new Dictionary<string, float>());
            }

            // Calculate utility for each option
            var optionScores = new Dictionary<DecisionOption, float>();
            var factorWeights = new Dictionary<DecisionOption, Dictionary<string, float>>();
            
            foreach (var option in options)
            {
                float utility = CalculateOptionUtility(option, contextFactors, out Dictionary<string, float> weights);
                optionScores[option] = utility;
                factorWeights[option] = weights;
            }

            // Select the option with highest utility (with some randomness)
            DecisionOption selectedOption = SelectOption(optionScores);
            float confidence = optionScores[selectedOption];

            return new DecisionOutcome(
                selectedOption.ActionId, 
                confidence,
                factorWeights[selectedOption]
            );
        }

        /// <summary>
        /// Calculate the utility (desirability) of a decision option
        /// </summary>
        private float CalculateOptionUtility(DecisionOption option, Dictionary<string, float> contextFactors, 
                                           out Dictionary<string, float> factorWeights)
        {
            factorWeights = new Dictionary<string, float>();
            float totalUtility = option.BaseUtility;
            
            // 1. Personality traits influence
            float traitScore = 0f;
            float traitWeight = 0.4f;
            
            var personalityTraits = _personality.ToDictionary();
            foreach (var traitReq in option.TraitRequirements)
            {
                if (personalityTraits.TryGetValue(traitReq.Key, out float traitValue))
                {
                    float match = 1f - Math.Abs(traitValue - traitReq.Value);
                    traitScore += match;
                }
            }
            
            // Normalize trait score
            if (option.TraitRequirements.Count > 0)
            {
                traitScore /= option.TraitRequirements.Count;
            }
            
            factorWeights["Personality"] = traitScore;
            totalUtility += traitScore * traitWeight;
            
            // 2. Mood influence
            float moodScore = 0f;
            float moodWeight = 0.2f;
            
            if (option.MoodModifiers.TryGetValue(_mood.CurrentMood.ToString(), out float moodInfluence))
            {
                moodScore = moodInfluence * _mood.MoodIntensity;
            }
            
            factorWeights["Mood"] = moodScore;
            totalUtility += moodScore * moodWeight;
            
            // 3. Context factors
            float contextScore = 0f;
            float contextWeight = 0.4f;
            
            foreach (var factor in contextFactors)
            {
                contextScore += factor.Value;
            }
            
            // Normalize context score
            if (contextFactors.Count > 0)
            {
                contextScore /= contextFactors.Count;
            }
            
            factorWeights["Context"] = contextScore;
            totalUtility += contextScore * contextWeight;
            
            // Return normalized utility (0-1)
            return Mathf.Clamp01(totalUtility);
        }

        /// <summary>
        /// Select an option based on utility scores with some randomness
        /// </summary>
        private DecisionOption SelectOption(Dictionary<DecisionOption, float> optionScores)
        {
            // Convert scores to cumulative probabilities
            List<DecisionOption> options = new List<DecisionOption>();
            List<float> probabilities = new List<float>();
            float totalScore = 0f;
            
            foreach (var kvp in optionScores)
            {
                options.Add(kvp.Key);
                // Apply softmax-like function to make selection more probabilistic
                float probability = Mathf.Exp(kvp.Value * 3); // Temperature parameter
                probabilities.Add(probability);
                totalScore += probability;
            }
            
            // Normalize probabilities
            for (int i = 0; i < probabilities.Count; i++)
            {
                probabilities[i] /= totalScore;
            }
            
            // Select option using weighted random selection
            float randomValue = (float)_random.NextDouble();
            float cumulativeProbability = 0f;
            
            for (int i = 0; i < options.Count; i++)
            {
                cumulativeProbability += probabilities[i];
                if (randomValue <= cumulativeProbability)
                {
                    return options[i];
                }
            }
            
            // Fallback
            return options[options.Count - 1];
        }

        /// <summary>
        /// Initialize the library of decision options for each decision type
        /// </summary>
        private Dictionary<DecisionType, List<DecisionOption>> InitializeDecisionLibrary()
        {
            var library = new Dictionary<DecisionType, List<DecisionOption>>();
            
            // Combat decision options
            library[DecisionType.Combat] = new List<DecisionOption>
            {
                new DecisionOption(
                    "attack_aggressive", 
                    "Attack aggressively",
                    new Dictionary<string, float> { 
                        { "Aggression", 0.8f }, 
                        { "Discipline", 0.3f } 
                    },
                    new Dictionary<string, float> { 
                        { "Angry", 0.8f },
                        { "Afraid", -0.5f }
                    },
                    0.6f
                ),
                
                new DecisionOption(
                    "attack_cautious", 
                    "Attack cautiously",
                    new Dictionary<string, float> { 
                        { "Aggression", 0.5f }, 
                        { "Discipline", 0.7f },
                        { "Intelligence", 0.6f }
                    },
                    new Dictionary<string, float> { 
                        { "Neutral", 0.3f },
                        { "Afraid", 0.3f }
                    },
                    0.5f
                ),
                
                new DecisionOption(
                    "defend", 
                    "Take defensive stance",
                    new Dictionary<string, float> { 
                        { "Aggression", 0.2f }, 
                        { "Discipline", 0.8f }
                    },
                    new Dictionary<string, float> { 
                        { "Afraid", 0.7f }
                    },
                    0.4f
                ),
                
                new DecisionOption(
                    "flee", 
                    "Attempt to flee",
                    new Dictionary<string, float> { 
                        { "Aggression", 0.1f }, 
                        { "Discipline", 0.2f },
                        { "Optimism", 0.2f }
                    },
                    new Dictionary<string, float> { 
                        { "Afraid", 0.9f }
                    },
                    0.3f
                )
            };
            
            // Social decision options
            library[DecisionType.Social] = new List<DecisionOption>
            {
                new DecisionOption(
                    "friendly_chat", 
                    "Engage in friendly conversation",
                    new Dictionary<string, float> { 
                        { "Friendliness", 0.7f }, 
                        { "Sociability", 0.7f } 
                    },
                    new Dictionary<string, float> { 
                        { "Happy", 0.6f },
                        { "Sad", -0.3f },
                        { "Angry", -0.5f }
                    },
                    0.6f
                ),
                
                new DecisionOption(
                    "share_rumor", 
                    "Share a rumor or information",
                    new Dictionary<string, float> { 
                        { "Sociability", 0.6f }, 
                        { "Curiosity", 0.5f }
                    },
                    new Dictionary<string, float> { 
                        { "Curious", 0.7f }
                    },
                    0.5f
                ),
                
                new DecisionOption(
                    "intimidate", 
                    "Intimidate or threaten",
                    new Dictionary<string, float> { 
                        { "Aggression", 0.8f }, 
                        { "Friendliness", 0.1f }
                    },
                    new Dictionary<string, float> { 
                        { "Angry", 0.8f }
                    },
                    0.3f
                ),
                
                new DecisionOption(
                    "avoid_interaction", 
                    "Avoid social interaction",
                    new Dictionary<string, float> { 
                        { "Sociability", 0.1f }
                    },
                    new Dictionary<string, float> { 
                        { "Sad", 0.6f },
                        { "Afraid", 0.5f }
                    },
                    0.3f
                )
            };
            
            // Economic decision options
            library[DecisionType.Economic] = new List<DecisionOption>
            {
                new DecisionOption(
                    "haggle_aggressive", 
                    "Haggle aggressively",
                    new Dictionary<string, float> { 
                        { "Aggression", 0.7f }, 
                        { "Intelligence", 0.6f }
                    },
                    new Dictionary<string, float> { 
                        { "Angry", 0.4f }
                    },
                    0.5f
                ),
                
                new DecisionOption(
                    "haggle_fair", 
                    "Haggle for fair price",
                    new Dictionary<string, float> { 
                        { "Discipline", 0.6f }, 
                        { "Intelligence", 0.6f },
                        { "Friendliness", 0.5f }
                    },
                    null,
                    0.6f
                ),
                
                new DecisionOption(
                    "accept_price", 
                    "Accept offered price",
                    new Dictionary<string, float> { 
                        { "Discipline", 0.3f },
                        { "Friendliness", 0.7f }
                    },
                    new Dictionary<string, float> { 
                        { "Happy", 0.5f },
                        { "Afraid", 0.4f }
                    },
                    0.4f
                ),
                
                new DecisionOption(
                    "walk_away", 
                    "Walk away from transaction",
                    new Dictionary<string, float> { 
                        { "Discipline", 0.7f }
                    },
                    new Dictionary<string, float> { 
                        { "Angry", 0.6f }
                    },
                    0.3f
                )
            };
            
            // Movement decision options
            library[DecisionType.Movement] = new List<DecisionOption>
            {
                new DecisionOption(
                    "explore_new_area", 
                    "Explore a new area",
                    new Dictionary<string, float> { 
                        { "Curiosity", 0.8f }, 
                        { "Optimism", 0.6f }
                    },
                    new Dictionary<string, float> { 
                        { "Curious", 0.8f },
                        { "Afraid", -0.7f }
                    },
                    0.5f
                ),
                
                new DecisionOption(
                    "stay_familiar", 
                    "Stay in familiar territory",
                    new Dictionary<string, float> { 
                        { "Curiosity", 0.2f }, 
                        { "Discipline", 0.6f }
                    },
                    new Dictionary<string, float> { 
                        { "Afraid", 0.6f }
                    },
                    0.5f
                ),
                
                new DecisionOption(
                    "follow_crowd", 
                    "Follow the crowd",
                    new Dictionary<string, float> { 
                        { "Sociability", 0.7f }, 
                        { "Discipline", 0.3f }
                    },
                    null,
                    0.4f
                ),
                
                new DecisionOption(
                    "seek_resources", 
                    "Seek out resources",
                    new Dictionary<string, float> { 
                        { "Intelligence", 0.7f }, 
                        { "Discipline", 0.6f }
                    },
                    null,
                    0.6f
                )
            };
            
            // Quest decision options
            library[DecisionType.Quest] = new List<DecisionOption>
            {
                new DecisionOption(
                    "accept_quest", 
                    "Accept the quest",
                    new Dictionary<string, float> { 
                        { "Optimism", 0.7f }, 
                        { "Curiosity", 0.6f }
                    },
                    new Dictionary<string, float> { 
                        { "Curious", 0.6f },
                        { "Happy", 0.4f }
                    },
                    0.6f
                ),
                
                new DecisionOption(
                    "negotiate_reward", 
                    "Negotiate for better reward",
                    new Dictionary<string, float> { 
                        { "Intelligence", 0.7f }, 
                        { "Aggression", 0.5f }
                    },
                    null,
                    0.5f
                ),
                
                new DecisionOption(
                    "request_details", 
                    "Request more details",
                    new Dictionary<string, float> { 
                        { "Intelligence", 0.8f }, 
                        { "Discipline", 0.7f },
                        { "Curiosity", 0.6f }
                    },
                    new Dictionary<string, float> { 
                        { "Curious", 0.7f }
                    },
                    0.5f
                ),
                
                new DecisionOption(
                    "reject_quest", 
                    "Reject the quest",
                    new Dictionary<string, float> { 
                        { "Optimism", 0.2f },
                        { "Discipline", 0.5f }
                    },
                    new Dictionary<string, float> { 
                        { "Afraid", 0.6f },
                        { "Sad", 0.4f }
                    },
                    0.3f
                )
            };
            
            return library;
        }

        /// <summary>
        /// Add a custom decision option to the library
        /// </summary>
        public void AddDecisionOption(DecisionType type, DecisionOption option)
        {
            if (!_decisionLibrary.ContainsKey(type))
            {
                _decisionLibrary[type] = new List<DecisionOption>();
            }
            
            _decisionLibrary[type].Add(option);
        }

        /// <summary>
        /// Set a custom seed for the random number generator
        /// </summary>
        public void SetRandomSeed(int seed)
        {
            _random = new System.Random(seed);
        }
    }
} 