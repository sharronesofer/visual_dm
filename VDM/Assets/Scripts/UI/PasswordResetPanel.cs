using UnityEngine;
using System;
using System.Collections;

namespace VisualDM.UI
{
    public class PasswordResetPanel : PanelBase
    {
        private GameObject emailField;
        private GameObject submitButton;
        private GameObject errorMsg;
        private float width = 400f;
        private float height = 220f;
        private Color bgColor = new Color(0.16f, 0.16f, 0.22f, 0.98f);

        public override void Initialize(params object[] args)
        {
            try
            {
                // Background
                var sr = gameObject.AddComponent<SpriteRenderer>();
                sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                    .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
                sr.sortingOrder = 120;

                // Email label and field
                var emailLabelObj = new GameObject("EmailLabel");
                emailLabelObj.transform.SetParent(transform);
                emailLabelObj.transform.localPosition = new Vector3(0, 60, 0);
                var emailLabel = emailLabelObj.AddComponent<TMPro.TextMeshPro>();
                emailLabel.text = "Email";
                emailLabel.fontSize = UI.DesignTokens.Typography.Body;
                emailLabel.font = UI.DesignTokens.Typography.SansFont;
                emailLabel.color = UI.DesignTokens.Colors.Neutral900;
                emailLabel.alignment = TMPro.TextAlignmentOptions.Center;

                emailField = new GameObject("EmailField");
                emailField.transform.SetParent(transform);
                emailField.transform.localPosition = new Vector3(0, 30, 0);
                var emailCore = emailField.AddComponent<UI.Components.CoreField>();
                emailCore.Placeholder = "Enter your email";
                emailCore.OnValueChanged = (val) => {
                    // Clear error message when user makes changes
                    if (errorLabel.text.Length > 0) {
                        errorLabel.text = "";
                    }
                };

                // Submit button
                submitButton = new GameObject("SubmitButton");
                submitButton.transform.SetParent(transform);
                submitButton.transform.localPosition = new Vector3(0, -30, 0);
                var btn = submitButton.AddComponent<UI.Components.Button>();
                btn.Label = "Reset Password";
                btn.OnClick = () => {
                    // Implemented password reset logic
                    if (string.IsNullOrEmpty(emailCore.Value))
                    {
                        errorLabel.text = "Please enter your email address.";
                        return;
                    }
                    
                    // Validate email format
                    if (!IsValidEmail(emailCore.Value))
                    {
                        errorLabel.text = "Please enter a valid email address.";
                        return;
                    }
                    
                    // Disable button during request
                    btn.Interactable = false;
                    errorLabel.text = "Sending reset email...";
                    
                    // Request password reset
                    RequestPasswordReset(emailCore.Value).Then(result => {
                        if (result.success)
                        {
                            // Request successful
                            errorLabel.text = "Password reset email sent. Please check your inbox.";
                            errorLabel.color = UI.DesignTokens.Colors.Success;
                            
                            // Disable field after successful request to prevent spam
                            emailCore.Interactable = false;
                            
                            // Close panel after delay
                            StartCloseTimer(5f);
                        }
                        else
                        {
                            // Request failed
                            errorLabel.text = result.errorMessage ?? "Failed to send reset email. Please try again later.";
                            errorLabel.color = UI.DesignTokens.Colors.Error;
                            btn.Interactable = true;
                        }
                    }).Catch(error => {
                        // Handle connection errors
                        errorLabel.text = "Connection error. Please try again later.";
                        errorLabel.color = UI.DesignTokens.Colors.Error;
                        Debug.LogError($"Password reset error: {error}");
                        btn.Interactable = true;
                    });
                };

                // Error message
                errorMsg = new GameObject("ErrorMsg");
                errorMsg.transform.SetParent(transform);
                errorMsg.transform.localPosition = new Vector3(0, -80, 0);
                var errorLabel = errorMsg.AddComponent<TMPro.TextMeshPro>();
                errorLabel.text = "";
                errorLabel.fontSize = UI.DesignTokens.Typography.Caption;
                errorLabel.font = UI.DesignTokens.Typography.SansFont;
                errorLabel.color = UI.DesignTokens.Colors.Neutral400;
                errorLabel.alignment = TMPro.TextAlignmentOptions.Center;
            }
            catch (Exception ex)
            {
                VisualDM.Utilities.ErrorHandlingService.Instance.LogException(ex, "Failed to initialize Password Reset Panel.", "PasswordResetPanel.Initialize");
            }
        }
        
