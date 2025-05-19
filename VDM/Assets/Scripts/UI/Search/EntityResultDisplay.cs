using UnityEngine;
using UnityEngine.UI;
using System;

namespace VisualDM.UI
{
    public class EntityResultDisplay : MonoBehaviour
    {
        public RectTransform displayPanel;
        public Image mapPreviewImage;
        public Text detailsText;

        void Awake()
        {
            if (displayPanel == null)
                displayPanel = CreatePanel("EntityDisplayPanel", new Vector2(400, 200));
            if (mapPreviewImage == null)
                mapPreviewImage = CreateMapPreview();
            if (detailsText == null)
                detailsText = CreateDetailsText();
        }

        private RectTransform CreatePanel(string name, Vector2 size)
        {
            var go = new GameObject(name);
            go.transform.SetParent(transform);
            var rect = go.AddComponent<RectTransform>();
            rect.sizeDelta = size;
            return rect;
        }

        private Image CreateMapPreview()
        {
            var go = new GameObject("MapPreview");
            go.transform.SetParent(displayPanel);
            var img = go.AddComponent<Image>();
            img.rectTransform.sizeDelta = new Vector2(100, 100);
            return img;
        }

        private Text CreateDetailsText()
        {
            var go = new GameObject("DetailsText");
            go.transform.SetParent(displayPanel);
            var txt = go.AddComponent<Text>();
            txt.font = Resources.GetBuiltinResource<Font>("Arial.ttf");
            txt.rectTransform.anchoredPosition = new Vector2(120, 0);
            return txt;
        }

        public void DisplayWorld(string name, string description, Sprite mapSprite)
        {
            mapPreviewImage.sprite = mapSprite;
            detailsText.text = $"World: {name}\n{description}";
        }

        public void DisplayNPC(string name, string traits, string relationships)
        {
            mapPreviewImage.sprite = null;
            detailsText.text = $"NPC: {name}\nTraits: {traits}\nRelationships: {relationships}";
        }

        public void DisplayItem(string name, string properties)
        {
            mapPreviewImage.sprite = null;
            detailsText.text = $"Item: {name}\nProperties: {properties}";
        }
    }
} 