using NUnit.Framework;

namespace VisualDM.Tests
{
    public class ParallelSkinningJobTests
    {
        [Test]
        public void ParallelSkinningJob_ExecutesWithoutError()
        {
            float[] input = new float[32];
            float[] output = new float[32];
            var job = new ParallelSkinningJob(input, output, 0, 32);
            Assert.DoesNotThrow(() => job.Execute());
            Assert.IsTrue(job.IsCompleted);
        }
    }
} 