from typing import Any, Dict, List, Union
from enum import Enum



class NPCEventType(Enum):
    INTERACTION = 'npc.interaction'
    AFFINITY_CHANGE = 'npc.affinity.change'
    RELATIONSHIP_CHANGE = 'npc.relationship.change'
class NPCEventBase:
    type: \'NPCEventType\'
    timestamp: float
    npcId: str
    targetId?: str
    context?: Dict[str, Any>
class NPCInteractionEvent:
    type: NPCEventType.INTERACTION
    interaction: NPCInteraction
class NPCAffinityChangeEvent:
    type: NPCEventType.AFFINITY_CHANGE
    affinity: NPCAffinity
    change: float
    before: NPCAffinity
    after: NPCAffinity
class NPCRelationshipChangeEvent:
    type: NPCEventType.RELATIONSHIP_CHANGE
    before: RelationshipType
    after: RelationshipType
    affinity: NPCAffinity
NPCEvent = Union[NPCInteractionEvent, NPCAffinityChangeEvent, NPCRelationshipChangeEvent]
/**
 * Service for structured logging of all NPC interactions and relationship/affinity changes.
 * Uses the shared Logger and supports JSON log format, log levels, and contextual metadata.
 * Log files are rotated daily, compressed, and retained for 30 days for analytics and auditing.
 */
class NPCEventLoggingService {
  private static instance: \'NPCEventLoggingService\'
  private logger: Logger
  private constructor() {
    this.logger = new Logger({
      level: LogLevel.INFO,
      transports: Dict[str, Any],
        },
      },
    })
  }
  /**
   * Get the singleton instance of the NPCEventLoggingService.
   */
  public static getInstance(): \'NPCEventLoggingService\' {
    if (!NPCEventLoggingService.instance) {
      NPCEventLoggingService.instance = new NPCEventLoggingService()
    }
    return NPCEventLoggingService.instance
  }
  /**
   * Log an NPC interaction event (dialogue, quest, combat, etc.).
   * @param npcId The acting NPC's ID
   * @param interaction The interaction details
   * @param context Optional contextual metadata (player, POI, quest, etc.)
   */
  public logInteraction(npcId: str, interaction: NPCInteraction, context?: Record<string, any>): void {
    const event: \'NPCInteractionEvent\' = {
      type: NPCEventType.INTERACTION,
      timestamp: Date.now(),
      npcId,
      targetId: interaction.targetId,
      interaction,
      context,
    }
    this.logger.info('NPC Interaction', event)
  }
  /**
   * Log an affinity score change between two NPCs.
   * @param npcId The acting NPC's ID
   * @param affinity The updated affinity object
   * @param change The change in affinity score
   * @param before The affinity state before the change
   * @param after The affinity state after the change
   * @param context Optional contextual metadata
   */
  public logAffinityChange(
    npcId: str,
    affinity: NPCAffinity,
    change: float,
    before: NPCAffinity,
    after: NPCAffinity,
    context?: Record<string, any>
  ): void {
    const event: \'NPCAffinityChangeEvent\' = {
      type: NPCEventType.AFFINITY_CHANGE,
      timestamp: Date.now(),
      npcId,
      targetId: affinity.npcId2,
      affinity,
      change,
      before,
      after,
      context,
    }
    this.logger.info('NPC Affinity Change', event)
  }
  /**
   * Log a relationship type transition between two NPCs.
   * @param npcId The acting NPC's ID
   * @param before The previous relationship type
   * @param after The new relationship type
   * @param affinity The current affinity object
   * @param context Optional contextual metadata
   */
  public logRelationshipChange(
    npcId: str,
    before: RelationshipType,
    after: RelationshipType,
    affinity: NPCAffinity,
    context?: Record<string, any>
  ): void {
    const event: \'NPCRelationshipChangeEvent\' = {
      type: NPCEventType.RELATIONSHIP_CHANGE,
      timestamp: Date.now(),
      npcId,
      targetId: affinity.npcId2,
      before,
      after,
      affinity,
      context,
    }
    this.logger.info('NPC Relationship Change', event)
  }
  /**
   * Set the log level for event logging.
   * @param level The desired log level
   */
  public setLogLevel(level: LogLevel): void {
    this.logger.setLevel(level)
  }
  /**
   * Export all NPC event logs (including rotated/compressed) to a specified directory for analytics.
   * @param exportDir The directory to copy all log files to
   */
  public exportLogsToFile(exportDir: str): void {
    const logDir = path.dirname('npc-events.log')
    const logBase = 'npc-events'
    if (!fs.existsSync(exportDir)) {
      fs.mkdirSync(exportDir, { recursive: true })
    }
    const files = fs.readdirSync(logDir).filter(f =>
      f.startsWith(logBase) && (f.endsWith('.log') || f.endsWith('.log.gz'))
    )
    for (const file of files) {
      const src = path.join(logDir, file)
      const dest = path.join(exportDir, file)
      fs.copyFileSync(src, dest)
    }
  }
  /**
   * Log a batch of NPC events in a single operation for performance.
   * @param events Array of NPCEvent objects to log
   */
  public logBatch(events: List[NPCEvent]): void {
    for (const event of events) {
      this.logger.info('NPC Batch Event', event)
    }
  }
  /**
   * Check the health of the logging system (writability, disk space, etc).
   * @returns An object with status and details
   */
  public checkHealth(): { status: 'ok' | 'error'; details: str } {
    try {
      const logDir = path.dirname('npc-events.log')
      if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true })
      }
      const testFile = path.join(logDir, 'healthcheck.tmp')
      fs.writeFileSync(testFile, 'test')
      fs.unlinkSync(testFile)
      return { status: 'ok', details: 'Log directory is writable.' }
    } catch (err: Any) {
      return { status: 'error', details: err.message }
    }
  }
} 