using UnityEngine;

namespace VDM.Infrastructure.Core.Core.Ui
{
    /// <summary>
    /// Base class for UI components
    /// </summary>
    public abstract class BaseUIComponent : MonoBehaviour
    {
        [Header("UI Configuration")]
        [SerializeField] protected bool autoInitialize = true;
        [SerializeField] protected bool startVisible = true;
        
        protected bool isInitialized = false;
        
        protected virtual void Start()
        {
            if (autoInitialize)
            {
                Initialize();
            }
            
            if (!startVisible)
            {
                Hide();
            }
        }
        
        public virtual void Initialize()
        {
            if (isInitialized)
            {
                return;
            }
            
            OnInitialize();
            isInitialized = true;
        }
        
        public virtual void Show()
        {
            gameObject.SetActive(true);
            OnShow();
        }
        
        public virtual void Hide()
        {
            gameObject.SetActive(false);
            OnHide();
        }
        
        protected abstract void OnInitialize();
        protected virtual void OnShow() { }
        protected virtual void OnHide() { }
    }
} 