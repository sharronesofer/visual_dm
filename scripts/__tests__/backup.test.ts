const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { createBackup } = require('../backup');

jest.mock('fs');
jest.mock('path');
jest.mock('crypto');
jest.mock('glob');

describe('Backup Script', () => {
  const mockFiles = [
    'src/index.ts',
    'src/components/App.tsx',
    'package.json'
  ];

  const mockFileContent = 'test content';
  const mockChecksum = 'test-checksum';

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Mock glob.sync
    require('glob').sync.mockReturnValue(mockFiles);

    // Mock fs functions
    (fs.mkdirSync as unknown as jest.Mock).mockImplementation(() => undefined);
    (fs.copyFileSync as unknown as jest.Mock).mockImplementation(() => undefined);
    (fs.writeFileSync as unknown as jest.Mock).mockImplementation(() => undefined);
    (fs.readFileSync as unknown as jest.Mock).mockReturnValue(Buffer.from(mockFileContent));
    (fs.statSync as unknown as jest.Mock).mockReturnValue({ size: mockFileContent.length });

    // Mock path functions
    (path.join as unknown as jest.Mock).mockImplementation((...args) => args.join('/'));
    (path.dirname as unknown as jest.Mock).mockImplementation((p) => p.split('/').slice(0, -1).join('/'));
    (path.relative as unknown as jest.Mock).mockImplementation((from, to) => to);

    // Mock createHash
    const mockHashUpdate = jest.fn().mockReturnThis();
    const mockHashDigest = jest.fn().mockReturnValue(mockChecksum);
    (crypto.createHash as unknown as jest.Mock).mockReturnValue({
      update: mockHashUpdate,
      digest: mockHashDigest
    });

    // Set test environment
    process.env.NODE_ENV = 'test';
  });

  it('should create backup directory with timestamp', async () => {
    await createBackup();
    expect(fs.mkdirSync).toHaveBeenCalledWith(expect.stringMatching(/backup_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}/), expect.any(Object));
  });

  it('should copy all files and create manifest', async () => {
    await createBackup();

    // Verify each file was copied
    mockFiles.forEach(file => {
      expect(fs.copyFileSync).toHaveBeenCalledWith(
        expect.stringContaining(file),
        expect.stringContaining(file)
      );
    });

    // Verify manifest was created
    expect(fs.writeFileSync).toHaveBeenCalledWith(
      expect.stringContaining('backup-manifest.json'),
      expect.stringMatching(/"totalFiles": 3/)
    );
  });

  it('should calculate checksums for verification', async () => {
    await createBackup();
    
    // Each file should be read twice: once for verification (source + dest) and once for manifest
    const expectedReads = mockFiles.length * 3;
    expect(fs.readFileSync).toHaveBeenCalledTimes(expectedReads);
    expect(crypto.createHash).toHaveBeenCalledTimes(expectedReads);
  });

  it('should handle file copy failures', async () => {
    const failingFile = mockFiles[0];
    (fs.copyFileSync as unknown as jest.Mock).mockImplementationOnce(() => {
      throw new Error('Copy failed');
    });

    await expect(createBackup()).rejects.toThrow('Backup completed with 1 failed files');
  });

  it('should handle verification failures', async () => {
    // Make verification fail for first file by returning different checksums
    let callCount = 0;
    const mockHashDigest = jest.fn().mockImplementation(() => {
      callCount++;
      return callCount <= 1 ? 'original-checksum' : 'different-checksum';
    });
    (crypto.createHash as unknown as jest.Mock).mockReturnValue({
      update: jest.fn().mockReturnThis(),
      digest: mockHashDigest
    });

    await expect(createBackup()).rejects.toThrow('Verification failed: checksums do not match');
  });

  it('should create correct manifest structure', async () => {
    await createBackup();

    // Verify manifest structure
    expect(fs.writeFileSync).toHaveBeenCalledWith(
      expect.stringContaining('backup-manifest.json'),
      expect.any(String)
    );

    // Get the actual manifest content
    const manifestCall = (fs.writeFileSync as unknown as jest.Mock).mock.calls.find(
      call => call[0].includes('backup-manifest.json')
    );
    const manifest = JSON.parse(manifestCall[1]);

    // Verify manifest structure
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
    });
  });
}); 