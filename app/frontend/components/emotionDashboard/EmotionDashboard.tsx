import React, { useEffect, useState } from 'react';
import { Box, Typography, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, TextField, CircularProgress } from '@mui/material';
import axios from 'axios';

interface Emotion {
    name: string;
    intensity: number;
    description?: string;
}

interface EntityEmotion {
    entityId: string;
    emotions: Emotion[];
}

const EmotionDashboard: React.FC = () => {
    const [entities, setEntities] = useState<EntityEmotion[]>([]);
    const [search, setSearch] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // TODO: Replace with real API call for all entities and their emotions
        axios.get('/api/emotions')
            .then(res => {
                // Assume response is { emotions: Array<Emotion> } for now
                setEntities([
                    { entityId: 'global', emotions: res.data.emotions }
                ]);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    }, []);

    const filteredEntities = entities.filter(e =>
        e.entityId.toLowerCase().includes(search.toLowerCase()) ||
        e.emotions.some(em => em.name.toLowerCase().includes(search.toLowerCase()))
    );

    return (
        <Box p={3}>
            <Typography variant="h4" gutterBottom>Emotion Dashboard</Typography>
            <TextField
                label="Search entities or emotions"
                value={search}
                onChange={e => setSearch(e.target.value)}
                fullWidth
                margin="normal"
            />
            {loading ? <CircularProgress /> : (
                <TableContainer component={Paper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>Entity</TableCell>
                                <TableCell>Emotions</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {filteredEntities.map(entity => (
                                <TableRow key={entity.entityId}>
                                    <TableCell>{entity.entityId}</TableCell>
                                    <TableCell>
                                        {entity.emotions.map(em => (
                                            <Box key={em.name} display="inline-block" mr={2}>
                                                <strong>{em.name}</strong> (Intensity: {em.intensity}){em.description ? ` - ${em.description}` : ''}
                                            </Box>
                                        ))}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            )}
        </Box>
    );
};

export default EmotionDashboard; 