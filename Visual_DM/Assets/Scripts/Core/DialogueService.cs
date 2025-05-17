using System.Collections;
using UnityEngine;
using UnityEngine.Networking;
using System;

namespace VisualDM.Core
{
    public static class DialogueService
    {
        private static string dialogueEndpoint = "http://localhost:5000/dialogue";

        public static void RequestDialogue(MonoBehaviour context, string npcName, Action<string> onResponse)
        {
            context.StartCoroutine(RequestDialogueCoroutine(npcName, onResponse));
        }

        private static IEnumerator RequestDialogueCoroutine(string npcName, Action<string> onResponse)
        {
            // Prepare JSON payload
            string json = JsonUtility.ToJson(new DialogueRequest { npc = npcName });
            var request = new UnityWebRequest(dialogueEndpoint, "POST");
            byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);
            request.uploadHandler = new UploadHandlerRaw(bodyRaw);
            request.downloadHandler = new DownloadHandlerBuffer();
            request.SetRequestHeader("Content-Type", "application/json");

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                string responseText = request.downloadHandler.text;
                onResponse?.Invoke(responseText);
            }
            else
            {
                Debug.LogError($"DialogueService error: {request.error}");
                onResponse?.Invoke("[Error: Could not fetch dialogue]");
            }
        }

        [Serializable]
        private class DialogueRequest
        {
            public string npc;
        }
    }
} 