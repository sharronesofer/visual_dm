using NUnit.Framework;
using VDM.Systems;

namespace VDM.Tests.Systems.Animation
{
    [TestFixture]
    public class AnimationCancellationHandlerTests
    {
        [Test]
        public void Constructor_InitializesCorrectly()
        {
            var handler = new AnimationCancellationHandler();
            Assert.IsNotNull(handler);
        }

        [Test]
        public void CancelAnimation_SetsCancelledFlag()
        {
            var handler = new AnimationCancellationHandler();
            handler.CancelAnimation();
            Assert.IsTrue(handler.IsCancelled);
        }

        [Test]
        public void Reset_ResetsCancelledFlag()
        {
            var handler = new AnimationCancellationHandler();
            handler.CancelAnimation();
            handler.Reset();
            Assert.IsFalse(handler.IsCancelled);
        }
    }
} 