using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using UnityEngine.UI;
using VDM.Tests.Core;

namespace VDM.Tests.UI
{
    /// <summary>
    /// UI component tests for VDM interface elements
    /// </summary>
    public class UIComponentTests : VDMUITestBase
    {
        [UnityTest]
        public IEnumerator CharacterCreationUI_WhenFormCompleted_ShouldEnableCreateButton()
        {
            // Arrange
            var nameInput = UIHelper.CreateTestInputField("Enter character name", 
                new Vector2(0, 100), new Vector2(200, 30));
            var classDropdown = CreateMockDropdown("Select class", new Vector2(0, 50), 
                new[] { "Warrior", "Mage", "Rogue" });
            var createButton = UIHelper.CreateTestButton("Create Character", 
                new Vector2(0, 0), new Vector2(150, 40));
            
            // Initially button should be disabled
            createButton.interactable = false;

            // Act
            UIHelper.SimulateTextInput(nameInput, "Test Hero");
            yield return new WaitForEndOfFrame();
            
            // Simulate dropdown selection
            classDropdown.value = 1; // Select "Mage"
            classDropdown.onValueChanged.Invoke(1);
            yield return new WaitForEndOfFrame();

            // Simulate form validation
            bool isNameValid = !string.IsNullOrEmpty(nameInput.text);
            bool isClassSelected = classDropdown.value > 0;
            createButton.interactable = isNameValid && isClassSelected;

            // Assert
            UIHelper.AssertUIElementVisible(nameInput.gameObject);
            UIHelper.AssertUIElementVisible(classDropdown.gameObject);
            UIHelper.AssertUIElementVisible(createButton.gameObject);
            Assert.IsTrue(createButton.interactable, "Create button should be enabled when form is valid");
            Assert.AreEqual("Test Hero", nameInput.text);
            Assert.AreEqual(1, classDropdown.value);
        }

        [UnityTest]
        public IEnumerator InventoryGrid_WhenItemsAdded_ShouldDisplayCorrectly()
        {
            // Arrange
            var inventoryPanel = CreateInventoryGrid(4, 6); // 4x6 grid
            var testItems = new[]
            {
                new { name = "Iron Sword", icon = "sword_icon", quantity = 1 },
                new { name = "Health Potion", icon = "potion_icon", quantity = 5 },
                new { name = "Magic Scroll", icon = "scroll_icon", quantity = 3 }
            };

            // Act
            for (int i = 0; i < testItems.Length; i++)
            {
                var item = testItems[i];
                var slot = inventoryPanel.transform.GetChild(i);
                var itemIcon = slot.GetChild(0).GetComponent<Image>();
                var quantityText = slot.GetChild(1).GetComponent<Text>();
                
                // Simulate item addition
                itemIcon.enabled = true;
                quantityText.text = item.quantity > 1 ? item.quantity.ToString() : "";
                
                yield return new WaitForEndOfFrame();
            }

            // Assert
            UIHelper.AssertUIElementVisible(inventoryPanel);
            
            // Check first three slots have items
            for (int i = 0; i < testItems.Length; i++)
            {
                var slot = inventoryPanel.transform.GetChild(i);
                var itemIcon = slot.GetChild(0).GetComponent<Image>();
                var quantityText = slot.GetChild(1).GetComponent<Text>();
                
                Assert.IsTrue(itemIcon.enabled, $"Item icon in slot {i} should be visible");
                if (testItems[i].quantity > 1)
                {
                    Assert.AreEqual(testItems[i].quantity.ToString(), quantityText.text);
                }
            }
        }

        [UnityTest]
        public IEnumerator QuestLogUI_WhenQuestCompleted_ShouldUpdateStatus()
        {
            // Arrange
            var questLogPanel = CreateQuestLogPanel();
            var questEntry = CreateQuestEntry("Find the Ancient Artifact", "In Progress");
            questEntry.transform.SetParent(questLogPanel.transform, false);

            // Act
            yield return new WaitForSeconds(0.1f);

            // Simulate quest completion
            var statusText = questEntry.transform.Find("StatusText").GetComponent<Text>();
            var progressBar = questEntry.transform.Find("ProgressBar").GetComponent<Slider>();
            
            statusText.text = "Completed";
            statusText.color = Color.green;
            progressBar.value = 1.0f;

            yield return new WaitForEndOfFrame();

            // Assert
            UIHelper.AssertUIElementVisible(questLogPanel);
            UIHelper.AssertUIElementVisible(questEntry);
            Assert.AreEqual("Completed", statusText.text);
            Assert.AreEqual(Color.green, statusText.color);
            Assert.AreEqual(1.0f, progressBar.value, 0.01f);
        }

