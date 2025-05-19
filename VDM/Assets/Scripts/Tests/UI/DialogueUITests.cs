using System.Collections;
using System.Collections.Generic;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;
using VDM.UI;
using VDM.Core;
using VDM.Core.Models;
using VDM.Systems.Dialogue;
using UnityEngine.UI;
using TMPro;

namespace VDM.Tests.UI
{
    /// <summary>
    /// Test suite for the DialogueUI component, which handles the display of
    /// NPC conversations and dialogue choices to the player.
    /// </summary>
    public class DialogueUITests : TestFramework
    {
        // Test dependencies
        private DialogueUI _dialogueUI;
        private DialogueSystem _dialogueSystem;
        private GameState _gameState;
        
        // UI Elements
        private GameObject _dialoguePanel;
        private TextMeshProUGUI _speakerNameText;
        private TextMeshProUGUI _dialogueText;
        private GameObject _choicesContainer;
        private List<Button> _choiceButtons;
        
        // Test data
        private DialogueNode _testDialogue;
        private List<DialogueChoice> _testChoices;
        
        [SetUp]
        public override void Setup()
        {
            base.Setup();
            
            // Create the GameState
            _gameState = new GameState();
            
            // Create the DialogueSystem
            GameObject dialogueSystemObj = CreateTestObject("DialogueSystem", typeof(DialogueSystem));
            _dialogueSystem = dialogueSystemObj.GetComponent<DialogueSystem>();
            _dialogueSystem.Initialize(_gameState);
            
            // Create the DialogueUI
            GameObject dialogueUIObj = CreateTestObject("DialogueUI", typeof(DialogueUI));
            _dialogueUI = dialogueUIObj.GetComponent<DialogueUI>();
            
            // Set up UI components
            _dialoguePanel = CreateUIPanel();
            _speakerNameText = CreateTextComponent("SpeakerNameText", _dialoguePanel.transform);
            _dialogueText = CreateTextComponent("DialogueText", _dialoguePanel.transform);
            _choicesContainer = CreateUIPanel("ChoicesContainer", _dialoguePanel.transform);
            
            // Configure DialogueUI with our test components
            _dialogueUI.DialoguePanel = _dialoguePanel;
            _dialogueUI.SpeakerNameText = _speakerNameText;
            _dialogueUI.DialogueText = _dialogueText;
            _dialogueUI.ChoicesContainer = _choicesContainer;
            _dialogueUI.Initialize(_dialogueSystem);
            
            // Create test data
            CreateTestDialogue();
        }
        
        private GameObject CreateUIPanel(string name = "DialoguePanel", Transform parent = null)
        {
            GameObject panel = CreateTestObject(name, typeof(RectTransform), typeof(CanvasRenderer), typeof(Image));
            if (parent != null)
            {
                panel.transform.SetParent(parent, false);
            }
            return panel;
        }
        
        private TextMeshProUGUI CreateTextComponent(string name, Transform parent)
        {
            GameObject textObj = CreateTestObject(name, typeof(RectTransform), typeof(TextMeshProUGUI));
            textObj.transform.SetParent(parent, false);
            return textObj.GetComponent<TextMeshProUGUI>();
        }
        
        private Button CreateChoiceButton(string text, Transform parent)
        {
            GameObject buttonObj = CreateTestObject("ChoiceButton", typeof(RectTransform), typeof(Button), typeof(Image));
            buttonObj.transform.SetParent(parent, false);
            
            GameObject textObj = CreateTestObject("Text", typeof(RectTransform), typeof(TextMeshProUGUI));
            textObj.transform.SetParent(buttonObj.transform, false);
            
            TextMeshProUGUI tmpText = textObj.GetComponent<TextMeshProUGUI>();
            tmpText.text = text;
            
            return buttonObj.GetComponent<Button>();
        }
        
        private void CreateTestDialogue()
        {
            _testChoices = new List<DialogueChoice>
            {
                new DialogueChoice { 
                    Id = "choice1", 
                    Text = "Tell me more about the town.", 
                    NextNodeId = "town_info" 
                },
                new DialogueChoice { 
                    Id = "choice2", 
                    Text = "I need to go.", 
                    NextNodeId = "goodbye" 
                }
            };
            
            _testDialogue = new DialogueNode
            {
                Id = "greeting",
                SpeakerId = "villager",
                SpeakerName = "Village Elder",
                Text = "Greetings, traveler! Welcome to our humble village.",
                Choices = _testChoices
            };
        }
        
        [Test]
        public void DialogueUI_Initialization_ShouldInitializeProperly()
        {
            // Assert
            Assert.IsNotNull(_dialogueUI);
            Assert.IsFalse(_dialoguePanel.activeSelf, "Dialogue panel should be hidden initially");
        }
        
        [UnityTest]
        public IEnumerator ShowDialogue_ShouldDisplayDialogueAndChoices()
        {
            // Act
            _dialogueUI.ShowDialogue(_testDialogue);
            
            // Wait a frame for UI to update
            yield return null;
            
            // Assert
            Assert.IsTrue(_dialoguePanel.activeSelf, "Dialogue panel should be visible");
            Assert.AreEqual(_testDialogue.SpeakerName, _speakerNameText.text, "Speaker name should be set correctly");
            Assert.AreEqual(_testDialogue.Text, _dialogueText.text, "Dialogue text should be set correctly");
            
            // Check that choices were created
            Assert.AreEqual(_testChoices.Count, _choicesContainer.transform.childCount, "Choice buttons should be created");
        }
        
