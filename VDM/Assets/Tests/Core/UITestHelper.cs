using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.EventSystems;
using UnityEngine.TestTools;
using NUnit.Framework;

namespace VDM.Tests.Core
{
    /// <summary>
    /// UI testing helper with utilities for Unity UI interaction testing
    /// </summary>
    public class UITestHelper : IDisposable
    {
        private Canvas _testCanvas;
        private EventSystem _eventSystem;
        private GraphicRaycaster _raycaster;
        private List<GameObject> _createdObjects;
        private bool _disposed;

        public UITestHelper()
        {
            _createdObjects = new List<GameObject>();
            SetupTestEnvironment();
        }

        private void SetupTestEnvironment()
        {
            // Create event system if none exists
            if (EventSystem.current == null)
            {
                var eventSystemObject = new GameObject("EventSystem");
                _eventSystem = eventSystemObject.AddComponent<EventSystem>();
                eventSystemObject.AddComponent<StandaloneInputModule>();
                _createdObjects.Add(eventSystemObject);
            }
        }

        /// <summary>
        /// Create a test canvas for UI testing
        /// </summary>
        public Canvas CreateTestCanvas()
        {
            var canvasObject = new GameObject("TestCanvas");
            _testCanvas = canvasObject.AddComponent<Canvas>();
            _testCanvas.renderMode = RenderMode.ScreenSpaceOverlay;
            
            canvasObject.AddComponent<CanvasScaler>();
            _raycaster = canvasObject.AddComponent<GraphicRaycaster>();
            
            _createdObjects.Add(canvasObject);
            return _testCanvas;
        }

        /// <summary>
        /// Create a test button with specified text
        /// </summary>
        public Button CreateTestButton(string text, Vector2 position = default, Vector2 size = default)
        {
            if (_testCanvas == null) CreateTestCanvas();

            var buttonObject = new GameObject("TestButton");
            buttonObject.transform.SetParent(_testCanvas.transform, false);
            
            var image = buttonObject.AddComponent<Image>();
            image.color = Color.white;
            
            var button = buttonObject.AddComponent<Button>();
            
            var textObject = new GameObject("Text");
            textObject.transform.SetParent(buttonObject.transform, false);
            
            var textComponent = textObject.AddComponent<Text>();
            textComponent.text = text;
            textComponent.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            textComponent.color = Color.black;
            textComponent.alignment = TextAnchor.MiddleCenter;
            
            var rectTransform = buttonObject.GetComponent<RectTransform>();
            if (size != default) rectTransform.sizeDelta = size;
            if (position != default) rectTransform.anchoredPosition = position;
            
            _createdObjects.Add(buttonObject);
            return button;
        }

        /// <summary>
        /// Create a test input field
        /// </summary>
        public InputField CreateTestInputField(string placeholder = "", Vector2 position = default, Vector2 size = default)
        {
            if (_testCanvas == null) CreateTestCanvas();

            var inputObject = new GameObject("TestInputField");
            inputObject.transform.SetParent(_testCanvas.transform, false);
            
            var image = inputObject.AddComponent<Image>();
            image.color = Color.white;
            
            var inputField = inputObject.AddComponent<InputField>();
            
            // Create text component for input
            var textObject = new GameObject("Text");
            textObject.transform.SetParent(inputObject.transform, false);
            
            var textComponent = textObject.AddComponent<Text>();
            textComponent.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            textComponent.color = Color.black;
            textComponent.supportRichText = false;
            
            inputField.textComponent = textComponent;
            
            // Create placeholder
            if (!string.IsNullOrEmpty(placeholder))
            {
                var placeholderObject = new GameObject("Placeholder");
                placeholderObject.transform.SetParent(inputObject.transform, false);
                
                var placeholderText = placeholderObject.AddComponent<Text>();
                placeholderText.text = placeholder;
                placeholderText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
                placeholderText.color = Color.gray;
                placeholderText.fontStyle = FontStyle.Italic;
                
                inputField.placeholder = placeholderText;
            }
            
            var rectTransform = inputObject.GetComponent<RectTransform>();
            if (size != default) rectTransform.sizeDelta = size;
            if (position != default) rectTransform.anchoredPosition = position;
            
            _createdObjects.Add(inputObject);
            return inputField;
        }

