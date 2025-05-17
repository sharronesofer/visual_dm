import { ErrorMessage } from './ErrorMessage';
import { ErrorCategory } from './ErrorCategory';

type ErrorListener = (error: ErrorMessage) => void;

export class ErrorEventSystem {
    private static listeners: { [category: string]: Set<ErrorListener> } = {};
    private static allListeners: Set<ErrorListener> = new Set();

    static subscribe(listener: ErrorListener, category?: ErrorCategory) {
        if (category) {
            if (!this.listeners[category]) this.listeners[category] = new Set();
            this.listeners[category].add(listener);
        } else {
            this.allListeners.add(listener);
        }
    }

    static unsubscribe(listener: ErrorListener, category?: ErrorCategory) {
        if (category) {
            this.listeners[category]?.delete(listener);
        } else {
            this.allListeners.delete(listener);
        }
    }

    static dispatch(error: ErrorMessage) {
        // Notify all listeners for this category
        this.listeners[error.category]?.forEach(listener => listener(error));
        // Notify global listeners
        this.allListeners.forEach(listener => listener(error));
    }
} 