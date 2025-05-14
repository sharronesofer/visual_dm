using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VisualDM.Backend;

namespace VisualDM.UI
{
    /// <summary>
    /// Handles the registration UI with CAPTCHA integration
    /// </summary>
    public class RegisterUI : MonoBehaviour
    {
        [Header("Input Fields")]
        [SerializeField] private TMP_InputField usernameField;
        [SerializeField] private TMP_InputField emailField;
        [SerializeField] private TMP_InputField passwordField;
        [SerializeField] private TMP_InputField confirmPasswordField;
        [SerializeField] private TMP_InputField firstNameField;
        [SerializeField] private TMP_InputField lastNameField;
        [SerializeField] private TMP_InputField captchaResponseField;

        [Header("Buttons")]
        [SerializeField] private Button registerButton;
        [SerializeField] private Button backToLoginButton;
        [SerializeField] private Button refreshCaptchaButton;

        [Header("CAPTCHA Display")]
        [SerializeField] private RawImage captchaImage;
        [SerializeField] private TextMeshProUGUI captchaQuestion;
        [SerializeField] private GameObject imageCaptchaContainer;
        [SerializeField] private GameObject logicCaptchaContainer;

        [Header("Status")]
        [SerializeField] private TextMeshProUGUI statusText;
        [SerializeField] private GameObject loadingIndicator;

        [Header("Options")]
        [SerializeField] private bool useImageCaptcha = true;
        [SerializeField] private string captchaDifficulty = "medium";

        private void Start()
        {
            // Set up button listeners
            registerButton.onClick.AddListener(OnRegisterClicked);
            backToLoginButton.onClick.AddListener(OnBackToLoginClicked);
            refreshCaptchaButton.onClick.AddListener(RefreshCaptcha);

            // Configure CAPTCHA type
            CaptchaService.Instance.SetCaptchaType(useImageCaptcha ? "image" : "logic");
            CaptchaService.Instance.SetDifficulty(captchaDifficulty);

            // Set up auth event listeners
            AuthService.Instance.OnRegistrationComplete += OnRegistrationComplete;

            // Set initial UI state
            SetUIState(true);
            statusText.text = "";

            // Get initial CAPTCHA
            RefreshCaptcha();
        }

        private void OnDestroy()
        {
            // Clean up auth event listeners
            if (AuthService.Instance != null)
            {
                AuthService.Instance.OnRegistrationComplete -= OnRegistrationComplete;
            }
        }

        /// <summary>
        /// Handle register button click
        /// </summary>
        public void OnRegisterClicked()
        {
            // Validate input
            string username = usernameField.text.Trim();
            string email = emailField.text.Trim();
            string password = passwordField.text;
            string confirmPassword = confirmPasswordField.text;
            string firstName = firstNameField.text.Trim();
            string lastName = lastNameField.text.Trim();
            string captchaResponse = captchaResponseField.text.Trim();

            // Basic validation
            if (string.IsNullOrEmpty(username))
            {
                statusText.text = "Please enter a username";
                return;
            }

            if (string.IsNullOrEmpty(email))
            {
                statusText.text = "Please enter an email address";
                return;
            }

            if (!IsValidEmail(email))
            {
                statusText.text = "Please enter a valid email address";
                return;
            }

            if (string.IsNullOrEmpty(password))
            {
                statusText.text = "Please enter a password";
                return;
            }

            if (password.Length < 8)
            {
                statusText.text = "Password must be at least 8 characters";
                return;
            }

            if (password != confirmPassword)
            {
                statusText.text = "Passwords do not match";
                return;
            }

            if (string.IsNullOrEmpty(captchaResponse))
            {
                statusText.text = "Please complete the CAPTCHA";
                return;
            }

            // Update UI
            SetUIState(false);
            statusText.text = "Registering...";

            // Attempt registration
            StartCoroutine(AuthService.Instance.Register(
                username, email, password, firstName, lastName, captchaResponse));
        }

        /// <summary>
        /// Handle back to login button click
        /// </summary>
        public void OnBackToLoginClicked()
        {
            // Switch to login screen
            // This would be handled by your UI navigation system
            Debug.Log("Switching to login screen");
        }

        /// <summary>
        /// Handle registration completion callback
        /// </summary>
        private void OnRegistrationComplete(bool success, string message)
        {
            SetUIState(true);

            if (success)
            {
                statusText.text = "Registration successful!";
                // Handle successful registration (e.g., switch to main menu or login screen)
                Debug.Log("Registration successful - redirecting");
            }
            else
            {
                statusText.text = message;
                // Refresh CAPTCHA if registration failed
                RefreshCaptcha();
            }
        }

        /// <summary>
        /// Refreshes the CAPTCHA display
        /// </summary>
        public void RefreshCaptcha()
        {
            SetUIState(false);
            statusText.text = "Loading CAPTCHA...";
            captchaResponseField.text = "";

            StartCoroutine(GetNewCaptcha());
        }

        /// <summary>
        /// Gets a new CAPTCHA challenge from the server
        /// </summary>
        private IEnumerator GetNewCaptcha()
        {
            yield return StartCoroutine(CaptchaService.Instance.GetCaptcha(OnCaptchaLoaded));
        }

        /// <summary>
        /// Handle CAPTCHA loading completion
        /// </summary>
        private void OnCaptchaLoaded(bool success, string errorMessage)
        {
            SetUIState(true);

            if (success)
            {
                statusText.text = "";
                UpdateCaptchaUI();
            }
            else
            {
                statusText.text = errorMessage ?? "Failed to load CAPTCHA";
            }
        }

        /// <summary>
        /// Updates the CAPTCHA UI based on the loaded CAPTCHA type
        /// </summary>
        private void UpdateCaptchaUI()
        {
            // Get CAPTCHA data
            Texture2D imageTexture = CaptchaService.Instance.GetCaptchaImage();
            string logicQuestion = CaptchaService.Instance.GetLogicQuestion();

            if (imageTexture != null)
            {
                // Image CAPTCHA
                imageCaptchaContainer.SetActive(true);
                logicCaptchaContainer.SetActive(false);
                captchaImage.texture = imageTexture;
                captchaImage.color = Color.white;
            }
            else if (!string.IsNullOrEmpty(logicQuestion))
            {
                // Logic CAPTCHA
                imageCaptchaContainer.SetActive(false);
                logicCaptchaContainer.SetActive(true);
                captchaQuestion.text = logicQuestion;
            }
            else
            {
                // No valid CAPTCHA data
                imageCaptchaContainer.SetActive(false);
                logicCaptchaContainer.SetActive(false);
                statusText.text = "Failed to load CAPTCHA data";
            }
        }

        /// <summary>
        /// Sets the UI interactive state
        /// </summary>
        private void SetUIState(bool interactive)
        {
            usernameField.interactable = interactive;
            emailField.interactable = interactive;
            passwordField.interactable = interactive;
            confirmPasswordField.interactable = interactive;
            firstNameField.interactable = interactive;
            lastNameField.interactable = interactive;
            captchaResponseField.interactable = interactive;
            registerButton.interactable = interactive;
            backToLoginButton.interactable = interactive;
            refreshCaptchaButton.interactable = interactive;
            loadingIndicator.SetActive(!interactive);
        }

        /// <summary>
        /// Simple email validation
        /// </summary>
        private bool IsValidEmail(string email)
        {
            // Basic regex for email validation
            var valid = !string.IsNullOrEmpty(email) &&
                        System.Text.RegularExpressions.Regex.IsMatch(email, 
                        @"^[^@\s]+@[^@\s]+\.[^@\s]+$");
            return valid;
        }
    }
} 