using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using VisualDM.Systems.Inventory;
using VisualDM.Theft;

namespace VisualDM.UI
{
    public class InventoryUI : MonoBehaviour
    {
        private Canvas canvas;
        private GameObject modalPanel;
        private GameObject inventoryPanel;
        private GameObject lootPanel;
        private GameObject tooltipPanel;
        private Text tooltipText;
        private List<GameObject> inventorySlots = new List<GameObject>();
        private List<GameObject> lootSlots = new List<GameObject>();
        private Inventory inventory;
        private List<Item> lootItems = new List<Item>();
        private int slotsPerRow = 5;
        private float slotSize = 80f;
        private float slotPadding = 10f;
        private Text promptText;
        private GameObject errorOverlay;
        private Text errorText;
        private GameObject tutorialOverlay;
        private Text tutorialText;
        private InventorySystemsSystem feedbackSystem;
        private const string TutorialSeenKey = "InventoryTutorialSeen";

        public void Initialize(Inventory playerInventory, InventorySystemsSystem feedback = null)
        {
            inventory = playerInventory;
            feedbackSystem = feedback;
            CreateCanvas();
            CreateModal();
            inventory.OnInventoryChanged += UpdateInventoryDisplay;
            Hide();
            if (!PlayerPrefs.HasKey(TutorialSeenKey))
                ShowTutorial();
        }

        private void CreateCanvas()
        {
            GameObject canvasObj = new GameObject("InventoryUICanvas");
            canvas = canvasObj.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasObj.AddComponent<CanvasScaler>().uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            canvasObj.AddComponent<GraphicRaycaster>();
            DontDestroyOnLoad(canvasObj);
        }

        private void CreateModal()
        {
            modalPanel = new GameObject("InventoryModal");
            var rect = modalPanel.AddComponent<RectTransform>();
            modalPanel.transform.SetParent(canvas.transform, false);
            rect.anchorMin = new Vector2(0.1f, 0.1f);
            rect.anchorMax = new Vector2(0.9f, 0.9f);
            rect.offsetMin = Vector2.zero;
            rect.offsetMax = Vector2.zero;
            var image = modalPanel.AddComponent<Image>();
            image.color = new Color(0, 0, 0, 0.85f);

            // Inventory Panel
            inventoryPanel = new GameObject("InventoryPanel");
            var invRect = inventoryPanel.AddComponent<RectTransform>();
            inventoryPanel.transform.SetParent(modalPanel.transform, false);
            invRect.anchorMin = new Vector2(0f, 0f);
            invRect.anchorMax = new Vector2(0.45f, 1f);
            invRect.offsetMin = Vector2.zero;
            invRect.offsetMax = Vector2.zero;
            inventoryPanel.AddComponent<Image>().color = new Color(0.1f, 0.1f, 0.1f, 0.9f);

            // Loot Panel
            lootPanel = new GameObject("LootPanel");
            var lootRect = lootPanel.AddComponent<RectTransform>();
            lootPanel.transform.SetParent(modalPanel.transform, false);
            lootRect.anchorMin = new Vector2(0.55f, 0f);
            lootRect.anchorMax = new Vector2(1f, 1f);
            lootRect.offsetMin = Vector2.zero;
            lootRect.offsetMax = Vector2.zero;
            lootPanel.AddComponent<Image>().color = new Color(0.15f, 0.15f, 0.15f, 0.9f);

            // Tooltip Panel
            tooltipPanel = new GameObject("TooltipPanel");
            var tooltipRect = tooltipPanel.AddComponent<RectTransform>();
            tooltipPanel.transform.SetParent(canvas.transform, false);
            tooltipRect.sizeDelta = new Vector2(300, 180);
            tooltipPanel.AddComponent<Image>().color = new Color(0.2f, 0.2f, 0.2f, 0.95f);
            tooltipText = new GameObject("TooltipText").AddComponent<Text>();
            tooltipText.transform.SetParent(tooltipPanel.transform, false);
            tooltipText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            tooltipText.color = Color.white;
            tooltipText.alignment = TextAnchor.UpperLeft;
            tooltipText.rectTransform.anchorMin = Vector2.zero;
            tooltipText.rectTransform.anchorMax = Vector2.one;
            tooltipText.rectTransform.offsetMin = Vector2.zero;
            tooltipText.rectTransform.offsetMax = Vector2.zero;
            tooltipPanel.SetActive(false);

            // Prompt Text
            var promptObj = new GameObject("PromptText");
            promptText = promptObj.AddComponent<Text>();
            promptObj.transform.SetParent(modalPanel.transform, false);
            promptText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            promptText.color = Color.yellow;
            promptText.alignment = TextAnchor.UpperCenter;
            promptText.rectTransform.anchorMin = new Vector2(0.25f, 0.9f);
            promptText.rectTransform.anchorMax = new Vector2(0.75f, 1f);
            promptText.rectTransform.offsetMin = Vector2.zero;
            promptText.rectTransform.offsetMax = Vector2.zero;
            // Error Overlay
            errorOverlay = new GameObject("ErrorOverlay");
            errorText = errorOverlay.AddComponent<Text>();
            errorOverlay.transform.SetParent(modalPanel.transform, false);
            errorText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            errorText.color = Color.red;
            errorText.alignment = TextAnchor.MiddleCenter;
            errorText.rectTransform.anchorMin = new Vector2(0.2f, 0.4f);
            errorText.rectTransform.anchorMax = new Vector2(0.8f, 0.6f);
            errorText.rectTransform.offsetMin = Vector2.zero;
            errorText.rectTransform.offsetMax = Vector2.zero;
            errorOverlay.SetActive(false);
            // Tutorial Overlay
            tutorialOverlay = new GameObject("TutorialOverlay");
            tutorialText = tutorialOverlay.AddComponent<Text>();
            tutorialOverlay.transform.SetParent(canvas.transform, false);
            tutorialText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            tutorialText.color = Color.cyan;
            tutorialText.alignment = TextAnchor.MiddleCenter;
            tutorialText.rectTransform.anchorMin = new Vector2(0.2f, 0.3f);
            tutorialText.rectTransform.anchorMax = new Vector2(0.8f, 0.7f);
            tutorialText.rectTransform.offsetMin = Vector2.zero;
            tutorialText.rectTransform.offsetMax = Vector2.zero;
            tutorialOverlay.SetActive(false);
        }

