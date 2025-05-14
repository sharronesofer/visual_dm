// Flash message auto-dismiss
document.addEventListener('DOMContentLoaded', () => {
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        // Auto-dismiss flash messages after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);

        // Add close button
        const closeButton = document.createElement('button');
        closeButton.innerHTML = '×';
        closeButton.className = 'flash-close';
        closeButton.onclick = () => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        };
        message.appendChild(closeButton);
    });
});

// Form validation
document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.querySelector('form[action*="register"]');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            const password = registerForm.querySelector('#password').value;
            const confirmPassword = registerForm.querySelector('#confirm_password').value;

            if (password !== confirmPassword) {
                e.preventDefault();
                alert('Passwords do not match!');
            }

            if (password.length < 8) {
                e.preventDefault();
                alert('Password must be at least 8 characters long!');
            }
        });
    }
});

// Add CSS styles for the close button
const style = document.createElement('style');
style.textContent = `
    .flash-close {
        position: absolute;
        right: 10px;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        color: inherit;
        font-size: 20px;
        cursor: pointer;
        padding: 0;
        margin: 0;
        opacity: 0.7;
    }
    .flash-close:hover {
        opacity: 1;
    }
    .flash-message {
        position: relative;
        transition: opacity 0.3s ease;
    }
`;
document.head.appendChild(style); 