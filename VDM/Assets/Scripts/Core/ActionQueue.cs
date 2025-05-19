using System;
using System.Collections.Generic;
using UnityEngine;
using VisualDM.Core;

namespace VisualDM.Core
{
    public enum ActionType
    {
        Attack,
        Defend,
        Move,
        UseItem,
        Special,
        Custom,
        ChainAction
    }

    public enum ActionSource
    {
        Player,
        AI
    }

    public enum PriorityTier
    {
        Critical = 100,
        High = 75,
        Normal = 50,
        Low = 25
    }

    public enum CancellationReason { None, Manual, Timeout, Dependency, GameState }
    public enum InterruptionReason { None, Animation, External, UserCore, System }

    public class ActionEntry
    {
        public ActionType Type;
        public ActionSource Source;
        public int Priority; // Higher = more important
        public float Timestamp; // ms
        public float ExpiryMs; // ms after which action expires
        public object Context; // Optional: extra data
        public PriorityTier Tier;
        public int BasePriority => (int)Tier;
        public int BoostedPriority;
        public float BoostExpiry;
        public Guid? ParentActionId;
        public bool IsCancelled;
        public bool IsInterrupted;
        public CancellationReason CancelReason;
        public InterruptionReason InterruptReason;
        public Guid ActionId;
        public object SavedState;

        public ActionEntry(ActionType type, ActionSource source, PriorityTier tier, float expiryMs, object context = null, Guid? parentActionId = null, string sessionId = null)
        {
            Type = type;
            Source = source;
            Tier = tier;
            Priority = (int)tier;
            BoostedPriority = (int)tier;
            ExpiryMs = expiryMs;
            Context = context;
            ParentActionId = parentActionId;
            BoostExpiry = 0f;
            IsCancelled = false;
            IsInterrupted = false;
            CancelReason = CancellationReason.None;
            InterruptReason = InterruptionReason.None;
            Timestamp = UnityEngine.Time.realtimeSinceStartup * 1000f;
            if (!string.IsNullOrEmpty(sessionId))
                ActionId = Guid.Parse(IdGenerator.GenerateActionId(sessionId));
            else
                ActionId = Guid.NewGuid();
            SavedState = null;
        }

        public void BoostPriority(int amount, float durationMs)
        {
            BoostedPriority = BasePriority + amount;
            BoostExpiry = Time.unscaledTime * 1000f + durationMs;
        }

        public void UpdateBoost()
        {
            if (BoostExpiry > 0f && Time.unscaledTime * 1000f > BoostExpiry)
                BoostedPriority = BasePriority;
        }

        public bool IsExpired(float now)
        {
            return now - Timestamp > ExpiryMs;
        }
    }

    public class ActionQueue
    {
        private List<ActionEntry> queue = new List<ActionEntry>();
        private int maxCapacity;
        private float defaultExpiryMs;

        public event Action<ActionEntry> OnActionCancelled;
        public event Action<ActionEntry> OnActionInterrupted;

        public ActionQueue(int maxCapacity = 12, float defaultExpiryMs = 1000f)
        {
            this.maxCapacity = Mathf.Max(4, maxCapacity);
            this.defaultExpiryMs = Mathf.Clamp(defaultExpiryMs, 500f, 2000f);
        }

        public bool EnqueueAction(ActionEntry action)
        {
            PruneExpiredActions();
            if (queue.Count >= maxCapacity)
            {
                // Drop lowest-priority or oldest
                queue.Sort(CompareActions);
                queue.RemoveAt(queue.Count - 1);
            }
            queue.Add(action);
            queue.Sort(CompareActions);
            return true;
        }

        public ActionEntry DequeueAction()
        {
            PruneExpiredActions();
            if (queue.Count == 0) return null;
            var action = queue[0];
            queue.RemoveAt(0);
            return action;
        }

        public void RemoveAction(Predicate<ActionEntry> predicate)
        {
            queue.RemoveAll(predicate);
        }

        public void UpdateAction(Predicate<ActionEntry> predicate, Action<ActionEntry> update)
        {
            foreach (var action in queue)
            {
                if (predicate(action))
                    update(action);
            }
        }

        public void PruneExpiredActions()
        {
            float now = Time.unscaledTime * 1000f;
            queue.RemoveAll(a => a.IsExpired(now));
        }

        public List<ActionEntry> GetQueueSnapshot()
        {
            PruneExpiredActions();
            return new List<ActionEntry>(queue);
        }

