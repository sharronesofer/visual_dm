from typing import Any



const Loader = require('./AssetIndexLoader')
(async () => {
  try {
    await Loader.load()
    const index = Loader.getIndex()
    console.log('Asset index loaded successfully. Version:', index.version)
    process.exit(0)
  } catch (err) {
    console.error('AssetIndexLoader test failed:', err)
    process.exit(1)
  }
})()