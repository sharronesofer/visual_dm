using System;
using System.Collections.Generic;
using UnityEngine;

namespace VisualDM.Animation
{
    /// <summary>
    /// Core timeline class for sequencing animation events with precise timing.
    /// </summary>
    public class AnimationTimeline
    {
        public enum TimelineState { Stopped, Playing, Paused, Cancelled }

        private float duration = 1.0f;
        private float playbackRate = 1.0f;
        private float currentTime = 0.0f;
        private TimelineState state = TimelineState.Stopped;
        private SortedDictionary<float, List<Action>> eventMap = new SortedDictionary<float, List<Action>>();
        private HashSet<float> triggeredEvents = new HashSet<float>();

        public float CurrentTime => currentTime;
        public bool IsPlaying => state == TimelineState.Playing;
        public TimelineState State => state;
        public float Duration => duration;
        public float PlaybackRate => playbackRate;

        public AnimationTimeline() { }

        public void RegisterEvent(float normalizedTime, Action callback)
        {
            if (normalizedTime < 0f || normalizedTime > 1f)
                throw new ArgumentOutOfRangeException(nameof(normalizedTime), "Must be between 0.0 and 1.0");
            if (!eventMap.ContainsKey(normalizedTime))
                eventMap[normalizedTime] = new List<Action>();
            eventMap[normalizedTime].Add(callback);
        }

        public void Start(float duration, float playbackRate = 1.0f)
        {
            if (duration <= 0f) duration = 0.01f; // Prevent zero-duration
            this.duration = duration;
            this.playbackRate = playbackRate;
            currentTime = 0f;
            state = TimelineState.Playing;
            triggeredEvents.Clear();
        }

        public void Update(float deltaTime)
        {
            if (state != TimelineState.Playing) return;
            float prevTime = currentTime;
            currentTime += deltaTime * playbackRate;
            float normalizedPrev = Mathf.Clamp01(prevTime / duration);
            float normalizedNow = Mathf.Clamp01(currentTime / duration);

            // Fire events between prevTime and currentTime
            foreach (var kvp in eventMap)
            {
                float t = kvp.Key;
                if (t > normalizedPrev && t <= normalizedNow && !triggeredEvents.Contains(t))
                {
                    foreach (var cb in kvp.Value)
                    {
                        try { cb?.Invoke(); } catch (Exception ex) { Debug.LogError($"AnimationTimeline event error: {ex}"); }
                    }
                    triggeredEvents.Add(t);
                }
            }

            if (currentTime >= duration)
            {
                state = TimelineState.Stopped;
                currentTime = duration;
            }
        }

        public void Pause()
        {
            if (state == TimelineState.Playing)
                state = TimelineState.Paused;
        }

        public void Resume()
        {
            if (state == TimelineState.Paused)
                state = TimelineState.Playing;
        }

        public void Cancel()
        {
            state = TimelineState.Cancelled;
        }

        public void Reset()
        {
            currentTime = 0f;
            state = TimelineState.Stopped;
            triggeredEvents.Clear();
        }

        public void SetPlaybackRate(float newRate)
        {
            playbackRate = newRate;
        }
    }
} 