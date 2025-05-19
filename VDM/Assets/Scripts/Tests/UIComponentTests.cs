using NUnit.Framework;
using UnityEngine;
using VisualDM.UI.Components;
using TMPro;

namespace VisualDM.Tests
{
    [TestFixture]
    public class UIComponentTests
    {
        [Test]
        public void Button_InitializesAndRespondsToStateChanges()
        {
            var go = new GameObject("Button");
            var button = go.AddComponent<Button>();
            button.SetLabel("Test");
            button.SetVariant(Button.Variant.Secondary);
            button.SetState(Button.State.Hover);
            Assert.AreEqual("Test", button.Label);
            Assert.AreEqual(Button.Variant.Secondary, button.ButtonVariant);
            Assert.AreEqual(Button.State.Hover, button.ButtonState);
            Object.DestroyImmediate(go);
        }

        [Test]
        public void Button_OnClick_InvokesAction()
        {
            var go = new GameObject("Button");
            var button = go.AddComponent<Button>();
            bool clicked = false;
            button.OnClick = () => clicked = true;
            button.SetState(Button.State.Default);
            button.OnMouseUp();
            Assert.IsTrue(clicked);
            Object.DestroyImmediate(go);
        }

        [Test]
        public void InputField_HandlesTextInputAndFocus()
        {
            var go = new GameObject("InputField");
            var input = go.AddComponent<InputField>();
            input.SetValue("");
            input.Focus();
            input.SetValue("abc");
            Assert.AreEqual("abc", input.Value);
            input.Blur();
            Assert.IsFalse(input.IsFocused);
            Object.DestroyImmediate(go);
        }

        [Test]
        public void InputField_HandlesPlaceholderAndPassword()
        {
            var go = new GameObject("InputField");
            var input = go.AddComponent<InputField>();
            input.SetPlaceholder("Type here");
            Assert.AreEqual("Type here", input.Placeholder);
            input.IsPassword = true;
            input.SetValue("secret");
            Assert.AreEqual("secret", input.Value);
            Object.DestroyImmediate(go);
        }

        [Test]
        public void Checkbox_TogglesAndInvokesCallback()
        {
            var go = new GameObject("Checkbox");
            var checkbox = go.AddComponent<Checkbox>();
            bool changed = false;
            checkbox.OnValueChanged = (val) => changed = true;
            checkbox.SetChecked(false);
            checkbox.Toggle();
            Assert.IsTrue(checkbox.IsChecked);
            Assert.IsTrue(changed);
            Object.DestroyImmediate(go);
        }

        [Test]
        public void Card_AppliesStyleAndSize()
        {
            var go = new GameObject("Card");
            var card = go.AddComponent<Card>();
            card.SetSize(400, 200);
            card.SetElevation(3);
            card.SetBackground(Color.red);
            Assert.AreEqual(400, card.Width);
            Assert.AreEqual(200, card.Height);
            Assert.AreEqual(3, card.Elevation);
            Object.DestroyImmediate(go);
        }

        [Test]
        public void Icon_SetsIconAndTint()
        {
            var go = new GameObject("Icon");
            var icon = go.AddComponent<Icon>();
            icon.SetIcon("test_icon");
            icon.SetTint(Color.green);
            icon.SetSize(32f);
            Assert.AreEqual("test_icon", icon.IconName);
            Assert.AreEqual(32f, icon.Size);
            Object.DestroyImmediate(go);
        }

        [Test]
        public void RuntimeTextLabel_AppliesTypeAndColor()
        {
            var go = new GameObject("Label");
            var label = go.AddComponent<RuntimeTextLabel>();
            label.SetText("Hello");
            label.SetType(RuntimeTextLabel.TextType.HeadingLarge);
            label.SetColor(Color.blue);
            label.SetAlignment(TextAlignmentOptions.Center);
            Assert.AreEqual("Hello", label.Text);
            Assert.AreEqual(RuntimeTextLabel.TextType.HeadingLarge, label.Type);
            Assert.AreEqual(TextAlignmentOptions.Center, label.Alignment);
            Object.DestroyImmediate(go);
        }
    }
} 