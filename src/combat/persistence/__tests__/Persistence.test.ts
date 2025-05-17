import { expect } from 'chai';
import { StateSerializer } from '../StateSerializer';
import { AutoSaveManager } from '../AutoSaveManager';
import { RecoveryManager } from '../RecoveryManager';
import { SaveLoadManager } from '../SaveLoadManager';
import { StateVersioning } from '../StateVersioning';

describe('Persistence System', () => {
    it('serializes and deserializes state', () => {
        const state = { a: 1, b: [2, 3] };
        const data = StateSerializer.serialize(state);
        const restored = StateSerializer.deserialize<typeof state>(data);
        expect(restored.a).to.equal(1);
        expect(restored.b[1]).to.equal(3);
    });

    it('auto-saves and retains saves', () => {
        const mgr = new AutoSaveManager(1, 2);
        mgr.onTurnStart({ foo: 1 });
        mgr.onTurnStart({ foo: 2 });
        mgr.onTurnStart({ foo: 3 });
        const saves = mgr.getAllSaves();
        expect(saves.length).to.equal(2);
    });

    it('recovers from latest save', () => {
        const mgr = new AutoSaveManager(1, 2);
        mgr.save({ bar: 42 });
        const rec = new RecoveryManager(mgr);
        const state = rec.recover();
        expect(state?.bar).to.equal(42);
    });

    it('manually saves and loads', () => {
        const mgr = new SaveLoadManager('1.0.0');
        mgr.save({ x: 5 }, 'test save');
        const loaded = mgr.load(0);
        expect(loaded?.x).to.equal(5);
        const files = mgr.getSaveFiles();
        expect(files[0].summary).to.equal('test save');
    });

    it('tags and migrates state versions', () => {
        const state = { foo: 'bar' };
        const tagged = StateVersioning.tagVersion(state);
        expect(tagged.__version).to.equal('1.0.0');
        expect(StateVersioning.isCompatible('1.0.0')).to.equal(true);
        expect(StateVersioning.migrate(tagged, '1.0.0').foo).to.equal('bar');
    });
}); 