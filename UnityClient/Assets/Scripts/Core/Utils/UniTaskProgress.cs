using System;
using System.Collections.Generic;
using Cysharp.Threading.Tasks;
using UnityEngine;

namespace VisualDM.Core.Utils
{
    /// <summary>
    /// Handles progress reporting for UniTask operations
    /// </summary>
    public class UniTaskProgress : IProgress<float>
    {
        private readonly Action<float> _progressAction;
        private readonly Action<string> _messageAction;
        private float _currentProgress;
        private string _currentMessage = string.Empty;
        
        /// <summary>
        /// Current progress value (0-1)
        /// </summary>
        public float CurrentProgress => _currentProgress;
        
        /// <summary>
        /// Current status message
        /// </summary>
        public string CurrentMessage => _currentMessage;
        
        /// <summary>
        /// Event fired when progress changes
        /// </summary>
        public event Action<float> ProgressChanged;
        
        /// <summary>
        /// Event fired when message changes
        /// </summary>
        public event Action<string> MessageChanged;

        /// <summary>
        /// Creates a new UniTaskProgress with optional callbacks
        /// </summary>
        public UniTaskProgress(Action<float> progressAction = null, Action<string> messageAction = null)
        {
            _progressAction = progressAction;
            _messageAction = messageAction;
        }

        /// <summary>
        /// Report progress (0-1)
        /// </summary>
        public void Report(float value)
        {
            _currentProgress = Mathf.Clamp01(value);
            _progressAction?.Invoke(_currentProgress);
            ProgressChanged?.Invoke(_currentProgress);
        }
        
        /// <summary>
        /// Report progress with message
        /// </summary>
        public void Report(float value, string message)
        {
            Report(value);
            ReportMessage(message);
        }
        
        /// <summary>
        /// Report a status message
        /// </summary>
        public void ReportMessage(string message)
        {
            _currentMessage = message ?? string.Empty;
            _messageAction?.Invoke(_currentMessage);
            MessageChanged?.Invoke(_currentMessage);
        }
        
        /// <summary>
        /// Creates a child progress object that reports back to this parent with a specified weight
        /// </summary>
        public IProgress<float> CreateChild(float weight = 1.0f, float offset = 0.0f)
        {
            return new ChildProgress(this, weight, offset);
        }
        
        /// <summary>
        /// Creates a transformation progress that applies a function to the reported progress
        /// </summary>
        public IProgress<float> CreateTransform(Func<float, float> transformFunc)
        {
            return new TransformProgress(this, transformFunc);
        }
        
        /// <summary>
        /// Creates a progress aggregator that combines multiple child progresses
        /// </summary>
        public static IProgress<float> CreateAggregator(IProgress<float> target, params (IProgress<float> progress, float weight)[] sources)
        {
            return new AggregateProgress(target, sources);
        }

        #region Helper Classes
        
        private class ChildProgress : IProgress<float>
        {
            private readonly UniTaskProgress _parent;
            private readonly float _weight;
            private readonly float _offset;

            public ChildProgress(UniTaskProgress parent, float weight, float offset)
            {
                _parent = parent;
                _weight = Mathf.Clamp01(weight);
                _offset = Mathf.Clamp01(offset);
            }

            public void Report(float value)
            {
                // Scale value by weight and add offset
                float scaledValue = Mathf.Clamp01(value) * _weight + _offset;
                _parent.Report(scaledValue);
            }
        }

        private class TransformProgress : IProgress<float>
        {
            private readonly UniTaskProgress _target;
            private readonly Func<float, float> _transformFunc;

            public TransformProgress(UniTaskProgress target, Func<float, float> transformFunc)
            {
                _target = target;
                _transformFunc = transformFunc;
            }

            public void Report(float value)
            {
                float transformedValue = _transformFunc(value);
                _target.Report(transformedValue);
            }
        }

        private class AggregateProgress : IProgress<float>
        {
            private readonly IProgress<float> _target;
            private readonly Dictionary<IProgress<float>, float> _sources = new Dictionary<IProgress<float>, float>();
            private readonly Dictionary<IProgress<float>, float> _currentValues = new Dictionary<IProgress<float>, float>();
            private float _totalWeight;

            public AggregateProgress(IProgress<float> target, IEnumerable<(IProgress<float> progress, float weight)> sources)
            {
                _target = target;
                foreach (var (progress, weight) in sources)
                {
                    _sources[progress] = weight;
                    _currentValues[progress] = 0;
                    _totalWeight += weight;
                }
            }

            public void Report(float value)
            {
                // Find the reporting source
                foreach (var source in _sources.Keys)
                {
                    if (source == this)
                    {
                        _currentValues[source] = value;
                        break;
                    }
                }

                // Calculate weighted average
                float weightedSum = 0;
                foreach (var source in _sources.Keys)
                {
                    weightedSum += _currentValues[source] * _sources[source];
                }

                _target.Report(_totalWeight > 0 ? weightedSum / _totalWeight : 0);
            }
        }
        
        #endregion
    }
} 