        /// <summary>
        /// Create a test toggle
        /// </summary>
        public Toggle CreateTestToggle(string labelText = "", Vector2 position = default)
        {
            if (_testCanvas == null) CreateTestCanvas();

            var toggleObject = new GameObject("TestToggle");
            toggleObject.transform.SetParent(_testCanvas.transform, false);
            
            var toggle = toggleObject.AddComponent<Toggle>();
            
            // Create background
            var backgroundObject = new GameObject("Background");
            backgroundObject.transform.SetParent(toggleObject.transform, false);
            
            var backgroundImage = backgroundObject.AddComponent<Image>();
            backgroundImage.color = Color.white;
            
            // Create checkmark
            var checkmarkObject = new GameObject("Checkmark");
            checkmarkObject.transform.SetParent(backgroundObject.transform, false);
            
            var checkmarkImage = checkmarkObject.AddComponent<Image>();
            checkmarkImage.color = Color.green;
            
            toggle.targetGraphic = backgroundImage;
            toggle.graphic = checkmarkImage;
            
            // Create label if provided
            if (!string.IsNullOrEmpty(labelText))
            {
                var labelObject = new GameObject("Label");
                labelObject.transform.SetParent(toggleObject.transform, false);
                
                var labelComponent = labelObject.AddComponent<Text>();
                labelComponent.text = labelText;
                labelComponent.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
                labelComponent.color = Color.black;
            }
            
            var rectTransform = toggleObject.GetComponent<RectTransform>();
            if (position != default) rectTransform.anchoredPosition = position;
            
            _createdObjects.Add(toggleObject);
            return toggle;
        }

        /// <summary>
        /// Create a test slider
        /// </summary>
        public Slider CreateTestSlider(float minValue = 0f, float maxValue = 1f, float value = 0.5f, Vector2 position = default)
        {
            if (_testCanvas == null) CreateTestCanvas();

            var sliderObject = new GameObject("TestSlider");
            sliderObject.transform.SetParent(_testCanvas.transform, false);
            
            var slider = sliderObject.AddComponent<Slider>();
            
            // Create background
            var backgroundObject = new GameObject("Background");
            backgroundObject.transform.SetParent(sliderObject.transform, false);
            
            var backgroundImage = backgroundObject.AddComponent<Image>();
            backgroundImage.color = Color.gray;
            
            // Create fill area
            var fillAreaObject = new GameObject("Fill Area");
            fillAreaObject.transform.SetParent(sliderObject.transform, false);
            
            var fillObject = new GameObject("Fill");
            fillObject.transform.SetParent(fillAreaObject.transform, false);
            
            var fillImage = fillObject.AddComponent<Image>();
            fillImage.color = Color.blue;
            
            // Create handle area
            var handleAreaObject = new GameObject("Handle Slide Area");
            handleAreaObject.transform.SetParent(sliderObject.transform, false);
            
            var handleObject = new GameObject("Handle");
            handleObject.transform.SetParent(handleAreaObject.transform, false);
            
            var handleImage = handleObject.AddComponent<Image>();
            handleImage.color = Color.white;
            
            slider.fillRect = fillObject.GetComponent<RectTransform>();
            slider.handleRect = handleObject.GetComponent<RectTransform>();
            slider.targetGraphic = handleImage;
            slider.direction = Slider.Direction.LeftToRight;
            
            slider.minValue = minValue;
            slider.maxValue = maxValue;
            slider.value = value;
            
            var rectTransform = sliderObject.GetComponent<RectTransform>();
            if (position != default) rectTransform.anchoredPosition = position;
            
            _createdObjects.Add(sliderObject);
            return slider;
        }

