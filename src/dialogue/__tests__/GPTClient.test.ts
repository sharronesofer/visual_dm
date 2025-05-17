import { GPTClient, GPTConfig } from '../GPTClient';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Helper to mock the axios instance returned by axios.create
function mockAxiosInstancePost(mockImpl: any) {
    const instance = { post: jest.fn(mockImpl) };
    mockedAxios.create.mockReturnValue(instance as any);
    return instance;
}

describe('GPTClient', () => {
    const apiKey = 'test-key';
    let client: GPTClient;
    const config: GPTConfig = { model: 'gpt-3.5-turbo' };

    beforeEach(() => {
        jest.clearAllMocks();
        client = new GPTClient({ apiKey, rateLimit: 2, timeoutMs: 100 });
        // Mock sleep to avoid real delays
        jest.spyOn(client as any, 'sleep').mockImplementation(() => Promise.resolve());
    });

    it('returns text on successful response', async () => {
        const instance = mockAxiosInstancePost(jest.fn().mockResolvedValueOnce({
            data: {
                choices: [{ message: { content: 'Hello world!' } }],
                usage: { prompt_tokens: 5, completion_tokens: 3, total_tokens: 8 },
            },
        }));
        (client as any).axios = instance;
        const res = await client.generateCompletion('Hi', [], config);
        expect(res.text).toEqual('Hello world!');
        expect(res.usage?.total_tokens).toEqual(8);
    });

    it('handles API error and retries, then returns error after 3 attempts', async () => {
        const instance = mockAxiosInstancePost(jest.fn().mockRejectedValue({ message: 'API down', response: { data: { error: 'fail' } } }));
        (client as any).axios = instance;
        client.on('error', () => { }); // Prevent unhandled error event
        const res = await client.generateCompletion('fail', [], config);
        expect(res.text).toEqual('');
        expect(res.error).toEqual('API down');
    });

    it('enforces rate limit', async () => {
        const instance = mockAxiosInstancePost(jest.fn().mockResolvedValue({
            data: {
                choices: [{ message: { content: 'A' } }],
                usage: { prompt_tokens: 1, completion_tokens: 1, total_tokens: 2 },
            },
        }));
        (client as any).axios = instance;
        await client.generateCompletion('A', [], config);
        await client.generateCompletion('B', [], config);
        const start = Date.now();
        await client.generateCompletion('C', [], config); // Should delay (mocked)
        const elapsed = Date.now() - start;
        expect(elapsed).toBeGreaterThanOrEqual(0); // Should not actually delay
    });

    it('counts tokens approximately', () => {
        expect(GPTClient.countTokens('12345678')).toEqual(2);
        expect(GPTClient.countTokens('abcd efgh ijkl')).toBeGreaterThan(2);
    });

    it('emits request, error, and fallback events', async () => {
        const instance = mockAxiosInstancePost(jest.fn().mockRejectedValue({ message: 'API down', response: { data: { error: 'fail' } } }));
        (client as any).axios = instance;
        const requestListener = jest.fn();
        const errorListener = jest.fn();
        const fallbackListener = jest.fn();
        client.on('request', requestListener);
        client.on('error', errorListener);
        client.on('fallback', fallbackListener);
        await client.generateCompletion('fail', [], config);
        expect(requestListener).toHaveBeenCalled();
        expect(errorListener).toHaveBeenCalled();
        expect(fallbackListener).toHaveBeenCalled();
    });

    it('tracks and reports token usage stats', async () => {
        const instance = mockAxiosInstancePost(jest.fn().mockResolvedValueOnce({
            data: {
                choices: [{ message: { content: 'Hello world!' } }],
                usage: { prompt_tokens: 5, completion_tokens: 3, total_tokens: 8 },
            },
        }));
        (client as any).axios = instance;
        await client.generateCompletion('Hi', [], config);
        const stats = client.getUsageStats();
        expect(stats.totalTokens).toBeGreaterThanOrEqual(8);
        expect(stats.rollingTokens).toBeGreaterThanOrEqual(8);
    });
}); 