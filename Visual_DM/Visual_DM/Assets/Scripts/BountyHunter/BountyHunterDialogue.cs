namespace VisualDM.BountyHunter
{
    public static class BountyHunterDialogue
    {
        private static readonly string[] taunts = new string[]
        {
            "You can't run forever!",
            "Your crimes have caught up with you!",
            "There's a price on your head, and I'm here to collect.",
            "Surrender now and I might go easy on you.",
            "Justice always finds its mark!"
        };

        public static string GetRandomTaunt()
        {
            return taunts[UnityEngine.Random.Range(0, taunts.Length)];
        }
    }
} 