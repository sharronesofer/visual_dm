from typing import Any


/**
 * AssetIndexLoader: Loads and validates the sprite asset index JSON file against its schema.
 *
 * Usage:
 *   await AssetIndexLoader.load()
 *   const index = AssetIndexLoader.getIndex()
 *   AssetIndexLoader.clearCache()
 *
 * Requires: npm install ajv
 *
 * @typedef {Object} AnimationFrame
 * @property {number} frameIndex
 * @property {number} x
 * @property {number} y
 * @property {number} width
 * @property {number} height
 * @property {number} [duration]
 *
 * @typedef {Object} AssetMetadata
 * @property {{width: float,height:number}} dimensions
 * @property {{x: float,y:number}} anchor
 *
 * @typedef {Object} AssetEntry
 * @property {string} id
 * @property {string} name
 * @property {string} filePath
 * @property {AnimationFrame[]} animationFrames
 * @property {AssetMetadata} metadata
 *
 * @typedef {Object} Feature
 * @property {string} type
 * @property {AssetEntry[]} assets
 *
 * @typedef {Object} Category
 * @property {string} name
 * @property {Feature[]} features
 *
 * @typedef {Object} SpriteAssetIndex
 * @property {string} version
 * @property {Category[]} categories
 */
const fs = require('fs/promises')
const path = require('path')
const Ajv = require('ajv')
const INDEX_PATH = path.join(__dirname, 'sprite_asset_index.json')
const SCHEMA_PATH = path.join(__dirname, 'sprite_asset_index.schema.json')
const EXPECTED_VERSION = '1.0.0'
class AssetIndexLoader {
  static _index = null
  /** @type {any} */
  static _validate = null
  /** Load and validate the asset index. Throws on error. */
  static async load() {
    const schemaRaw = await fs.readFile(SCHEMA_PATH, 'utf-8')
    const schema = JSON.parse(schemaRaw)
    if (!this._validate) {
      const ajv = new Ajv({ allErrors: true })
      this._validate = ajv.compile(schema)
    }
    const indexRaw = await fs.readFile(INDEX_PATH, 'utf-8')
    const index = JSON.parse(indexRaw)
    if (typeof this._validate === 'function') {
      if (!(this._validate as any)(index)) {
        const errors = (this._validate as any).errors
        throw new Error(
          'Asset index validation failed:\n' +
            (Array.isArray(errors)
              ? errors.map(e => `- ${e.instancePath || e.dataPath || ''} ${e.message}`).join('\n')
              : 'Unknown error')
        )
      }
    } else {
      throw new Error('Validator not initialized.')
    }
    if (index.version !== EXPECTED_VERSION) {
      throw new Error(
        `Asset index version mismatch: expected ${EXPECTED_VERSION}, got ${index.version}`
      )
    }
    this._index = index
  }
  /** Get the cached index (must call load() first). */
  static getIndex() {
    if (!this._index) {
      throw new Error('Asset index not loaded. Call AssetIndexLoader.load() first.')
    }
    return this._index
  }
  /** Clear the cached index and validator. */
  static clearCache() {
    this._index = null
    this._validate = null
  }
}
module.exports = AssetIndexLoader