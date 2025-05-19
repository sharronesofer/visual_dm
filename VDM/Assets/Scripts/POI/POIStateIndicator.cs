using UnityEngine;
using TMPro;

namespace VDM.POI
{
    /// <summary>
    /// Visual indicator for POI state, color-codes SpriteRenderer and displays floating label.
    /// </summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public class POIStateIndicator : MonoBehaviour
    {
        private SpriteRenderer _spriteRenderer;
        private TextMeshPro _label;
        private POIStateManager _stateManager;

        private static readonly Color NormalColor = Color.green;
        private static readonly Color DecliningColor = Color.yellow;
        private static readonly Color AbandonedColor = new Color(1f, 0.5f, 0f); // Orange
        private static readonly Color RuinsColor = Color.gray;
        private static readonly Color DungeonColor = Color.red;

        void Awake()
        {
            _spriteRenderer = GetComponent<SpriteRenderer>();
            _stateManager = GetComponent<POIStateManager>();
            if (_stateManager != null)
            {
                _stateManager.OnStateChanged += HandleStateChanged;
                HandleStateChanged(null, _stateManager.CurrentState);
            }
            // Create floating label
            var labelObj = new GameObject("POIStateLabel");
            labelObj.transform.SetParent(transform);
            labelObj.transform.localPosition = new Vector3(0, 1.5f, 0);
            _label = labelObj.AddComponent<TextMeshPro>();
            _label.fontSize = 3;
            _label.alignment = TextAlignmentOptions.Center;
        }

        private void HandleStateChanged(POIState oldState, POIState newState)
        {
            if (newState == null) return;
            switch (newState.Type)
            {
                case POIStateType.Normal:
                    _spriteRenderer.color = NormalColor;
                    break;
                case POIStateType.Declining:
                    _spriteRenderer.color = DecliningColor;
                    break;
                case POIStateType.Abandoned:
                    _spriteRenderer.color = AbandonedColor;
                    break;
                case POIStateType.Ruins:
                    _spriteRenderer.color = RuinsColor;
                    break;
                case POIStateType.Dungeon:
                    _spriteRenderer.color = DungeonColor;
                    break;
            }
            UpdateLabel();
        }

        private void UpdateLabel()
        {
            if (_stateManager == null || _label == null) return;
            _label.text = $"{_stateManager.CurrentState.Type}\nPop: {_stateManager.CurrentPopulation}/{_stateManager.MaxPopulation}";
            // Show warning if near threshold
            var rules = _stateManager.GetTransitionRuleSet();
            if (rules != null)
            {
                foreach (var rule in rules.transitionRules)
                {
                    if (rule.fromState.ToString() == _stateManager.CurrentState.Type.ToString())
                    {
                        float thresholdPop = rule.populationThreshold * _stateManager.MaxPopulation;
                        float pop = _stateManager.CurrentPopulation;
                        if (!rule.oneWayOnly && pop > thresholdPop && pop < thresholdPop + 0.1f * _stateManager.MaxPopulation)
                        {
                            _label.text += "\n<color=yellow>Near upward threshold!</color>";
                            StartFlashing(Color.yellow);
                        }
                        else if (pop < thresholdPop && pop > thresholdPop - 0.1f * _stateManager.MaxPopulation)
                        {
                            _label.text += "\n<color=orange>Near transition!</color>";
                            StartFlashing(new Color(1f, 0.5f, 0f));
                        }
                        else
                        {
                            StopFlashing();
                        }
                    }
                }
            }
        }

        private bool _isFlashing = false;
        private Color _flashColor;
        private float _flashTimer = 0f;
        private void StartFlashing(Color color)
        {
            _isFlashing = true;
            _flashColor = color;
            _flashTimer = 0f;
        }
        private void StopFlashing()
        {
            _isFlashing = false;
            _spriteRenderer.color = GetColorForState(_stateManager.CurrentState.Type);
        }
        private void Update()
        {
            if (_isFlashing)
            {
                _flashTimer += Time.deltaTime;
                float t = Mathf.PingPong(_flashTimer * 2f, 1f);
                _spriteRenderer.color = Color.Lerp(GetColorForState(_stateManager.CurrentState.Type), _flashColor, t);
            }
        }
        private Color GetColorForState(POIStateType type)
        {
            switch (type)
            {
                case POIStateType.Normal: return NormalColor;
                case POIStateType.Declining: return DecliningColor;
                case POIStateType.Abandoned: return AbandonedColor;
                case POIStateType.Ruins: return RuinsColor;
                case POIStateType.Dungeon: return DungeonColor;
                default: return Color.white;
            }
        }

        void OnDestroy()
        {
            if (_stateManager != null)
                _stateManager.OnStateChanged -= HandleStateChanged;
        }
    }
} 