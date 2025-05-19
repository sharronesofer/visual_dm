using System.Collections;
using UnityEngine;
using UnityEngine.UI;
using TMPro;
using VisualDM.Core;

namespace VisualDM.UI
{
    /// <summary>
    /// Handles the login UI with CAPTCHA integration
    /// </summary>
    public class LoginUI : MonoBehaviour
    {
        [Header("Core Fields")]
        [SerializeField] private TMP_CoreField usernameField;
        [SerializeField] private TMP_CoreField passwordField;
        [SerializeField] private TMP_CoreField captchaResponseField;

        [Header("Buttons")]
        [SerializeField] private Button loginButton;
        [SerializeField] private Button registerButton;
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
            loginButton.onClick.AddListener(OnLoginClicked);
            registerButton.onClick.AddListener(OnRegisterClicked);
            refreshCaptchaButton.onClick.AddListener(RefreshCaptcha);

            // Configure CAPTCHA type
            CaptchaService.Instance.SetCaptchaType(useImageCaptcha ? "image" : "logic");
            CaptchaService.Instance.SetDifficulty(captchaDifficulty);

            // Set up auth event listeners
            AuthService.Instance.OnLoginComplete += OnLoginComplete;

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
                AuthService.Instance.OnLoginComplete -= OnLoginComplete;
            }
        }

        /// <summary>
        /// Handle login button click
        /// </summary>
        public void OnLoginClicked()
        {
            // Validate input
            string username = usernameField.text.Trim();
            string password = passwordField.text;
            string captchaResponse = captchaResponseField.text.Trim();

            if (string.IsNullOrEmpty(username))
            {
                statusText.text = "Please enter your username or email";
                return;
            }

            if (string.IsNullOrEmpty(password))
            {
                statusText.text = "Please enter your password";
                return;
            }

            if (string.IsNullOrEmpty(captchaResponse))
            {
                statusText.text = "Please complete the CAPTCHA";
                return;
            }

            // Update UI
            SetUIState(false);
            statusText.text = "Logging in...";

            // Attempt login
            StartCoroutine(AuthService.Instance.Login(username, password, captchaResponse));
        }

        /// <summary>
        /// Handle register button click
        /// </summary>
        public void OnRegisterClicked()
        {
            // Switch to registration screen
            // This would be handled by your UI navigation system
            Debug.Log("Switching to registration screen");
        }

        /// <summary>
        /// Handle login completion callback
        /// </summary>
        private void OnLoginComplete(bool success, string message)
        {
            SetUIState(true);

            if (success)
            {
                statusText.text = "Login successful!";
                // Handle successful login (e.g., switch to main menu)
                Debug.Log("Login successful - redirecting to main menu");
            }
            else
            {
                statusText.text = message;
                // Refresh CAPTCHA if login failed
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
            passwordField.interactable = interactive;
            captchaResponseField.interactable = interactive;
            loginButton.interactable = interactive;
            registerButton.interactable = interactive;
            refreshCaptchaButton.interactable = interactive;
            loadingIndicator.SetActive(!interactive);
        }
    }
} 