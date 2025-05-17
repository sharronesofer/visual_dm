import { ValidationPipeline } from '../ValidationPipeline';
import { AttackValidator, AttackAction, CombatState as AttackState } from '../validators/AttackValidator';
import { SpellValidator, SpellAction, CombatState as SpellState } from '../validators/SpellValidator';
import { MovementValidator, MovementAction, CombatState as MoveState } from '../validators/MovementValidator';
import { ValidationResult } from '../ValidationResult';
import { expect } from 'chai';

describe('ValidationPipeline', () => {
    it('runs only applicable validators and combines results', () => {
        const pipeline = new ValidationPipeline();
        pipeline.register(new AttackValidator());
        pipeline.register(new SpellValidator());
        pipeline.register(new MovementValidator());

        const attackAction: AttackAction = {
            type: 'attack',
            attackerId: 'a1',
            targetId: 't1',
            weaponId: 'w1',
        };
        const combatState: AttackState = {};

        const result = pipeline.preValidate(attackAction, combatState);
        expect(result.success).to.equal(true);
        expect(result.messages.length).to.equal(0);
    });

    it('returns failure if any validator fails', () => {
        // Custom validator that always fails
        const failValidator = {
            isApplicable: () => true,
            preValidate: () => ValidationResult.fail('fail', 'ERR'),
            postValidate: () => ValidationResult.ok(),
        };
        const pipeline = new ValidationPipeline();
        pipeline.register(failValidator);
        const action = { type: 'any' };
        const state = {};
        const result = pipeline.preValidate(action, state);
        expect(result.success).to.equal(false);
        expect(result.messages).to.include('fail');
    });
}); 