        /// <summary>
        /// Validate email format using a simple regex pattern.
        /// </summary>
        private bool IsValidEmail(string email)
        {
            try
            {
                var regex = new System.Text.RegularExpressions.Regex(
                    @"^[^@\s]+@[^@\s]+\.[^@\s]+$", 
                    System.Text.RegularExpressions.RegexOptions.IgnoreCase
                );
                return regex.IsMatch(email);
            }
            catch
            {
                return false;
            }
        }
        
        /// <summary>
        /// Requests a password reset for the provided email.
        /// </summary>
        /// <param name="email">The email address to send the reset link to</param>
        /// <returns>A Promise with the request result</returns>
        private VisualDM.Utilities.Promise<ResetResult> RequestPasswordReset(string email)
        {
            var promise = new VisualDM.Utilities.Promise<ResetResult>();
            
            // Create password reset request
            var resetRequest = new VisualDM.Networking.PasswordResetRequest
            {
                Email = email,
                ClientInfo = SystemInfo.deviceUniqueIdentifier
            };
            
            // Send request to the server
            VisualDM.Networking.NetworkManager.Instance.SendPasswordResetRequest(resetRequest, response => {
                if (response.Success)
                {
                    // Resolve promise with success result
                    promise.Resolve(new ResetResult { 
                        success = true
                    });
                }
                else
                {
                    // Resolve promise with error result
                    promise.Resolve(new ResetResult { 
                        success = false, 
                        errorMessage = response.ErrorMessage 
                    });
                }
            }, error => {
                // Reject promise with error
                promise.Reject(error);
            });
            
            return promise;
        }
        
        /// <summary>
        /// Start a timer to close the panel after successful password reset request.
        /// </summary>
        private void StartCloseTimer(float seconds)
        {
            // Use a coroutine to close the panel after delay
            StartCoroutine(CloseAfterDelay(seconds));
        }
        
        /// <summary>
        /// Coroutine to close the panel after a delay.
        /// </summary>
        private IEnumerator CloseAfterDelay(float seconds)
        {
            yield return new WaitForSeconds(seconds);
            
            // Hide this panel
            gameObject.SetActive(false);
            
            // Notify the UIManager that we're done
            UIManager.Instance.OnPasswordResetRequestComplete();
        }
        
        /// <summary>
        /// Class representing the result of a password reset request.
        /// </summary>
        private class ResetResult
        {
            public bool success;
            public string errorMessage;
        }

        public override void OnBreakpointChanged(UIManager.Breakpoint breakpoint)
        {
            switch (breakpoint)
            {
                case UIManager.Breakpoint.Mobile:
                    width = 260f; height = 140f;
                    break;
                case UIManager.Breakpoint.Tablet:
                    width = 320f; height = 180f;
                    break;
                case UIManager.Breakpoint.Desktop:
                    width = 400f; height = 220f;
                    break;
                case UIManager.Breakpoint.LargeDesktop:
                    width = 520f; height = 300f;
                    break;
            }
            var sr = GetComponent<SpriteRenderer>();
            if (sr != null)
                sr.sprite = UIManager.Instance.GetType().GetMethod("GenerateRectSprite", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance)
                    .Invoke(UIManager.Instance, new object[] { (int)width, (int)height, bgColor }) as Sprite;
            if (emailField != null) emailField.transform.localPosition = new Vector3(0, height/4, 0);
            if (submitButton != null) submitButton.transform.localPosition = new Vector3(0, -height/8, 0);
            if (errorMsg != null) errorMsg.transform.localPosition = new Vector3(0, -height/3, 0);
        }
    }
} 