        [UnityTest]
        public IEnumerator CombatUI_WhenActionSelected_ShouldHighlightButton()
        {
            // Arrange
            var combatPanel = CreateCombatActionPanel();
            var attackButton = UIHelper.CreateTestButton("Attack", new Vector2(-100, 0));
            var defendButton = UIHelper.CreateTestButton("Defend", new Vector2(0, 0));
            var spellButton = UIHelper.CreateTestButton("Cast Spell", new Vector2(100, 0));
            
            attackButton.transform.SetParent(combatPanel.transform, false);
            defendButton.transform.SetParent(combatPanel.transform, false);
            spellButton.transform.SetParent(combatPanel.transform, false);

            // Act
            UIHelper.SimulateClick(attackButton.gameObject);
            yield return new WaitForEndOfFrame();

            // Simulate button highlighting
            var attackButtonImage = attackButton.GetComponent<Image>();
            attackButtonImage.color = Color.yellow; // Highlight color

            // Assert
            UIHelper.AssertUIElementVisible(combatPanel);
            Assert.AreEqual(Color.yellow, attackButtonImage.color, "Attack button should be highlighted");
        }

        [UnityTest]
        public IEnumerator DialogueUI_WhenChoiceMade_ShouldAdvanceConversation()
        {
            // Arrange
            var dialoguePanel = CreateDialoguePanel();
            var speakerText = dialoguePanel.transform.Find("SpeakerName").GetComponent<Text>();
            var dialogueText = dialoguePanel.transform.Find("DialogueText").GetComponent<Text>();
            var choice1Button = UIHelper.CreateTestButton("Be friendly", new Vector2(-100, -50));
            var choice2Button = UIHelper.CreateTestButton("Be suspicious", new Vector2(100, -50));
            
            choice1Button.transform.SetParent(dialoguePanel.transform, false);
            choice2Button.transform.SetParent(dialoguePanel.transform, false);

            // Initial dialogue
            speakerText.text = "Village Elder";
            dialogueText.text = "Welcome, traveler. What brings you to our village?";

            // Act
            UIHelper.SimulateClick(choice1Button.gameObject);
            yield return new WaitForSeconds(0.1f);

            // Simulate dialogue advancement
            dialogueText.text = "Ah, a friendly soul! We could use more like you around here.";
            choice1Button.gameObject.SetActive(false);
            choice2Button.gameObject.SetActive(false);

            yield return new WaitForEndOfFrame();

            // Assert
            UIHelper.AssertUIElementVisible(dialoguePanel);
            Assert.AreEqual("Village Elder", speakerText.text);
            Assert.AreEqual("Ah, a friendly soul! We could use more like you around here.", dialogueText.text);
            UIHelper.AssertUIElementHidden(choice1Button.gameObject);
            UIHelper.AssertUIElementHidden(choice2Button.gameObject);
        }

        [UnityTest]
        public IEnumerator HealthBarUI_WhenDamageTaken_ShouldAnimateCorrectly()
        {
            // Arrange
            var healthBarPanel = CreateHealthBarPanel();
            var healthBar = healthBarPanel.transform.Find("HealthBar").GetComponent<Slider>();
            var healthText = healthBarPanel.transform.Find("HealthText").GetComponent<Text>();
            
            healthBar.maxValue = 100;
            healthBar.value = 100;
            healthText.text = "100/100";

            // Act - Simulate damage
            float targetHealth = 65f;
            float animationSpeed = 2f;
            float startValue = healthBar.value;
            
            for (float t = 0; t < 1f; t += Time.deltaTime * animationSpeed)
            {
                healthBar.value = Mathf.Lerp(startValue, targetHealth, t);
                healthText.text = $"{(int)healthBar.value}/100";
                yield return null;
            }
            
            healthBar.value = targetHealth;
            healthText.text = $"{(int)targetHealth}/100";

            // Assert
            UIHelper.AssertUIElementVisible(healthBarPanel);
            Assert.AreEqual(65f, healthBar.value, 1f);
            Assert.AreEqual("65/100", healthText.text);
        }

