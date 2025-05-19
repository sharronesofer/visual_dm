#if UNITY_EDITOR
using NUnit.Framework;
using VDM.NPC;

namespace VDM.Tests.NPC
{
    public class RumorResponseHandlerTests
    {
        [Test]
        public void ReceiveRumor_Queues_By_Priority()
        {
            var handler = new RumorResponseHandler(1);
            var low = new RumorData { Content = "Mild news", Category = RumorCategory.News, BelievabilityScores = { [1] = 0.2f } };
            var high = new RumorData { Content = "Danger!", Category = RumorCategory.Danger, BelievabilityScores = { [1] = 0.9f } };
            handler.ReceiveRumor(low);
            handler.ReceiveRumor(high);
            Assert.AreEqual("Danger!", handler.GetTopRumor().Content);
        }

        [Test]
        public void SeekVerification_Does_Not_Throw()
        {
            var handler = new RumorResponseHandler(1);
            var rumor = new RumorData { Content = "Test", Category = RumorCategory.Mystery };
            Assert.DoesNotThrow(() => handler.SeekVerification(rumor));
        }
    }
}
#endif 