namespace VisualDM.CombatSystem
{
    /// <summary>
    /// Allows modification of effect parameters before application.
    /// </summary>
    public abstract class EffectModifier
    {
        protected EffectModifier next;

        public void SetNext(EffectModifier nextModifier)
        {
            next = nextModifier;
        }

        public virtual void Modify(IEffect effect, UnityEngine.GameObject target)
        {
            next?.Modify(effect, target);
        }
    }
} 