        [UnityTest]
        public IEnumerator HideDialogue_ShouldCloseDialoguePanel()
        {
            // Arrange
            _dialogueUI.ShowDialogue(_testDialogue);
            yield return null;
            Assert.IsTrue(_dialoguePanel.activeSelf, "Dialogue panel should be visible initially");
            
            // Act
            _dialogueUI.HideDialogue();
            yield return null;
            
            // Assert
            Assert.IsFalse(_dialoguePanel.activeSelf, "Dialogue panel should be hidden");
        }
        
        [UnityTest]
        public IEnumerator SelectChoice_ShouldTriggerChoiceEvent()
        {
            // Arrange
            bool choiceSelected = false;
            string selectedChoiceId = "";
            
            _dialogueUI.OnChoiceSelected += (choiceId) => {
                choiceSelected = true;
                selectedChoiceId = choiceId;
            };
            
            _dialogueUI.ShowDialogue(_testDialogue);
            yield return null;
            
            // Simulate selecting the first choice
            // We need to get the button that was dynamically created
            if (_choicesContainer.transform.childCount > 0)
            {
                Button firstChoiceButton = _choicesContainer.transform.GetChild(0).GetComponent<Button>();
                
                // Act - simulate button click
                firstChoiceButton.onClick.Invoke();
                yield return null;
                
                // Assert
                Assert.IsTrue(choiceSelected, "Choice selection event should have been triggered");
                Assert.AreEqual(_testChoices[0].Id, selectedChoiceId, "Correct choice ID should be passed");
            }
            else
            {
                Assert.Fail("No choice buttons were created");
            }
        }
        
        [UnityTest]
        public IEnumerator ShowDialogueWithNoChoices_ShouldDisplayContinueButton()
        {
            // Arrange
            DialogueNode dialogueWithoutChoices = new DialogueNode
            {
                Id = "info",
                SpeakerId = "villager",
                SpeakerName = "Village Elder",
                Text = "This is just information with no choices.",
                Choices = new List<DialogueChoice>()
            };
            
            // Act
            _dialogueUI.ShowDialogue(dialogueWithoutChoices);
            yield return null;
            
            // Assert
            Assert.IsTrue(_dialoguePanel.activeSelf, "Dialogue panel should be visible");
            Assert.AreEqual(1, _choicesContainer.transform.childCount, "A single continue button should be created");
            
            // Check that the button is labeled correctly
            TextMeshProUGUI buttonText = _choicesContainer.transform.GetChild(0)
                .GetComponentInChildren<TextMeshProUGUI>();
            
            Assert.IsNotNull(buttonText, "Button should have text component");
            Assert.AreEqual("Continue", buttonText.text, "Button should show 'Continue'");
        }
        
        [Test]
        public void ShowDialogue_WithNullNode_ShouldHandleGracefully()
        {
            // Act & Assert - should not throw exceptions
            Assert.DoesNotThrow(() => _dialogueUI.ShowDialogue(null));
        }
        
        [UnityTest]
        public IEnumerator TypewriterEffect_ShouldRevealTextGradually()
        {
            // Assuming the DialogueUI has a typewriter effect
            
            // Arrange
            _dialogueUI.TypewriterSpeed = 0.01f; // Set fast typewriter for testing
            string longText = "This is a long text that should be displayed gradually.";
            DialogueNode nodeWithLongText = new DialogueNode
            {
                Id = "long_text",
                SpeakerId = "villager",
                SpeakerName = "Storyteller",
                Text = longText,
                Choices = new List<DialogueChoice>()
            };
            
            // Act
            _dialogueUI.ShowDialogue(nodeWithLongText);
            
            // Check text immediately after showing
            Assert.AreNotEqual(longText, _dialogueText.text, "Text should not be fully displayed immediately");
            
            // Wait for typewriter to complete
            yield return new WaitForSeconds(longText.Length * 0.01f + 0.1f);
            
            // Assert
            Assert.AreEqual(longText, _dialogueText.text, "Full text should be displayed after typewriter effect");
        }
        
        [UnityTest]
        public IEnumerator DialogueChoiceWithCondition_ShouldShowOnlyValidChoices()
        {
            // Arrange
            _testChoices[0].Condition = "PlayerHasItem('key')";
            
            // Set up game state - player doesn't have the key
            _gameState.PlayerInventory = new Inventory();
            
            // Act
            _dialogueUI.ShowDialogue(_testDialogue);
            yield return null;
            
            // Assert
            Assert.AreEqual(1, _choicesContainer.transform.childCount, "Only choices with valid conditions should be shown");
            
            // Get the text of the shown choice
            TextMeshProUGUI buttonText = _choicesContainer.transform.GetChild(0)
                .GetComponentInChildren<TextMeshProUGUI>();
            
            Assert.AreEqual(_testChoices[1].Text, buttonText.text, "The choice without condition should be shown");
        }
    }
} 