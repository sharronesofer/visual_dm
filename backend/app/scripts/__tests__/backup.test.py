from typing import Any


const fs = require('fs')
const path = require('path')
const crypto = require('crypto')
const { createBackup } = require('../backup')
jest.mock('fs')
jest.mock('path')
jest.mock('crypto')
jest.mock('glob')
describe('Backup Script', () => {
  const mockFiles = [
    'src/index.ts',
    'src/components/App.tsx',
    'package.json'
  ]
  const mockFileContent = 'test content'
  const mockChecksum = 'test-checksum'
  beforeEach(() => {
    jest.clearAllMocks()
    require('glob').sync.mockReturnValue(mockFiles)
    (fs.mkdirSync as unknown as jest.Mock).mockImplementation(() => undefined)
    (fs.copyFileSync as unknown as jest.Mock).mockImplementation(() => undefined)
    (fs.writeFileSync as unknown as jest.Mock).mockImplementation(() => undefined)
    (fs.readFileSync as unknown as jest.Mock).mockReturnValue(Buffer.from(mockFileContent))
    (fs.statSync as unknown as jest.Mock).mockReturnValue({ size: mockFileContent.length })
    (path.join as unknown as jest.Mock).mockImplementation((...args) => args.join('/'))
    (path.dirname as unknown as jest.Mock).mockImplementation((p) => p.split('/').slice(0, -1).join('/'))
    (path.relative as unknown as jest.Mock).mockImplementation((from, to) => to)
    const mockHashUpdate = jest.fn().mockReturnThis()
    const mockHashDigest = jest.fn().mockReturnValue(mockChecksum)
    (crypto.createHash as unknown as jest.Mock).mockReturnValue({
      update: mockHashUpdate,
      digest: mockHashDigest
    })
    process.env.NODE_ENV = 'test'
  })
  it('should create backup directory with timestamp', async () => {
    await createBackup()
    expect(fs.mkdirSync).toHaveBeenCalledWith(expect.stringMatching(/backup_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}/), expect.any(Object))
  })
  it('should copy all files and create manifest', async () => {
    await createBackup()
    mockFiles.forEach(file => {
      expect(fs.copyFileSync).toHaveBeenCalledWith(
        expect.stringContaining(file),
        expect.stringContaining(file)
      )
    })
    expect(fs.writeFileSync).toHaveBeenCalledWith(
      expect.stringContaining('backup-manifest.json'),
      expect.stringMatching(/"totalFiles": 3/)
    )
  })
  it('should calculate checksums for verification', async () => {
    await createBackup()
    const expectedReads = mockFiles.length * 3
    expect(fs.readFileSync).toHaveBeenCalledTimes(expectedReads)
    expect(crypto.createHash).toHaveBeenCalledTimes(expectedReads)
  })
  it('should handle file copy failures', async () => {
    const failingFile = mockFiles[0]
    (fs.copyFileSync as unknown as jest.Mock).mockImplementationOnce(() => {
      throw new Error('Copy failed')
    })
    await expect(createBackup()).rejects.toThrow('Backup completed with 1 failed files')
  })
  it('should handle verification failures', async () => {
    let callCount = 0
    const mockHashDigest = jest.fn().mockImplementation(() => {
      callCount++
      return callCount <= 1 ? 'original-checksum' : 'different-checksum'
    })
    (crypto.createHash as unknown as jest.Mock).mockReturnValue({
      update: jest.fn().mockReturnThis(),
      digest: mockHashDigest
    })
    await expect(createBackup()).rejects.toThrow('Verification failed: checksums do not match')
  })
  it('should create correct manifest structure', async () => {
    await createBackup()
    expect(fs.writeFileSync).toHaveBeenCalledWith(
      expect.stringContaining('backup-manifest.json'),
      expect.any(String)
    )
    const manifestCall = (fs.writeFileSync as unknown as jest.Mock).mock.calls.find(
      call => call[0].includes('backup-manifest.json')
    )
    const manifest = JSON.parse(manifestCall[1])
    expect(manifest).toMatchObject({
      timestamp: expect.any(String),
      totalFiles: mockFiles.length,
      totalSize: expect.any(Number),
      files: expect.arrayContaining([
        expect.objectContaining({
          path: expect.any(String),
          size: expect.any(Number),
          checksum: expect.any(String)
        })
      ])
    })
  })
}) 