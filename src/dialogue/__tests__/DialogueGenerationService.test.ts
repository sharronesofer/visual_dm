import { DialogueGenerationService } from '../DialogueGenerationService';
import { GPTClient, GPTConfig, GPTResponse } from '../GPTClient';

class MockGPTClient {
    generateCompletion = jest.fn();
}

describe('DialogueGenerationService', () => {
    const defaultConfig: GPTConfig = { model: 'gpt-3.5-turbo', temperature: 0.5 };
    let gptClient: MockGPTClient;
    let service: DialogueGenerationService;

    beforeEach(() => {
        gptClient = new MockGPTClient();
        service = new DialogueGenerationService(gptClient as any as GPTClient, defaultConfig);
    });

    it('returns dialogue text on success', async () => {
        gptClient.generateCompletion.mockResolvedValue({ text: 'Hi there!' });
        const res = await service.generateDialogue('Hello', ['context1']);
        expect(res.text).toBe('Hi there!');
        expect(gptClient.generateCompletion).toHaveBeenCalledWith('Hello', ['context1'], defaultConfig);
    });

    it('merges config overrides', async () => {
        gptClient.generateCompletion.mockResolvedValue({ text: 'Override' });
        const res = await service.generateDialogue('Prompt', [], { temperature: 0.9 });
        expect(res.text).toBe('Override');
        expect(gptClient.generateCompletion).toHaveBeenCalledWith('Prompt', [], { ...defaultConfig, temperature: 0.9 });
    });

    it('logs and returns error if GPTClient returns error', async () => {
        gptClient.generateCompletion.mockResolvedValue({ text: '', error: 'API error' });
        const res = await service.generateDialogue('fail', []);
        expect(res.error).toBe('API error');
    });

    it('catches and logs thrown exceptions', async () => {
        gptClient.generateCompletion.mockRejectedValue(new Error('Thrown error'));
        const res = await service.generateDialogue('fail', []);
        expect(res.error).toBe('Thrown error');
    });
}); 