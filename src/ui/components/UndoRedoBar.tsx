import React from 'react';

export interface UndoRedoBarProps {
    onUndo: () => void;
    onRedo: () => void;
}

/**
 * UndoRedoBar provides undo and redo controls for customization actions.
 */
export const UndoRedoBar: React.FC<UndoRedoBarProps> = ({ onUndo, onRedo }) => (
    <div style={{ display: 'flex', gap: 12 }}>
        <button aria-label="Undo" style={{ padding: 8, borderRadius: 4, border: 'none', background: '#444', color: '#fff' }} onClick={onUndo}>Undo</button>
        <button aria-label="Redo" style={{ padding: 8, borderRadius: 4, border: 'none', background: '#444', color: '#fff' }} onClick={onRedo}>Redo</button>
    </div>
);

export default UndoRedoBar; 