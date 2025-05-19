using UnityEngine;

namespace VisualDM.UI
{
    public class InventoryFeedbackSystem : MonoBehaviour
    {
        private AudioSource audioSource;
        private AudioClip successClip;
        private AudioClip errorClip;
        private AudioClip acquireClip;
        private AudioClip discardClip;

        void Awake()
        {
            audioSource = gameObject.AddComponent<AudioSource>();
            successClip = Resources.Load<AudioClip>("Sounds/inventory_success");
            errorClip = Resources.Load<AudioClip>("Sounds/inventory_error");
            acquireClip = Resources.Load<AudioClip>("Sounds/inventory_acquire");
            discardClip = Resources.Load<AudioClip>("Sounds/inventory_discard");
        }

        public void PlaySuccessSound()
        {
            if (successClip) audioSource.PlayOneShot(successClip);
        }
        public void PlayErrorSound()
        {
            if (errorClip) audioSource.PlayOneShot(errorClip);
        }
        public void PlayItemAcquired()
        {
            if (acquireClip) audioSource.PlayOneShot(acquireClip);
        }
        public void PlayItemDiscarded()
        {
            if (discardClip) audioSource.PlayOneShot(discardClip);
        }
    }
} 