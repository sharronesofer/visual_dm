using NUnit.Framework;
using VDM.Systems;
using UnityEngine;

namespace VDM.Tests.Systems.Animation
{
    [TestFixture]
    public class AnimationEffectConfigTests
    {
        [Test]
        public void CreateInstance_InitializesCorrectly()
        {
            var config = ScriptableObject.CreateInstance<AnimationEffectConfig>();
            Assert.IsNotNull(config);
        }

        [Test]
        public void SetAndGetEffectName_Works()
        {
            var config = ScriptableObject.CreateInstance<AnimationEffectConfig>();
            config.EffectName = "FadeIn";
            Assert.AreEqual("FadeIn", config.EffectName);
        }

        [Test]
        public void SetAndGetDuration_Works()
        {
            var config = ScriptableObject.CreateInstance<AnimationEffectConfig>();
            config.Duration = 1.5f;
            Assert.AreEqual(1.5f, config.Duration, 1e-4);
        }
    }
} 