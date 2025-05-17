using UnityEngine;
using UnityEngine.UI;
using System.Collections;

namespace VisualDM.Bounty
{
    public class BountyNotificationSystem : MonoBehaviour
    {
        private Canvas notificationCanvas;
        private Text notificationText;
        private AudioSource audioSource;
        public AudioClip bountyIncreaseClip;
        public AudioClip bountyDecreaseClip;

        private void Start()
        {
            CreateNotificationUI();
            BountyManager.Instance.OnBountyChanged += OnBountyChanged;
        }

        private void CreateNotificationUI()
        {
            var canvasGO = new GameObject("BountyNotificationCanvas");
            notificationCanvas = canvasGO.AddComponent<Canvas>();
            notificationCanvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasGO.AddComponent<CanvasScaler>();
            canvasGO.AddComponent<GraphicRaycaster>();
            DontDestroyOnLoad(canvasGO);

            var textGO = new GameObject("NotificationText");
            textGO.transform.SetParent(canvasGO.transform);
            notificationText = textGO.AddComponent<Text>();
            notificationText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            notificationText.alignment = TextAnchor.UpperCenter;
            notificationText.color = Color.white;
            notificationText.rectTransform.anchorMin = new Vector2(0.3f, 0.85f);
            notificationText.rectTransform.anchorMax = new Vector2(0.7f, 0.95f);
            notificationText.rectTransform.offsetMin = Vector2.zero;
            notificationText.rectTransform.offsetMax = Vector2.zero;
            notificationText.text = "";
            notificationText.enabled = false;

            audioSource = canvasGO.AddComponent<AudioSource>();
        }

        private float lastBounty = 0f;
        private void OnBountyChanged(float newBounty)
        {
            if (Mathf.Approximately(lastBounty, 0f))
            {
                lastBounty = newBounty;
                return;
            }
            if (newBounty > lastBounty)
            {
                ShowNotification($"Bounty Increased: {newBounty:0}", Color.red);
                if (bountyIncreaseClip) audioSource.PlayOneShot(bountyIncreaseClip);
            }
            else if (newBounty < lastBounty)
            {
                ShowNotification($"Bounty Decreased: {newBounty:0}", Color.green);
                if (bountyDecreaseClip) audioSource.PlayOneShot(bountyDecreaseClip);
            }
            lastBounty = newBounty;
        }

        private void ShowNotification(string message, Color color)
        {
            StopAllCoroutines();
            StartCoroutine(NotificationRoutine(message, color));
        }

        private IEnumerator NotificationRoutine(string message, Color color)
        {
            notificationText.text = message;
            notificationText.color = color;
            notificationText.enabled = true;
            float t = 0f;
            // Slide in
            while (t < 0.3f)
            {
                notificationText.rectTransform.anchoredPosition = Vector2.Lerp(new Vector2(0, 100), Vector2.zero, t / 0.3f);
                t += Time.unscaledDeltaTime;
                yield return null;
            }
            notificationText.rectTransform.anchoredPosition = Vector2.zero;
            yield return new WaitForSecondsRealtime(1.5f);
            // Fade out
            t = 0f;
            Color startColor = notificationText.color;
            while (t < 0.5f)
            {
                notificationText.color = Color.Lerp(startColor, new Color(startColor.r, startColor.g, startColor.b, 0), t / 0.5f);
                t += Time.unscaledDeltaTime;
                yield return null;
            }
            notificationText.enabled = false;
            notificationText.color = startColor;
        }
    }
} 