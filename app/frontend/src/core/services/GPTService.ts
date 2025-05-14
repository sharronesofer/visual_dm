import { ApiService, ApiResponse } from './ApiService';

interface GPTResponse {
  choices: Array<{
    text: string;
    index: number;
    logprobs: null;
    finish_reason: string;
  }>;
}

interface NameSuggestion {
  name: string;
  description: string;
}

export class GPTService {
  private static instance: GPTService;
  private apiService: ApiService;

  private constructor() {
    this.apiService = ApiService.getInstance();
  }

  public static getInstance(): GPTService {
    if (!GPTService.instance) {
      GPTService.instance = new GPTService();
    }
    return GPTService.instance;
  }

  public async generateNames(params: {
    race?: string;
    class?: string;
    alignment?: string;
    count?: number;
  }): Promise<NameSuggestion[]> {
    try {
      const { race = '', class: characterClass = '', alignment = '', count = 5 } = params;

      const prompt = `Generate ${count} fantasy character names suitable for a ${race} ${characterClass} with ${alignment} alignment. For each name, provide a brief description of its meaning or origin.`;

      const response = await this.apiService.post<GPTResponse>('/api/gpt/generate', {
        prompt,
        max_tokens: 200,
        temperature: 0.7,
      });

      if (response.error) {
        throw new Error(response.error.message);
      }

      // Parse the response and extract name suggestions
      const suggestions = this.parseNameSuggestions(response.data.choices[0].text);
      return suggestions;
    } catch (error) {
      console.error('Error generating names:', error);
      throw new Error('Failed to generate name suggestions');
    }
  }

  public async generateBackground(params: {
    name: string;
    race: string;
    class: string;
    alignment: string;
  }): Promise<string> {
    try {
      const { name, race, class: characterClass, alignment } = params;

      const prompt = `Create a compelling background story for a ${alignment} ${race} ${characterClass} named ${name}. Include their upbringing, motivations, and key events that shaped their character.`;

      const response = await this.apiService.post<GPTResponse>('/api/gpt/generate', {
        prompt,
        max_tokens: 500,
        temperature: 0.8,
      });

      if (response.error) {
        throw new Error(response.error.message);
      }

      return response.data.choices[0].text.trim();
    } catch (error) {
      console.error('Error generating background:', error);
      throw new Error('Failed to generate background story');
    }
  }

  private parseNameSuggestions(text: string): NameSuggestion[] {
    // Split the text into lines and parse each name suggestion
    const lines = text.split('\n').filter(line => line.trim());
    const suggestions: NameSuggestion[] = [];

    for (let i = 0; i < lines.length; i += 2) {
      const name = lines[i].replace(/^\d+\.\s*/, '').trim();
      const description = lines[i + 1]?.trim() || '';

      if (name) {
        suggestions.push({ name, description });
      }
    }

    return suggestions;
  }
}
