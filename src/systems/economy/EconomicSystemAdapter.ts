import { EventBus, EventPriority } from '../../core/events/EventBus';
import { SceneEventType, ISceneEvent } from '../../core/events/SceneEventTypes';
import { EconomicAgentSystem } from './EconomicAgentSystem';
import { UnifiedApiGateway, EconomyApi } from '../../core/services/UnifiedApiGateway';
import { TransactionEvent } from '../../core/events/SceneEventTypes';
import { ValidationService, ValidationContext } from '../../core/services/ValidationService';

export class EconomicSystemAdapter implements EconomyApi {
    private economicSystem: EconomicAgentSystem;
    private eventBus: EventBus;
    private static instance: EconomicSystemAdapter;
    private apiGateway: UnifiedApiGateway;

    private constructor(economicSystem: EconomicAgentSystem) {
        this.economicSystem = economicSystem;
        this.eventBus = EventBus.getInstance();
        this.apiGateway = UnifiedApiGateway.getInstance();
        this.registerEventHandlers();
    }

    public static getInstance(economicSystem: EconomicAgentSystem): EconomicSystemAdapter {
        if (!EconomicSystemAdapter.instance) {
            EconomicSystemAdapter.instance = new EconomicSystemAdapter(economicSystem);
        }
        return EconomicSystemAdapter.instance;
    }

    // Register event handlers using eventBus.on
    private registerEventHandlers() {
        this.eventBus.on(
            SceneEventType.TRANSACTION_COMPLETED,
            this.handleTransactionCompleted.bind(this),
            { priority: EventPriority.NORMAL }
        );
        // Register other event types as needed
    }

    // Handler for transaction completed events
    private async handleTransactionCompleted(event: ISceneEvent) {
        // Implement logic to update system state based on transaction event
    }

    // EconomyApi implementation
    public async getBalance(agentId: string): Promise<number> {
        const agent = (this.economicSystem as any).agents?.get(agentId);
        if (agent && typeof agent.currency === 'number') {
            return agent.currency;
        }
        throw new Error('Agent not found or missing currency');
    }
    public async transferFunds(fromAgentId: string, toAgentId: string, amount: number): Promise<boolean> {
        const agents = (this.economicSystem as any).agents;
        const fromAgent = agents?.get(fromAgentId);
        const toAgent = agents?.get(toAgentId);
        const validationService = ValidationService.getInstance();
        // Pre-operation validation
        const preContext = await validationService.validateAsync('economic', { fromAgentId, toAgentId, amount, fromAgent, toAgent });
        if (preContext.errors.length > 0) {
            // Optionally emit validation event here
            throw new Error('Validation failed before transfer: ' + preContext.errors.join('; '));
        }
        if (fromAgent && toAgent && typeof fromAgent.currency === 'number' && typeof toAgent.currency === 'number') {
            if (fromAgent.currency >= amount) {
                fromAgent.currency -= amount;
                toAgent.currency += amount;
                // Post-operation validation
                const postContext = await validationService.validateAsync('economic', { fromAgentId, toAgentId, amount, fromAgent, toAgent });
                if (postContext.errors.length > 0) {
                    // Optionally emit validation event here
                    // Rollback (simple example)
                    fromAgent.currency += amount;
                    toAgent.currency -= amount;
                    throw new Error('Validation failed after transfer: ' + postContext.errors.join('; '));
                }
                const event: TransactionEvent = {
                    type: SceneEventType.TRANSACTION_COMPLETED,
                    transactionType: 'transfer',
                    amount,
                    fromAgentId,
                    toAgentId,
                    source: 'EconomicSystemAdapter',
                    timestamp: Date.now(),
                };
                await this.eventBus.emit(event);
                return true;
            }
        }
        return false;
    }
    public async getTransactionHistory(agentId: string): Promise<any[]> {
        // No transaction history implemented; return empty array or add TODO
        return [];
    }
} 