        public void Show(List<Item> loot)
        {
            lootItems = loot;
            modalPanel.SetActive(true);
            UpdateInventoryDisplay();
            UpdateLootDisplay();
            SetPrompt("Select an item to take or discard.");
        }

        public void Hide()
        {
            modalPanel.SetActive(false);
            tooltipPanel.SetActive(false);
        }

        private void UpdateInventoryDisplay()
        {
            foreach (var slot in inventorySlots)
                Destroy(slot);
            inventorySlots.Clear();
            var slots = inventory.Slots;
            for (int i = 0; i < slots.Count; i++)
            {
                var slotObj = CreateSlot(slots[i].Item, slots[i].Quantity, i, true);
                slotObj.transform.SetParent(inventoryPanel.transform, false);
                inventorySlots.Add(slotObj);
            }
        }

        private void UpdateLootDisplay()
        {
            foreach (var slot in lootSlots)
                Destroy(slot);
            lootSlots.Clear();
            for (int i = 0; i < lootItems.Count; i++)
            {
                var slotObj = CreateSlot(lootItems[i], 1, i, false);
                slotObj.transform.SetParent(lootPanel.transform, false);
                lootSlots.Add(slotObj);
            }
        }

        private GameObject CreateSlot(Item item, int quantity, int index, bool isInventory)
        {
            var slotObj = new GameObject((isInventory ? "InventorySlot_" : "LootSlot_") + index);
            var rect = slotObj.AddComponent<RectTransform>();
            rect.sizeDelta = new Vector2(slotSize, slotSize);
            var image = slotObj.AddComponent<Image>();
            image.color = GetRarityColor(item.Rarity);
            if (item.Icon != null)
            {
                var iconObj = new GameObject("Icon");
                var iconRect = iconObj.AddComponent<RectTransform>();
                iconObj.transform.SetParent(slotObj.transform, false);
                iconRect.sizeDelta = new Vector2(slotSize * 0.8f, slotSize * 0.8f);
                var iconImage = iconObj.AddComponent<Image>();
                iconImage.sprite = item.Icon;
                iconImage.preserveAspect = true;
            }
            if (quantity > 1)
            {
                var qtyObj = new GameObject("Quantity");
                var qtyText = qtyObj.AddComponent<Text>();
                qtyObj.transform.SetParent(slotObj.transform, false);
                qtyText.text = quantity.ToString();
                qtyText.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
                qtyText.color = Color.white;
                qtyText.alignment = TextAnchor.LowerRight;
                qtyText.rectTransform.anchorMin = new Vector2(0.7f, 0f);
                qtyText.rectTransform.anchorMax = new Vector2(1f, 0.3f);
                qtyText.rectTransform.offsetMin = Vector2.zero;
                qtyText.rectTransform.offsetMax = Vector2.zero;
            }
            // Stolen item indicator
            if (StolenStateManager.Instance != null && StolenStateManager.Instance.GetItemState(item.ID) == StolenState.Stolen)
            {
                var stolenOverlay = new GameObject("StolenOverlay");
                var overlayRect = stolenOverlay.AddComponent<RectTransform>();
                stolenOverlay.transform.SetParent(slotObj.transform, false);
                overlayRect.sizeDelta = rect.sizeDelta;
                var overlayImage = stolenOverlay.AddComponent<Image>();
                overlayImage.color = new Color(1f, 0f, 0f, 0.3f); // semi-transparent red
                overlayImage.raycastTarget = false;
            }
            var btn = slotObj.AddComponent<Button>();
            btn.onClick.AddListener(() => ShowTooltip(item, isInventory));
            return slotObj;
        }

