using System;
using System.Collections.Generic;

namespace VDM.Motifs
{
    /// <summary>
    /// Adapts motif changes to dialogue system (injects motif-relevant topics/phrases).
    /// </summary>
    public class MotifDialogueAdapter : IMotifObserver
    {
        public event Action<List<string>> OnDialogueTopicsChanged;

        public MotifDialogueAdapter()
        {
            MotifDispatcher.Instance.Register(this);
        }

        /// <summary>
        /// Called when a motif changes. Updates dialogue topics.
        /// </summary>
        public void OnMotifChanged(Motif motif)
        {
            // Example: Generate topics based on motif tags and name
            var topics = new List<string>(motif.Tags);
            topics.Add(motif.Name);
            OnDialogueTopicsChanged?.Invoke(topics);
        }
    }
} 