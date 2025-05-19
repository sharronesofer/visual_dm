using UnityEngine;
using UnityEngine.UI;

namespace VisualDM.Bounty
{
    public class BountyUIController : MonoBehaviour
    {
        private Text bountyText;
        private Image background;
        private GameObject wantedIcon;
        private Text witnessText;

        private void Start()
        {
            CreateUI();
            BountyManager.Instance.OnBountyChanged += UpdateBountyUI;
            if (WitnessManager.Instance != null)
                WitnessManager.Instance.OnWitnessStateChanged += UpdateWitnessUI;
            UpdateBountyUI(BountyManager.Instance.GetCurrentBounty());
        }

        private void CreateUI()
        {
            var canvasGO = new GameObject("BountyUICanvas");
            var canvas = canvasGO.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasGO.AddComponent<CanvasScaler>();
            canvasGO.AddComponent<GraphicRaycaster>();
            DontDestroyOnLoad(canvasGO);

            var panelGO = new GameObject("BountyPanel");
            panelGO.transform.SetParent(canvasGO.transform);
            background = panelGO.AddComponent<Image>();
            background.rectTransform.anchorMin = new Vector2(0.75f, 0.9f);
            background.rectTransform.anchorMax = new Vector2(0.98f, 0.98f);
            background.rectTransform.offsetMin = Vector2.zero;
            background.rectTransform.offsetMax = Vector2.zero;

            var textGO = new GameObject("BountyText");
            textGO.transform.SetParent(panelGO.transform);
            bountyText = textGO.AddComponent<Text>();
            bountyText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            bountyText.alignment = TextAnchor.MiddleCenter;
            bountyText.color = Color.white;
            bountyText.rectTransform.anchorMin = new Vector2(0, 0);
            bountyText.rectTransform.anchorMax = new Vector2(1, 1);
            bountyText.rectTransform.offsetMin = Vector2.zero;
            bountyText.rectTransform.offsetMax = Vector2.zero;

            wantedIcon = new GameObject("WantedIcon");
            wantedIcon.transform.SetParent(panelGO.transform);
            var iconImage = wantedIcon.AddComponent<Image>();
            iconImage.color = Color.red;
            iconImage.rectTransform.anchorMin = new Vector2(0.85f, 0.1f);
            iconImage.rectTransform.anchorMax = new Vector2(0.98f, 0.4f);
            iconImage.rectTransform.offsetMin = Vector2.zero;
            iconImage.rectTransform.offsetMax = Vector2.zero;
            wantedIcon.SetActive(false);

            var witnessGO = new GameObject("WitnessText");
            witnessGO.transform.SetParent(panelGO.transform);
            witnessText = witnessGO.AddComponent<Text>();
            witnessText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            witnessText.alignment = TextAnchor.UpperRight;
            witnessText.color = Color.yellow;
            witnessText.rectTransform.anchorMin = new Vector2(0.7f, 0.7f);
            witnessText.rectTransform.anchorMax = new Vector2(1f, 1f);
            witnessText.rectTransform.offsetMin = Vector2.zero;
            witnessText.rectTransform.offsetMax = Vector2.zero;
            witnessText.text = "";
        }

        private void UpdateBountyUI(float bounty)
        {
            string status = BountyManager.Instance.GetBountyStatus();
            bountyText.text = $"Bounty: {bounty:0} ({status})";
            if (bounty >= 1000f)
            {
                background.color = Color.red;
                wantedIcon.SetActive(true);
            }
            else if (bounty >= 500f)
            {
                background.color = Color.yellow;
                wantedIcon.SetActive(true);
            }
            else if (bounty > 0f)
            {
                background.color = Color.green;
                wantedIcon.SetActive(false);
            }
            else
            {
                background.color = Color.gray;
                wantedIcon.SetActive(false);
            }
        }

        private void UpdateWitnessUI(WitnessNPCController witness, WitnessState state)
        {
            if (state == WitnessState.Reporting)
                witnessText.text = "Witnessed!";
            else if (state == WitnessState.Investigating)
                witnessText.text = "Being Watched";
            else
                witnessText.text = "";
        }
    }
} 