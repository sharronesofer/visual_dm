import React, { useEffect, useState } from 'react';
import { ReputationManager } from '../../managers/ReputationManager';

export const ReputationPanel: React.FC = () => {
    const [reputations, setReputations] = useState([]);

    useEffect(() => {
        const manager = ReputationManager.getInstance();
        setReputations(manager.getAllReputations());
        // TODO: Subscribe to reputation change events for live updates
    }, []);

    return (
        <div className="reputation-panel">
            <h2>Faction Reputation</h2>
            <table>
                <thead>
                    <tr>
                        <th>Faction</th>
                        <th>Moral Standing</th>
                        <th>Fame</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {reputations.map((rep: any) => (
                        <tr key={rep.factionId}>
                            <td>{rep.factionId}</td>
                            <td>{rep.moral}</td>
                            <td>{rep.fame}</td>
                            <td>{getStatus(rep.moral, rep.fame)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            {/* TODO: Add reputation history visualization and notifications */}
        </div>
    );
};

function getStatus(moral: number, fame: number): string {
    if (moral > 50 && fame > 50) return 'Heroic & Famous';
    if (moral < -50 && fame > 50) return 'Infamous Villain';
    if (moral > 0) return 'Respected';
    if (moral < 0) return 'Distrusted';
    return 'Neutral';
} 