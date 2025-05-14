from typing import Any, List


const args = process.argv.slice(2)
const config = {
  type: args[0] || 'dungeon',
  size: args[1] || 'large',
  theme: args[2] || 'medieval',
  complexity: parseFloat(args[3] || '0.7'),
  runs: parseInt(args[4] || '10', 10),
  seed: args[5] || 'benchmark-seed'
}
async function runBenchmark(cfg = config) {
  const times: List[number] = []
  const memories: List[number] = []
  for (let i = 0; i < cfg.runs; i++) {
    const rng = seedrandom(cfg.seed + '-' + i)
    let idCounter = 0
    const deterministicIdGen = () => `id-${i}-${idCounter++}`
    const fixedNow = () => '2020-01-01T00:00:00.000Z'
    const DeterministicPOIGenerationService = (POIGenerationService as any)
    const service = new DeterministicPOIGenerationService(
      () => rng(),
      deterministicIdGen,
      fixedNow
    )
    const params = {
      type: cfg.type,
      size: cfg.size,
      theme: cfg.theme,
      complexity: cfg.complexity,
      seed: cfg.seed + '-' + i
    }
    const memStart = process.memoryUsage().heapUsed
    const t0 = performance.now()
    await service.generatePOI(params)
    const t1 = performance.now()
    const memEnd = process.memoryUsage().heapUsed
    times.push(t1 - t0)
    memories.push(memEnd - memStart)
  }
  const result = {
    config: cfg,
    avgTimeMs: times.reduce((a, b) => a + b, 0) / times.length,
    maxTimeMs: Math.max(...times),
    minTimeMs: Math.min(...times),
    avgMemBytes: memories.reduce((a, b) => a + b, 0) / memories.length,
    maxMemBytes: Math.max(...memories),
    minMemBytes: Math.min(...memories),
    times,
    memories
  }
  fs.writeFileSync(path.join(process.cwd(), 'benchmark-results.json'), JSON.stringify(result, null, 2))
  console.log(JSON.stringify(result, null, 2))
  return result
}
if (require.main === module) {
  runBenchmark()
}