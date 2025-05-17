import { DialogueConfigurationManager, defaultDialogueConfig } from '../config/DialogueConfigurationManager';
import { defaultPromptTemplates } from '../templates/promptTemplates';

describe('DialogueConfigurationManager', () => {
    it('loads default config and templates', () => {
        const manager = new DialogueConfigurationManager();
        expect(manager.getConfig().model).toBe(defaultDialogueConfig.model);
        expect(manager.getPromptTemplate('mentoring')).toBe(defaultPromptTemplates.mentoring);
    });

    it('can update config and retrieve new values', () => {
        const manager = new DialogueConfigurationManager();
        manager.setConfig({ model: 'gpt-3.5-turbo', temperature: 0.5 });
        expect(manager.getConfig().model).toBe('gpt-3.5-turbo');
        expect(manager.getConfig().temperature).toBe(0.5);
    });

    it('can set and apply presets', () => {
        const manager = new DialogueConfigurationManager();
        manager.setPreset('friendly', { ...defaultDialogueConfig, tone: 'friendly' });
        manager.applyPreset('friendly');
        expect(manager.getConfig().tone).toBe('friendly');
    });

    it('can set and get prompt templates', () => {
        const manager = new DialogueConfigurationManager();
        manager.setPromptTemplate('test_scenario', 'Test template');
        expect(manager.getPromptTemplate('test_scenario')).toBe('Test template');
    });
}); 