        private void ShowTooltip(Item item, bool isInventory)
        {
            tooltipPanel.SetActive(true);
            tooltipText.text = $"<b>{item.Name}</b>\n{item.Description}\nRarity: {item.Rarity}\n";
            foreach (var stat in item.Stats)
            {
                tooltipText.text += $"{stat.Key}: {stat.Value}\n";
            }
            if (StolenStateManager.Instance != null && StolenStateManager.Instance.GetItemState(item.ID) == StolenState.Stolen)
            {
                tooltipText.text += "\n<color=red><b>STOLEN ITEM</b></color>";
            }
        }

        private Color GetRarityColor(ItemRarity rarity)
        {
            switch (rarity)
            {
                case ItemRarity.Common: return Color.gray;
                case ItemRarity.Uncommon: return Color.green;
                case ItemRarity.Rare: return Color.blue;
                case ItemRarity.Epic: return new Color(0.6f, 0f, 0.8f);
                case ItemRarity.Legendary: return new Color(1f, 0.5f, 0f);
                default: return Color.white;
            }
        }

        public void ShowError(string message)
        {
            errorText.text = message;
            errorOverlay.SetActive(true);
            feedbackSystem?.PlayErrorSound();
            Invoke("HideError", 2f);
        }

        private void HideError()
        {
            errorOverlay.SetActive(false);
        }

        public void SetPrompt(string message)
        {
            promptText.text = message;
        }

        public void ShowTutorial()
        {
            tutorialText.text = "Welcome! This is the inventory give/take system. Select an item to take, or discard an item if your inventory is full. You can always decline loot. Click anywhere to continue.";
            tutorialOverlay.SetActive(true);
            tutorialOverlay.AddComponent<Button>().onClick.AddListener(() => {
                tutorialOverlay.SetActive(false);
                PlayerPrefs.SetInt(TutorialSeenKey, 1);
            });
        }

        public void HighlightSlot(GameObject slot, bool success)
        {
            var image = slot.GetComponent<Image>();
            if (image != null)
            {
                Color original = image.color;
                image.color = success ? Color.green : Color.red;
                feedbackSystem?.PlaySuccessSound();
                LeanTween.value(slot, c => image.color = c, image.color, original, 0.5f);
            }
        }
    }
} 