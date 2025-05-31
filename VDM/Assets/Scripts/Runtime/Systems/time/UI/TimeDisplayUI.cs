using UnityEngine;
using TMPro;
using VDM.Systems.Time.Integration;
using VDM.Systems.Time.Models;
using UnityEngine.UI;

namespace VDM.Systems.Time.Ui
{
    /// <summary>
    /// UI component for displaying game time information.
    /// </summary>
    public class TimeDisplayUI : MonoBehaviour
    {
        [Header("UI References")]
        [SerializeField] private TextMeshProUGUI _timeText;
        [SerializeField] private TextMeshProUGUI _dateText;
        [SerializeField] private TextMeshProUGUI _seasonText;
        [SerializeField] private Image _seasonIcon;
        [SerializeField] private Slider _timeScaleSlider;
        [SerializeField] private Button _pauseButton;
        [SerializeField] private Button _resumeButton;

        [Header("Display Settings")]
        [SerializeField] private bool _showSeconds = true;
        [SerializeField] private bool _show24HourFormat = true;
        [SerializeField] private string _timeFormat = "HH:mm:ss";
        [SerializeField] private string _dateFormat = "Year {0}, Month {1}, Day {2}";

        [Header("Season Icons")]
        [SerializeField] private Sprite _springIcon;
        [SerializeField] private Sprite _summerIcon;
        [SerializeField] private Sprite _autumnIcon;
        [SerializeField] private Sprite _winterIcon;

        [Header("Colors")]
        [SerializeField] private Color _springColor = Color.green;
        [SerializeField] private Color _summerColor = Color.yellow;
        [SerializeField] private Color _autumnColor = Color.red;
        [SerializeField] private Color _winterColor = Color.cyan;

        private bool _isInitialized;

        private void Start()
        {
            InitializeUI();
        }

        private void InitializeUI()
        {
            // Subscribe to time events
            if (TimeManager.Instance != null)
            {
                TimeManager.OnTimeAdvanced += OnTimeAdvanced;
                TimeManager.OnPauseStateChanged += OnPauseStateChanged;
                TimeManager.OnTimeScaleChanged += OnTimeScaleChanged;
                TimeManager.OnSeasonChanged += OnSeasonChanged;
            }

            // Setup UI controls
            if (_timeScaleSlider != null)
            {
                _timeScaleSlider.minValue = 0f;
                _timeScaleSlider.maxValue = 10f;
                _timeScaleSlider.value = TimeManager.TimeScale;
                _timeScaleSlider.onValueChanged.AddListener(OnTimeScaleSliderChanged);
            }

            if (_pauseButton != null)
            {
                _pauseButton.onClick.AddListener(OnPauseClicked);
            }

            if (_resumeButton != null)
            {
                _resumeButton.onClick.AddListener(OnResumeClicked);
            }

            // Initial update
            UpdateDisplay();
            UpdatePauseButtons();

            _isInitialized = true;
        }

        private void OnDestroy()
        {
            // Unsubscribe from events
            if (TimeManager.Instance != null)
            {
                TimeManager.OnTimeAdvanced -= OnTimeAdvanced;
                TimeManager.OnPauseStateChanged -= OnPauseStateChanged;
                TimeManager.OnTimeScaleChanged -= OnTimeScaleChanged;
                TimeManager.OnSeasonChanged -= OnSeasonChanged;
            }

            // Remove UI listeners
            if (_timeScaleSlider != null)
            {
                _timeScaleSlider.onValueChanged.RemoveListener(OnTimeScaleSliderChanged);
            }

            if (_pauseButton != null)
            {
                _pauseButton.onClick.RemoveListener(OnPauseClicked);
            }

            if (_resumeButton != null)
            {
                _resumeButton.onClick.RemoveListener(OnResumeClicked);
            }
        }

        private void OnTimeAdvanced(GameTime gameTime)
        {
            UpdateDisplay();
        }

        private void OnPauseStateChanged(bool isPaused)
        {
            UpdatePauseButtons();
        }

        private void OnTimeScaleChanged(float timeScale)
        {
            if (_timeScaleSlider != null && !Mathf.Approximately(_timeScaleSlider.value, timeScale))
            {
                _timeScaleSlider.value = timeScale;
            }
        }

        private void OnSeasonChanged(Season season)
        {
            UpdateSeasonDisplay(season);
        }

        private void OnTimeScaleSliderChanged(float value)
        {
            TimeManager.TimeScale = value;
        }

        private void OnPauseClicked()
        {
            TimeManager.Pause();
        }

        private void OnResumeClicked()
        {
            TimeManager.Resume();
        }

        private void UpdateDisplay()
        {
            var currentTime = TimeManager.CurrentTime;
            if (currentTime == null) return;

            // Update time text
            if (_timeText != null)
            {
                if (_showSeconds)
                {
                    _timeText.text = $"{currentTime.Hour:D2}:{currentTime.Minute:D2}:{currentTime.Second:D2}";
                }
                else
                {
                    _timeText.text = $"{currentTime.Hour:D2}:{currentTime.Minute:D2}";
                }
            }

            // Update date text
            if (_dateText != null)
            {
                _dateText.text = string.Format(_dateFormat, currentTime.Year, currentTime.Month, currentTime.Day);
            }

            // Update season display
            UpdateSeasonDisplay(currentTime.Season);
        }

        private void UpdateSeasonDisplay(Season season)
        {
            // Update season text
            if (_seasonText != null)
            {
                _seasonText.text = season.ToString();
                _seasonText.color = GetSeasonColor(season);
            }

            // Update season icon
            if (_seasonIcon != null)
            {
                _seasonIcon.sprite = GetSeasonIcon(season);
                _seasonIcon.color = GetSeasonColor(season);
            }
        }

        private void UpdatePauseButtons()
        {
            bool isPaused = TimeManager.IsPaused;

            if (_pauseButton != null)
            {
                _pauseButton.gameObject.SetActive(!isPaused);
            }

            if (_resumeButton != null)
            {
                _resumeButton.gameObject.SetActive(isPaused);
            }
        }

        private Sprite GetSeasonIcon(Season season)
        {
            return season switch
            {
                Season.Spring => _springIcon,
                Season.Summer => _summerIcon,
                Season.Autumn => _autumnIcon,
                Season.Winter => _winterIcon,
                _ => _springIcon
            };
        }

        private Color GetSeasonColor(Season season)
        {
            return season switch
            {
                Season.Spring => _springColor,
                Season.Summer => _summerColor,
                Season.Autumn => _autumnColor,
                Season.Winter => _winterColor,
                _ => _springColor
            };
        }

        // Public methods for external control

        /// <summary>
        /// Set whether to show seconds in time display
        /// </summary>
        public void SetShowSeconds(bool showSeconds)
        {
            _showSeconds = showSeconds;
            UpdateDisplay();
        }

        /// <summary>
        /// Set the time format string
        /// </summary>
        public void SetTimeFormat(string format)
        {
            _timeFormat = format;
            UpdateDisplay();
        }

        /// <summary>
        /// Set the date format string
        /// </summary>
        public void SetDateFormat(string format)
        {
            _dateFormat = format;
            UpdateDisplay();
        }

        /// <summary>
        /// Force update the display
        /// </summary>
        public void RefreshDisplay()
        {
            UpdateDisplay();
        }
    }
} 