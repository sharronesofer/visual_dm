import { DialogueConfigurationManager, DialogueConfigOptions } from '../../dialogue/config/DialogueConfigurationManager';
import { defaultPromptTemplates } from '../../dialogue/templates/promptTemplates';

/**
 * DialogueConfigPanel provides a UI for configuring dialogue generation settings, editing prompt templates,
 * managing presets, and collecting feedback on dialogue responses.
 */
export class DialogueConfigPanel {
    private container: HTMLElement;
    private configManager: DialogueConfigurationManager;
    private settingsForm: HTMLFormElement;
    private templateList: HTMLElement;
    private presetList: HTMLElement;
    private feedbackSection: HTMLElement;

    constructor(containerId: string, configManager: DialogueConfigurationManager) {
        const element = document.getElementById(containerId);
        if (!element) throw new Error(`Container element with id '${containerId}' not found`);
        this.container = element;
        this.configManager = configManager;
        this.settingsForm = document.createElement('form');
        this.templateList = document.createElement('div');
        this.presetList = document.createElement('div');
        this.feedbackSection = document.createElement('div');
        this.initializePanel();
    }

    /**
     * Initializes the configuration panel UI.
     */
    private initializePanel(): void {
        this.container.innerHTML = '';
        this.container.className = 'dialogue-config-panel';
        this.renderSettingsForm();
        this.renderTemplateList();
        this.renderPresetList();
        this.renderFeedbackSection();
        this.container.appendChild(this.settingsForm);
        this.container.appendChild(this.templateList);
        this.container.appendChild(this.presetList);
        this.container.appendChild(this.feedbackSection);
        // Add minimal CSS for layout
        const style = document.createElement('style');
        style.textContent = `
      .dialogue-config-panel { background: #23232b; color: #fff; padding: 16px; border-radius: 8px; max-width: 600px; }
      .dialogue-config-panel h3 { margin-top: 1.5em; }
      .dialogue-config-panel label { display: block; margin: 0.5em 0 0.2em; }
      .dialogue-config-panel input, .dialogue-config-panel select, .dialogue-config-panel textarea { width: 100%; margin-bottom: 0.5em; }
      .dialogue-config-panel .template-item { margin-bottom: 1em; }
      .dialogue-config-panel .preset-item { margin-bottom: 0.5em; }
      .dialogue-config-panel .feedback-section { margin-top: 2em; background: #18181f; padding: 1em; border-radius: 6px; }
    `;
        document.head.appendChild(style);
    }

    /**
     * Renders the settings form for dialogue configuration.
     */
    private renderSettingsForm(): void {
        this.settingsForm.innerHTML = '<h3>Dialogue Settings</h3>';
        const config = this.configManager.getConfig();
        // Model
        this.settingsForm.appendChild(this.createLabeledInput('Model', 'model', config.model));
        // Temperature
        this.settingsForm.appendChild(this.createLabeledInput('Temperature', 'temperature', config.temperature?.toString() || '0.7', 'number', 'step=0.01 min=0 max=2'));
        // Max Tokens
        this.settingsForm.appendChild(this.createLabeledInput('Max Tokens', 'maxTokens', config.maxTokens?.toString() || '512', 'number', 'min=1 max=4096'));
        // Tone
        this.settingsForm.appendChild(this.createLabeledInput('Tone', 'tone', config.tone || 'neutral'));
        // Response Style
        this.settingsForm.appendChild(this.createLabeledInput('Response Style', 'responseStyle', config.responseStyle || 'default'));
        // Save button
        const saveBtn = document.createElement('button');
        saveBtn.type = 'button';
        saveBtn.textContent = 'Save Settings';
        saveBtn.onclick = () => this.saveSettings();
        this.settingsForm.appendChild(saveBtn);
    }