        /// <summary>
        /// Simulate a click on a UI element
        /// </summary>
        public void SimulateClick(GameObject target)
        {
            var eventData = new PointerEventData(EventSystem.current)
            {
                position = RectTransformUtility.WorldToScreenPoint(null, target.transform.position)
            };

            ExecuteEvents.Execute(target, eventData, ExecuteEvents.pointerDownHandler);
            ExecuteEvents.Execute(target, eventData, ExecuteEvents.pointerUpHandler);
            ExecuteEvents.Execute(target, eventData, ExecuteEvents.pointerClickHandler);
        }

        /// <summary>
        /// Simulate text input
        /// </summary>
        public void SimulateTextInput(InputField inputField, string text)
        {
            inputField.text = text;
            inputField.onEndEdit.Invoke(text);
        }

        /// <summary>
        /// Simulate toggle interaction
        /// </summary>
        public void SimulateToggle(Toggle toggle)
        {
            toggle.isOn = !toggle.isOn;
            toggle.onValueChanged.Invoke(toggle.isOn);
        }

        /// <summary>
        /// Simulate slider drag
        /// </summary>
        public void SimulateSliderDrag(Slider slider, float value)
        {
            slider.value = value;
            slider.onValueChanged.Invoke(value);
        }

        /// <summary>
        /// Wait for UI animation to complete
        /// </summary>
        public IEnumerator WaitForUIAnimation(float duration = 1f)
        {
            yield return new WaitForSeconds(duration);
        }

        /// <summary>
        /// Assert that UI element is visible
        /// </summary>
        public void AssertUIElementVisible(GameObject element)
        {
            Assert.IsNotNull(element, "UI element should not be null");
            Assert.IsTrue(element.activeInHierarchy, "UI element should be active in hierarchy");
            
            var canvasGroup = element.GetComponent<CanvasGroup>();
            if (canvasGroup != null)
            {
                Assert.IsTrue(canvasGroup.alpha > 0f, "UI element should have alpha > 0");
                Assert.IsTrue(canvasGroup.interactable, "UI element should be interactable");
            }
        }

        /// <summary>
        /// Assert that UI element is hidden
        /// </summary>
        public void AssertUIElementHidden(GameObject element)
        {
            if (element == null) return; // Null is considered hidden
            
            if (!element.activeInHierarchy)
            {
                return; // Inactive is hidden
            }
            
            var canvasGroup = element.GetComponent<CanvasGroup>();
            if (canvasGroup != null)
            {
                Assert.IsTrue(canvasGroup.alpha <= 0f, "Hidden UI element should have alpha <= 0");
            }
        }

        /// <summary>
        /// Get all UI elements of a specific type
        /// </summary>
        public T[] FindUIElements<T>() where T : Component
        {
            return UnityEngine.Object.FindObjectsOfType<T>();
        }

        /// <summary>
        /// Take a screenshot for visual regression testing
        /// </summary>
        public void TakeScreenshot(string testName)
        {
            var filename = $"Screenshots/{testName}_{DateTime.Now:yyyyMMdd_HHmmss}.png";
            ScreenCapture.CaptureScreenshot(filename);
            UnityEngine.Debug.Log($"Screenshot saved: {filename}");
        }

        /// <summary>
        /// Assert UI layout dimensions
        /// </summary>
        public void AssertUILayoutDimensions(RectTransform rectTransform, Vector2 expectedSize, float tolerance = 1f)
        {
            var actualSize = rectTransform.sizeDelta;
            Assert.LessOrEqual(Mathf.Abs(actualSize.x - expectedSize.x), tolerance, 
                $"UI width {actualSize.x} differs from expected {expectedSize.x} by more than {tolerance}");
            Assert.LessOrEqual(Mathf.Abs(actualSize.y - expectedSize.y), tolerance,
                $"UI height {actualSize.y} differs from expected {expectedSize.y} by more than {tolerance}");
        }

        public void Dispose()
        {
            if (!_disposed)
            {
                foreach (var obj in _createdObjects)
                {
                    if (obj != null)
                    {
                        UnityEngine.Object.DestroyImmediate(obj);
                    }
                }
                _createdObjects.Clear();
                _disposed = true;
            }
        }
    }
} 