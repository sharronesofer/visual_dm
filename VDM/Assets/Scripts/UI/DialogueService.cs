// <copyright file="DialogueService.cs" company="PlaceholderCompany">
// Copyright (c) PlaceholderCompany. All rights reserved.
// </copyright>

namespace VisualDM.UI
{
    using System;
    using UnityEngine;

    /// <summary>
    /// Provides methods to request and handle dialogue interactions.
    /// </summary>
    public static class DialogueService
    {
        /// <summary>
        /// Requests a dialogue for the given NPC and invokes the callback with the response.
        /// </summary>
        /// <param name="npc">The NPCController requesting dialogue.</param>
        /// <param name="npcName">The name of the NPC.</param>
        /// <param name="callback">The callback to invoke with the dialogue response.</param>
        public static void RequestDialogue(MonoBehaviour npc, string npcName, Action<string> callback)
        {
            // Simulate a dialogue response (replace with real logic as needed)
            npc.StartCoroutine(SimulateDialogueResponse(npcName, callback));
        }

        private static System.Collections.IEnumerator SimulateDialogueResponse(string npcName, Action<string> callback)
        {
            // Simulate loading delay
            yield return new WaitForSeconds(1.0f);
            // Simulate a response
            callback?.Invoke($"Hello, I am {npcName}. This is a generated dialogue response.");
        }
    }
}