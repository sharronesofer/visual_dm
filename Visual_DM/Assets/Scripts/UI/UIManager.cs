using UnityEngine;
using TMPro;
using UnityEngine.UI;

public static class UIManager
{
    // Initialize the HUD UI elements
    public static void InitializeHUD()
    {
        // Check if a Canvas already exists
        Canvas existingCanvas = Object.FindObjectOfType<Canvas>();
        Canvas canvas;
        if (existingCanvas == null)
        {
            // Create a new Canvas
            GameObject canvasGO = new GameObject("HUD_Canvas");
            canvas = canvasGO.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasGO.AddComponent<CanvasScaler>();
            canvasGO.AddComponent<GraphicRaycaster>();
        }
        else
        {
            canvas = existingCanvas;
        }

        // Check if a HUD label already exists
        var existingLabel = Object.FindObjectOfType<TextMeshProUGUI>();
        if (existingLabel != null && existingLabel.text == "Procedural 2D Game Loaded")
            return;

        // Create a new TextMeshProUGUI element
        GameObject textGO = new GameObject("HUD_Label");
        textGO.transform.SetParent(canvas.transform, false);
        var text = textGO.AddComponent<TextMeshProUGUI>();
        text.text = "Procedural 2D Game Loaded";
        text.fontSize = 32;
        text.color = Color.white;
        text.alignment = TextAlignmentOptions.TopLeft;
        text.rectTransform.anchorMin = new Vector2(0, 1);
        text.rectTransform.anchorMax = new Vector2(0, 1);
        text.rectTransform.pivot = new Vector2(0, 1);
        text.rectTransform.anchoredPosition = new Vector2(10, -10);
    }

    private static GameObject dialogueBoxGO;
    private static TextMeshProUGUI dialogueText;
    private static GameObject loadingIndicatorGO;

    static UIManager()
    {
        DialogueStateManager.OnStateChanged += OnDialogueStateChanged;
    }

    private static void OnDialogueStateChanged(DialogueState state, string text, string error)
    {
        switch (state)
        {
            case DialogueState.Pending:
                ShowDialogue(text, true);
                break;
            case DialogueState.Received:
                ShowDialogue(text, false);
                break;
            case DialogueState.Error:
                ShowDialogue(error, false);
                break;
            case DialogueState.Idle:
            default:
                HideDialogue();
                break;
        }
    }

    public static void CreateDialogueUI()
    {
        Canvas canvas = Object.FindObjectOfType<Canvas>();
        if (canvas == null) return;

        // Dialogue box
        dialogueBoxGO = new GameObject("DialogueBox");
        dialogueBoxGO.transform.SetParent(canvas.transform, false);
        var bg = dialogueBoxGO.AddComponent<Image>();
        bg.color = new Color(0, 0, 0, 0.8f);
        var rect = dialogueBoxGO.GetComponent<RectTransform>();
        rect.anchorMin = new Vector2(0.5f, 0);
        rect.anchorMax = new Vector2(0.5f, 0);
        rect.pivot = new Vector2(0.5f, 0);
        rect.sizeDelta = new Vector2(600, 120);
        rect.anchoredPosition = new Vector2(0, 80);
        dialogueBoxGO.SetActive(false);

        // Dialogue text
        var textGO = new GameObject("DialogueText");
        textGO.transform.SetParent(dialogueBoxGO.transform, false);
        dialogueText = textGO.AddComponent<TextMeshProUGUI>();
        dialogueText.text = "";
        dialogueText.fontSize = 28;
        dialogueText.color = Color.white;
        dialogueText.alignment = TextAlignmentOptions.MidlineLeft;
        var textRect = dialogueText.rectTransform;
        textRect.anchorMin = new Vector2(0, 0);
        textRect.anchorMax = new Vector2(1, 1);
        textRect.offsetMin = new Vector2(20, 20);
        textRect.offsetMax = new Vector2(-20, -20);

        // Loading indicator
        loadingIndicatorGO = new GameObject("DialogueLoading");
        loadingIndicatorGO.transform.SetParent(dialogueBoxGO.transform, false);
        var loadingText = loadingIndicatorGO.AddComponent<TextMeshProUGUI>();
        loadingText.text = "...";
        loadingText.fontSize = 24;
        loadingText.color = Color.gray;
        loadingText.alignment = TextAlignmentOptions.BottomRight;
        var loadingRect = loadingText.rectTransform;
        loadingRect.anchorMin = new Vector2(1, 0);
        loadingRect.anchorMax = new Vector2(1, 0);
        loadingRect.pivot = new Vector2(1, 0);
        loadingRect.anchoredPosition = new Vector2(-10, 10);
        loadingIndicatorGO.SetActive(false);
    }

    public static void ShowDialogue(string text, bool loading = false)
    {
        if (dialogueBoxGO == null) return;
        dialogueBoxGO.SetActive(true);
        dialogueText.text = text;
        loadingIndicatorGO.SetActive(loading);
    }

    public static void HideDialogue()
    {
        if (dialogueBoxGO == null) return;
        dialogueBoxGO.SetActive(false);
        dialogueText.text = "";
        loadingIndicatorGO.SetActive(false);
    }
} 