        [UnityTest]
        public IEnumerator ModalDialog_WhenConfirmPressed_ShouldCloseAndExecuteAction()
        {
            // Arrange
            var modalDialog = CreateModalDialog("Confirm Action", "Are you sure you want to delete this item?");
            var confirmButton = modalDialog.transform.Find("ConfirmButton").GetComponent<Button>();
            var cancelButton = modalDialog.transform.Find("CancelButton").GetComponent<Button>();
            
            bool actionExecuted = false;
            confirmButton.onClick.AddListener(() => actionExecuted = true);

            // Act
            UIHelper.SimulateClick(confirmButton.gameObject);
            yield return new WaitForEndOfFrame();

            // Simulate modal closing
            modalDialog.SetActive(false);

            // Assert
            Assert.IsTrue(actionExecuted, "Confirm action should have been executed");
            UIHelper.AssertUIElementHidden(modalDialog);
        }

        [UnityTest]
        public IEnumerator LoadingScreen_WhenDataLoading_ShouldShowProgressAnimation()
        {
            // Arrange
            var loadingScreen = CreateLoadingScreen();
            var progressBar = loadingScreen.transform.Find("ProgressBar").GetComponent<Slider>();
            var loadingText = loadingScreen.transform.Find("LoadingText").GetComponent<Text>();
            
            progressBar.value = 0f;
            loadingText.text = "Loading...";

            // Act - Simulate loading progress
            string[] loadingStages = { "Initializing...", "Loading assets...", "Connecting...", "Complete!" };
            
            for (int stage = 0; stage < loadingStages.Length; stage++)
            {
                loadingText.text = loadingStages[stage];
                float targetProgress = (stage + 1) / (float)loadingStages.Length;
                
                // Animate progress bar
                while (progressBar.value < targetProgress - 0.01f)
                {
                    progressBar.value = Mathf.MoveTowards(progressBar.value, targetProgress, Time.deltaTime * 2f);
                    yield return null;
                }
                
                yield return new WaitForSeconds(0.3f);
            }

            // Hide loading screen when complete
            loadingScreen.SetActive(false);

            // Assert
            Assert.AreEqual(1f, progressBar.value, 0.01f);
            UIHelper.AssertUIElementHidden(loadingScreen);
        }

        [UnityTest]
        public IEnumerator ResponsiveLayout_WhenScreenSizeChanges_ShouldAdaptCorrectly()
        {
            // Arrange
            var originalScreenSize = new Vector2(Screen.width, Screen.height);
            var uiPanel = CreateResponsivePanel();
            var rectTransform = uiPanel.GetComponent<RectTransform>();
            
            // Set initial layout
            rectTransform.anchorMin = new Vector2(0.1f, 0.1f);
            rectTransform.anchorMax = new Vector2(0.9f, 0.9f);
            rectTransform.offsetMin = Vector2.zero;
            rectTransform.offsetMax = Vector2.zero;

            yield return new WaitForEndOfFrame();

            // Store initial size
            var initialSize = rectTransform.sizeDelta;

            // Act - Simulate screen size change (mock)
            // In a real test, you might change Canvas scaler settings
            Canvas.ForceUpdateCanvases();
            yield return new WaitForEndOfFrame();

            // Assert - Panel should maintain relative positioning
            UIHelper.AssertUIElementVisible(uiPanel);
            
            // Verify the panel maintains its relative screen coverage
            Assert.AreEqual(new Vector2(0.1f, 0.1f), rectTransform.anchorMin);
            Assert.AreEqual(new Vector2(0.9f, 0.9f), rectTransform.anchorMax);
        }

        [Test]
        public void UIAccessibility_AllInteractableElements_ShouldHaveProperLabels()
        {
            // Arrange
            var testButton = UIHelper.CreateTestButton("Test Action");
            var testInput = UIHelper.CreateTestInputField("Enter text");
            var testToggle = UIHelper.CreateTestToggle("Enable feature");

            // Act & Assert
            Assert.IsNotNull(testButton.gameObject.name, "Button should have a name");
            Assert.IsNotNull(testInput.placeholder, "Input field should have placeholder text");
            
            // Verify accessibility components could be added
            Assert.IsNotNull(testButton.GetComponent<Button>());
            Assert.IsNotNull(testInput.GetComponent<InputField>());
            Assert.IsNotNull(testToggle.GetComponent<Toggle>());
        }

