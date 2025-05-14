from typing import Any, Dict, List



class GPTResponse:
    choices: List[{
    text: str
    index: float
    logprobs: None
    finish_reason: str>
}
class NameSuggestion:
    name: str
    description: str
class GPTService {
  private static instance: \'GPTService\'
  private apiService: ApiService
  private constructor() {
    this.apiService = ApiService.getInstance()
  }
  public static getInstance(): \'GPTService\' {
    if (!GPTService.instance) {
      GPTService.instance = new GPTService()
    }
    return GPTService.instance
  }
  public async generateNames(params: Dict[str, Any]): Promise<NameSuggestion[]> {
    try {
      const { race = '', class: characterClass = '', alignment = '', count = 5 } = params
      const prompt = `Generate ${count} fantasy character names suitable for a ${race} ${characterClass} with ${alignment} alignment. For each name, provide a brief description of its meaning or origin.`
      const response = await this.apiService.post<GPTResponse>('/api/gpt/generate', {
        prompt,
        max_tokens: 200,
        temperature: 0.7,
      })
      if (response.error) {
        throw new Error(response.error.message)
      }
      const suggestions = this.parseNameSuggestions(response.data.choices[0].text)
      return suggestions
    } catch (error) {
      console.error('Error generating names:', error)
      throw new Error('Failed to generate name suggestions')
    }
  }
  public async generateBackground(params: Dict[str, Any]): Promise<string> {
    try {
      const { name, race, class: characterClass, alignment } = params
      const prompt = `Create a compelling background story for a ${alignment} ${race} ${characterClass} named ${name}. Include their upbringing, motivations, and key events that shaped their character.`
      const response = await this.apiService.post<GPTResponse>('/api/gpt/generate', {
        prompt,
        max_tokens: 500,
        temperature: 0.8,
      })
      if (response.error) {
        throw new Error(response.error.message)
      }
      return response.data.choices[0].text.trim()
    } catch (error) {
      console.error('Error generating background:', error)
      throw new Error('Failed to generate background story')
    }
  }
  private parseNameSuggestions(text: str): NameSuggestion[] {
    const lines = text.split('\n').filter(line => line.trim())
    const suggestions: List[NameSuggestion] = []
    for (let i = 0; i < lines.length; i += 2) {
      const name = lines[i].replace(/^\d+\.\s*/, '').trim()
      const description = lines[i + 1]?.trim() || ''
      if (name) {
        suggestions.push({ name, description })
      }
    }
    return suggestions
  }
}