namespace VisualDM.Tests
{
    using NUnit.Framework;
    using VisualDM.NPC;
    using UnityEngine;

    public class NPCPersonalityTests
    {
        private class TestTemplate : INPCTemplate
        {
            public string TemplateName => "TestTemplate";
            public PersonalityProfile GetDefaultPersonality() => new PersonalityProfile(0.8f, 0.2f, 0.5f, 0.7f, 0.6f, 0.9f, 0.4f);
        }

        [Test]
        public void RandomTraitGenerationProducesValidRange()
        {
            var profile = NPCTraitGenerator.GenerateRandomProfile();
            Assert.That(profile.Friendliness, Is.InRange(0f, 1f));
            Assert.That(profile.Aggression, Is.InRange(0f, 1f));
            Assert.That(profile.Curiosity, Is.InRange(0f, 1f));
            Assert.That(profile.Discipline, Is.InRange(0f, 1f));
            Assert.That(profile.Optimism, Is.InRange(0f, 1f));
            Assert.That(profile.Sociability, Is.InRange(0f, 1f));
            Assert.That(profile.Intelligence, Is.InRange(0f, 1f));
        }

        [Test]
        public void TemplateTraitGenerationIsCloseToTemplate()
        {
            var template = new TestTemplate();
            var profile = NPCTraitGenerator.GenerateFromTemplate(template, 0.05f, new System.Random(42));
            var baseProfile = template.GetDefaultPersonality();
            Assert.That(Mathf.Abs(profile.Friendliness - baseProfile.Friendliness), Is.LessThanOrEqualTo(0.05f));
            Assert.That(Mathf.Abs(profile.Aggression - baseProfile.Aggression), Is.LessThanOrEqualTo(0.05f));
        }

        [Test]
        public void MoodTransitionsAndDecayWork()
        {
            var mood = new NPCMood();
            mood.ApplyMood(MoodState.Happy, 0.8f);
            Assert.AreEqual(MoodState.Happy, mood.CurrentMood);
            Assert.That(mood.MoodIntensity, Is.EqualTo(0.8f).Within(0.01f));
            mood.DecayMood(20f); // Should decay to neutral
            Assert.AreEqual(MoodState.Neutral, mood.CurrentMood);
            Assert.That(mood.MoodIntensity, Is.EqualTo(0f).Within(0.01f));
        }

        [Test]
        public void BehaviorModifierCalculatesWeights()
        {
            var profile = new PersonalityProfile(0.5f, 0.7f, 0.3f, 0.6f, 0.4f, 0.8f, 0.2f);
            var mood = new NPCMood();
            var modifier = new NPCBehaviorModifier(profile, mood);
            Assert.That(modifier.GetAggressionWeight(), Is.EqualTo(0.7f).Within(0.01f));
            mood.ApplyMood(MoodState.Angry, 0.6f);
            Assert.That(modifier.GetAggressionWeight(), Is.GreaterThan(0.7f));
        }
    }
} 