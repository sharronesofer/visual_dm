from typing import Any, Dict


global.fetch = jest.fn()
describe('GPTService', () => {
  let gptService: GPTService
  beforeEach(() => {
    jest.clearAllMocks()
    gptService = GPTService.getInstance()
  })
  describe('generateNames', () => {
    const mockCharacterInfo = {
      race: 'Elf',
      class: 'Wizard',
      alignment: 'Lawful Good',
    }
    it('successfully generates name suggestions', async () => {
      const mockResponse = {
        ok: true,
        json: jest.fn().mockResolvedValue({
          choices: [
            {
              message: Dict[str, Any],
                  { name: 'Thalanil', description: 'Mystic sage name' },
                ]),
              },
            },
          ],
        }),
      }
      (global.fetch as jest.Mock).mockResolvedValue(mockResponse)
      const result = await gptService.generateNames(mockCharacterInfo)
      expect(result).toHaveLength(2)
      expect(result[0].name).toBe('Elindor')
      expect(result[1].name).toBe('Thalanil')
      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: expect.stringContaining('Elf'),
        })
      )
    })
    it('handles API error gracefully', async () => {
      const mockError = new Error('API Error')
      (global.fetch as jest.Mock).mockRejectedValue(mockError)
      await expect(gptService.generateNames(mockCharacterInfo)).rejects.toThrow(
        'Failed to generate name suggestions'
      )
    })
    it('handles malformed API response', async () => {
      const mockResponse = {
        ok: true,
        json: jest.fn().mockResolvedValue({
          choices: [
            {
              message: Dict[str, Any],
            },
          ],
        }),
      }
      (global.fetch as jest.Mock).mockResolvedValue(mockResponse)
      await expect(gptService.generateNames(mockCharacterInfo)).rejects.toThrow(
        'Failed to parse name suggestions'
      )
    })
  })
  describe('generateBackground', () => {
    const mockCharacterInfo = {
      name: 'Elindor',
      race: 'Elf',
      class: 'Wizard',
      alignment: 'Lawful Good',
    }
    it('successfully generates background story', async () => {
      const mockStory = 'A fascinating tale of an elven wizard...'
      const mockResponse = {
        ok: true,
        json: jest.fn().mockResolvedValue({
          choices: [
            {
              message: Dict[str, Any],
            },
          ],
        }),
      }
      (global.fetch as jest.Mock).mockResolvedValue(mockResponse)
      const result = await gptService.generateBackground(mockCharacterInfo)
      expect(result).toBe(mockStory)
      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: expect.stringContaining('Elindor'),
        })
      )
    })
    it('handles API error gracefully', async () => {
      const mockError = new Error('API Error')
      (global.fetch as jest.Mock).mockRejectedValue(mockError)
      await expect(
        gptService.generateBackground(mockCharacterInfo)
      ).rejects.toThrow('Failed to generate background story')
    })
    it('handles empty API response', async () => {
      const mockResponse = {
        ok: true,
        json: jest.fn().mockResolvedValue({
          choices: [],
        }),
      }
      (global.fetch as jest.Mock).mockResolvedValue(mockResponse)
      await expect(
        gptService.generateBackground(mockCharacterInfo)
      ).rejects.toThrow('No background story generated')
    })
    it('retries on rate limit error', async () => {
      const rateLimitResponse = {
        ok: false,
        status: 429,
        json: jest.fn().mockResolvedValue({ error: 'Rate limit exceeded' }),
      }
      const successResponse = {
        ok: true,
        json: jest.fn().mockResolvedValue({
          choices: [
            {
              message: Dict[str, Any],
            },
          ],
        }),
      }
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce(rateLimitResponse)
        .mockResolvedValueOnce(successResponse)
      const result = await gptService.generateBackground(mockCharacterInfo)
      expect(result).toBe('A successful story after retry')
      expect(global.fetch).toHaveBeenCalledTimes(2)
    })
  })
  describe('error handling', () => {
    it('handles network errors', async () => {
      const mockError = new Error('Network error')
      (global.fetch as jest.Mock).mockRejectedValue(mockError)
      await expect(
        gptService.generateNames({
          race: 'Elf',
          class: 'Wizard',
          alignment: 'Lawful Good',
        })
      ).rejects.toThrow('Failed to generate name suggestions')
    })
    it('handles invalid API key', async () => {
      const mockResponse = {
        ok: false,
        status: 401,
        json: jest.fn().mockResolvedValue({ error: 'Invalid API key' }),
      }
      (global.fetch as jest.Mock).mockResolvedValue(mockResponse)
      await expect(
        gptService.generateNames({
          race: 'Elf',
          class: 'Wizard',
          alignment: 'Lawful Good',
        })
      ).rejects.toThrow('Authentication failed')
    })
    it('handles rate limiting', async () => {
      const mockResponse = {
        ok: false,
        status: 429,
        json: jest.fn().mockResolvedValue({ error: 'Rate limit exceeded' }),
      }
      (global.fetch as jest.Mock).mockResolvedValue(mockResponse)
      await expect(
        gptService.generateNames({
          race: 'Elf',
          class: 'Wizard',
          alignment: 'Lawful Good',
        })
      ).rejects.toThrow('Rate limit exceeded')
    })
  })
})