    /**
     * Creates a labeled input element.
     */
    private createLabeledInput(label: string, name: string, value: string, type = 'text', extra = ''): HTMLElement {
        const wrapper = document.createElement('div');
        const lbl = document.createElement('label');
        lbl.textContent = label;
        const input = document.createElement('input');
        input.name = name;
        input.value = value;
        input.type = type;
        if (extra) {
            extra.split(' ').forEach(attr => {
                const [k, v] = attr.split('=');
                if (k && v) input.setAttribute(k, v.replace(/['"]/g, ''));
            });
        }
        wrapper.appendChild(lbl);
        wrapper.appendChild(input);
        return wrapper;
    }

    /**
     * Saves the settings from the form to the config manager.
     */
    private saveSettings(): void {
        const formData = new FormData(this.settingsForm);
        const newConfig: Partial<DialogueConfigOptions> = {
            model: formData.get('model') as string,
            temperature: parseFloat(formData.get('temperature') as string),
            maxTokens: parseInt(formData.get('maxTokens') as string, 10),
            tone: formData.get('tone') as string,
            responseStyle: formData.get('responseStyle') as string,
        };
        this.configManager.setConfig(newConfig);
        alert('Settings saved!');
    }

    /**
     * Renders the list of prompt templates for editing.
     */
    private renderTemplateList(): void {
        this.templateList.innerHTML = '<h3>Prompt Templates</h3>';
        const templates = this.configManager.getConfig().promptTemplates || defaultPromptTemplates;
        Object.entries(templates).forEach(([scenario, template]) => {
            const item = document.createElement('div');
            item.className = 'template-item';
            const lbl = document.createElement('label');
            lbl.textContent = scenario;
            const textarea = document.createElement('textarea');
            textarea.value = template;
            textarea.rows = 2;
            textarea.onchange = () => this.configManager.setPromptTemplate(scenario, textarea.value);
            item.appendChild(lbl);
            item.appendChild(textarea);
            this.templateList.appendChild(item);
        });
    }

    /**
     * Renders the list of configuration presets.
     */
    private renderPresetList(): void {
        this.presetList.innerHTML = '<h3>Presets</h3>';
        const presets = this.configManager.getConfig().presets || {};
        Object.entries(presets).forEach(([name, preset]) => {
            const item = document.createElement('div');
            item.className = 'preset-item';
            const btn = document.createElement('button');
            btn.textContent = `Apply "${name}"`;
            btn.onclick = () => { this.configManager.applyPreset(name); this.renderSettingsForm(); };
            item.appendChild(btn);
            this.presetList.appendChild(item);
        });
        // Add new preset
        const savePresetBtn = document.createElement('button');
        savePresetBtn.type = 'button';
        savePresetBtn.textContent = 'Save as New Preset';
        savePresetBtn.onclick = () => this.savePreset();
        this.presetList.appendChild(savePresetBtn);
    }

    /**
     * Saves the current config as a new preset.
     */
    private savePreset(): void {
        const name = prompt('Enter a name for the new preset:');
        if (name) {
            this.configManager.setPreset(name, this.configManager.getConfig());
            this.renderPresetList();
        }
    }

    /**
     * Renders the feedback section for rating/flagging dialogue responses.
     */
    private renderFeedbackSection(): void {
        this.feedbackSection.className = 'feedback-section';
        this.feedbackSection.innerHTML = '<h3>Dialogue Feedback</h3>';
        // For demonstration, allow rating the last dialogue response
        const rateLabel = document.createElement('label');
        rateLabel.textContent = 'Rate last response:';
        const select = document.createElement('select');
        ['Excellent', 'Good', 'Average', 'Poor', 'Flag as Problematic'].forEach(opt => {
            const option = document.createElement('option');
            option.value = opt;
            option.textContent = opt;
            select.appendChild(option);
        });
        const submitBtn = document.createElement('button');
        submitBtn.type = 'button';
        submitBtn.textContent = 'Submit Feedback';
        submitBtn.onclick = () => {
            alert(`Feedback submitted: ${select.value}`);
            // TODO: Integrate with feedback storage/analytics
        };
        this.feedbackSection.appendChild(rateLabel);
        this.feedbackSection.appendChild(select);
        this.feedbackSection.appendChild(submitBtn);
    }
} 