        private int CompareActions(ActionEntry a, ActionEntry b)
        {
            a.UpdateBoost();
            b.UpdateBoost();
            int cmp = b.BoostedPriority.CompareTo(a.BoostedPriority); // Descending
            if (cmp == 0)
                cmp = ((int)b.Tier).CompareTo((int)a.Tier); // Descending by tier
            if (cmp == 0)
                cmp = a.Timestamp.CompareTo(b.Timestamp); // Ascending (older first)
            if (cmp == 0)
                cmp = a.Source.CompareTo(b.Source); // Prefer Player (lower enum value)
            return cmp;
        }

        // Example validation integration
        public bool ValidateAndEnqueue(ActionEntry action, InputBuffer inputBuffer, GameState state)
        {
            // Example: Only enqueue if input is valid in current state
            // (Assume action.Context contains InputEvent)
            if (action.Context is InputEvent inputEvent)
            {
                if (!inputBuffer.ValidateInput(inputEvent, state))
                    return false;
            }
            return EnqueueAction(action);
        }

        public void BoostPriority(ActionEntry action, int amount, float durationMs)
        {
            action.BoostPriority(amount, durationMs);
        }

        public void AdjustPriorityBasedOnContext(ActionEntry action, GameState state)
        {
            // Example: boost Move in SceneTransition, Attack in Gameplay
            if (state == GameState.SceneTransition && action.Type == ActionType.Move)
                action.BoostPriority(30, 300f);
            else if (state == GameState.Gameplay && action.Type == ActionType.Attack)
                action.BoostPriority(20, 200f);
        }

        // Priority inheritance
        public void InheritPriority(ActionEntry child, ActionEntry parent)
        {
            if (parent != null)
            {
                child.Tier = parent.Tier;
                child.BoostedPriority = parent.BoostedPriority;
                child.ParentActionId = parent.ParentActionId ?? Guid.NewGuid();
            }
        }

        public void CancelAction(Guid actionId, CancellationReason reason = CancellationReason.Manual)
        {
            var action = queue.Find(a => a.ActionId == actionId);
            if (action != null)
            {
                action.IsCancelled = true;
                action.CancelReason = reason;
                queue.Remove(action);
                OnActionCancelled?.Invoke(action);
                // Cascading: cancel children
                CancelChildActions(action.ActionId, reason);
            }
        }

        public void CancelActionsByType(ActionType type, CancellationReason reason = CancellationReason.Manual)
        {
            var toCancel = queue.FindAll(a => a.Type == type);
            foreach (var action in toCancel)
                CancelAction(action.ActionId, reason);
        }

        public void CancelActionsBySource(ActionSource source, CancellationReason reason = CancellationReason.Manual)
        {
            var toCancel = queue.FindAll(a => a.Source == source);
            foreach (var action in toCancel)
                CancelAction(action.ActionId, reason);
        }

        private void CancelChildActions(Guid parentId, CancellationReason reason)
        {
            var children = queue.FindAll(a => a.ParentActionId == parentId);
            foreach (var child in children)
                CancelAction(child.ActionId, reason);
        }

        public void InterruptAction(Guid actionId, InterruptionReason reason = InterruptionReason.System)
        {
            var action = queue.Find(a => a.ActionId == actionId);
            if (action != null)
            {
                action.IsInterrupted = true;
                action.InterruptReason = reason;
                queue.Remove(action);
                OnActionInterrupted?.Invoke(action);
                // Optionally: Save state for recovery
                action.SavedState = SaveInterruptedState(action);
            }
        }

        public void InterruptCurrentAction(InterruptionReason reason = InterruptionReason.System)
        {
            if (queue.Count > 0)
                InterruptAction(queue[0].ActionId, reason);
        }

        private object SaveInterruptedState(ActionEntry action)
        {
            // Placeholder for saving state (extend as needed)
            return null;
        }

        public void RequeueInterruptedAction(Guid actionId)
        {
            // Find interrupted action (not in queue)
            // For demo, assume we have a way to track interrupted actions externally
            // Implement as needed
        }

        public void CreateFallbackAction(Guid interruptedActionId)
        {
            // Generate a fallback/simplified action for recovery
            // Implement as needed
        }

        public void RestoreActionState(ActionEntry action)
        {
            // Restore saved state if needed
            // Implement as needed
        }
    }
} 