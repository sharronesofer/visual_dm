// Minimal test for AssetIndexLoader (CommonJS style for ts-node compatibility)
const Loader = require('./AssetIndexLoader');

(async () => {
  try {
    await Loader.load();
    const index = Loader.getIndex();
    console.log('Asset index loaded successfully. Version:', index.version);
    process.exit(0);
  } catch (err) {
    console.error('AssetIndexLoader test failed:', err);
    process.exit(1);
  }
})();
