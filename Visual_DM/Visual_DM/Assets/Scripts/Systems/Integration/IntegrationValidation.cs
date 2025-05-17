using System;
using System.Collections.Generic;

namespace Systems.Integration
{
    public static class IntegrationValidation
    {
        public static bool ValidateInput<T>(T input, Func<T, bool> validator)
        {
            return validator(input);
        }

        public static bool PreCondition(Func<bool> condition)
        {
            return condition();
        }

        public static bool PostCondition(Func<bool> condition)
        {
            return condition();
        }

        public static bool SchemaValidate<T>(T obj, Func<T, bool> schemaValidator)
        {
            return schemaValidator(obj);
        }

        public static bool IntegrityCheck(Func<bool> check)
        {
            return check();
        }
    }

    public class IntegrationTransaction : IDisposable
    {
        private readonly Action _rollback;
        private bool _committed;

        public IntegrationTransaction(Action rollback)
        {
            _rollback = rollback;
            _committed = false;
        }

        public void Commit()
        {
            _committed = true;
        }

        public void Dispose()
        {
            if (!_committed)
                _rollback();
        }
    }
} 