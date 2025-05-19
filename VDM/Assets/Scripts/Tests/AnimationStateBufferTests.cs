using NUnit.Framework;

namespace VisualDM.Tests
{
    public class AnimationStateBufferTests
    {
        [Test]
        public void AnimationStateBuffer_SwapsAndVersionsCorrectly()
        {
            var buffer = new AnimationStateBuffer<int>();
            buffer.WriteState = 42;
            buffer.SwapBuffers();
            Assert.AreEqual(42, buffer.ReadState);
            int v1 = buffer.Version;
            buffer.WriteState = 99;
            buffer.SwapBuffers();
            Assert.AreEqual(99, buffer.ReadState);
            Assert.Greater(buffer.Version, v1);
        }
    }
} 