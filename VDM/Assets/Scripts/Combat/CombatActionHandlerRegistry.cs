using System.Collections.Generic;

namespace VDM.Combat
{
    /// <summary>
    /// Registry for combat action handlers by action type.
    /// </summary>
    public class CombatActionHandlerRegistry
    {
        private readonly Dictionary<CombatActionType, ICombatActionHandler> _handlers = new();

        public void RegisterHandler(CombatActionType type, ICombatActionHandler handler)
        {
            _handlers[type] = handler;
        }

        public ICombatActionHandler GetHandler(CombatActionType type)
        {
            return _handlers.TryGetValue(type, out var handler) ? handler : null;
        }
    }
} 