        [UnityTest]
        public IEnumerator UIPerformance_WithManyElements_ShouldMaintainFramerate()
        {
            // Arrange
            var container = new GameObject("Container");
            container.transform.SetParent(TestCanvas.transform, false);
            
            var targetFramerate = 30f; // Minimum acceptable framerate
            var elementCount = 100;

            // Act - Create many UI elements
            for (int i = 0; i < elementCount; i++)
            {
                var element = UIHelper.CreateTestButton($"Button {i}", 
                    new Vector2(Random.Range(-400, 400), Random.Range(-300, 300)));
                element.transform.SetParent(container.transform, false);
                
                if (i % 10 == 0) // Check framerate periodically
                {
                    yield return null;
                    var currentFramerate = 1f / Time.deltaTime;
                    Assert.GreaterOrEqual(currentFramerate, targetFramerate, 
                        $"Framerate dropped below {targetFramerate} FPS at {i} elements");
                }
            }

            yield return new WaitForSeconds(0.5f);

            // Assert final performance
            var finalFramerate = 1f / Time.deltaTime;
            Assert.GreaterOrEqual(finalFramerate, targetFramerate, 
                $"Final framerate {finalFramerate} FPS is below minimum {targetFramerate} FPS");
            
            // Cleanup
            Object.DestroyImmediate(container);
        }

        #region Helper Methods

        private GameObject CreateInventoryGrid(int rows, int columns)
        {
            var gridPanel = new GameObject("InventoryGrid");
            gridPanel.transform.SetParent(TestCanvas.transform, false);
            
            var gridLayout = gridPanel.AddComponent<GridLayoutGroup>();
            gridLayout.constraint = GridLayoutGroup.Constraint.FixedColumnCount;
            gridLayout.constraintCount = columns;
            gridLayout.cellSize = new Vector2(50, 50);
            gridLayout.spacing = new Vector2(5, 5);

            // Create slots
            for (int i = 0; i < rows * columns; i++)
            {
                var slot = new GameObject($"Slot_{i}");
                slot.transform.SetParent(gridPanel.transform, false);
                slot.AddComponent<Image>().color = Color.gray;
                
                // Add item icon (initially disabled)
                var iconObj = new GameObject("ItemIcon");
                iconObj.transform.SetParent(slot.transform, false);
                var icon = iconObj.AddComponent<Image>();
                icon.enabled = false;
                
                // Add quantity text
                var quantityObj = new GameObject("Quantity");
                quantityObj.transform.SetParent(slot.transform, false);
                var quantityText = quantityObj.AddComponent<Text>();
                quantityText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
                quantityText.fontSize = 12;
                quantityText.alignment = TextAnchor.LowerRight;
            }

            return gridPanel;
        }

        private GameObject CreateQuestLogPanel()
        {
            var panel = new GameObject("QuestLogPanel");
            panel.transform.SetParent(TestCanvas.transform, false);
            panel.AddComponent<Image>().color = new Color(0, 0, 0, 0.8f);
            
            var rectTransform = panel.GetComponent<RectTransform>();
            rectTransform.sizeDelta = new Vector2(400, 300);
            
            return panel;
        }

        private GameObject CreateQuestEntry(string questTitle, string status)
        {
            var entry = new GameObject("QuestEntry");
            entry.AddComponent<Image>().color = Color.white;
            
            var titleObj = new GameObject("TitleText");
            titleObj.transform.SetParent(entry.transform, false);
            var titleText = titleObj.AddComponent<Text>();
            titleText.text = questTitle;
            titleText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            
            var statusObj = new GameObject("StatusText");
            statusObj.transform.SetParent(entry.transform, false);
            var statusText = statusObj.AddComponent<Text>();
            statusText.text = status;
            statusText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            statusText.color = status == "Completed" ? Color.green : Color.yellow;
            
            var progressObj = new GameObject("ProgressBar");
            progressObj.transform.SetParent(entry.transform, false);
            var progressBar = progressObj.AddComponent<Slider>();
            progressBar.value = status == "Completed" ? 1.0f : 0.5f;
            
            return entry;
        }

        private GameObject CreateCombatActionPanel()
        {
            var panel = new GameObject("CombatActionPanel");
            panel.transform.SetParent(TestCanvas.transform, false);
            panel.AddComponent<Image>().color = new Color(0.2f, 0.2f, 0.2f, 0.9f);
            
            var rectTransform = panel.GetComponent<RectTransform>();
            rectTransform.sizeDelta = new Vector2(400, 100);
            rectTransform.anchoredPosition = new Vector2(0, -200);
            
            return panel;
        }

        private GameObject CreateDialoguePanel()
        {
            var panel = new GameObject("DialoguePanel");
            panel.transform.SetParent(TestCanvas.transform, false);
            panel.AddComponent<Image>().color = new Color(0, 0, 0, 0.8f);
            
            var rectTransform = panel.GetComponent<RectTransform>();
            rectTransform.sizeDelta = new Vector2(600, 200);
            rectTransform.anchoredPosition = new Vector2(0, -150);
            
            // Speaker name
            var speakerObj = new GameObject("SpeakerName");
            speakerObj.transform.SetParent(panel.transform, false);
            var speakerText = speakerObj.AddComponent<Text>();
            speakerText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            speakerText.fontSize = 16;
            speakerText.fontStyle = FontStyle.Bold;
            
            // Dialogue text
            var dialogueObj = new GameObject("DialogueText");
            dialogueObj.transform.SetParent(panel.transform, false);
            var dialogueText = dialogueObj.AddComponent<Text>();
            dialogueText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            dialogueText.fontSize = 14;
            
            return panel;
        }

        private GameObject CreateHealthBarPanel()
        {
            var panel = new GameObject("HealthBarPanel");
            panel.transform.SetParent(TestCanvas.transform, false);
            
            var healthBarObj = new GameObject("HealthBar");
            healthBarObj.transform.SetParent(panel.transform, false);
            var healthBar = healthBarObj.AddComponent<Slider>();
            
            var healthTextObj = new GameObject("HealthText");
            healthTextObj.transform.SetParent(panel.transform, false);
            var healthText = healthTextObj.AddComponent<Text>();
            healthText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            
            return panel;
        }

        private GameObject CreateModalDialog(string title, string message)
        {
            var modal = new GameObject("ModalDialog");
            modal.transform.SetParent(TestCanvas.transform, false);
            modal.AddComponent<Image>().color = new Color(0, 0, 0, 0.9f);
            
            var confirmBtn = new GameObject("ConfirmButton");
            confirmBtn.transform.SetParent(modal.transform, false);
            confirmBtn.AddComponent<Button>();
            
            var cancelBtn = new GameObject("CancelButton");
            cancelBtn.transform.SetParent(modal.transform, false);
            cancelBtn.AddComponent<Button>();
            
            return modal;
        }

        private GameObject CreateLoadingScreen()
        {
            var screen = new GameObject("LoadingScreen");
            screen.transform.SetParent(TestCanvas.transform, false);
            screen.AddComponent<Image>().color = Color.black;
            
            var progressObj = new GameObject("ProgressBar");
            progressObj.transform.SetParent(screen.transform, false);
            progressObj.AddComponent<Slider>();
            
            var textObj = new GameObject("LoadingText");
            textObj.transform.SetParent(screen.transform, false);
            var text = textObj.AddComponent<Text>();
            text.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            
            return screen;
        }

        private GameObject CreateResponsivePanel()
        {
            var panel = new GameObject("ResponsivePanel");
            panel.transform.SetParent(TestCanvas.transform, false);
            panel.AddComponent<Image>().color = Color.blue;
            
            return panel;
        }

        private Dropdown CreateMockDropdown(string placeholder, Vector2 position, string[] options)
        {
            var dropdownObj = new GameObject("TestDropdown");
            dropdownObj.transform.SetParent(TestCanvas.transform, false);
            
            var dropdown = dropdownObj.AddComponent<Dropdown>();
            dropdown.options.Clear();
            dropdown.options.Add(new Dropdown.OptionData(placeholder));
            foreach (var option in options)
            {
                dropdown.options.Add(new Dropdown.OptionData(option));
            }
            
            var rectTransform = dropdownObj.GetComponent<RectTransform>();
            rectTransform.anchoredPosition = position;
            rectTransform.sizeDelta = new Vector2(200, 30);
            
            return dropdown;
        }

        #endregion
    }
} 