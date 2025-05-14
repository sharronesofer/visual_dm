import express from 'express';
import logRoutes from '../../core/logs/routes/logRoutes';

/**
 * Registers RBAC-enabled log access routes with tamper-proof audit trails
 * @param app Express application instance
 */
export function registerLogRoutes(app: express.Application): void {
    // Register the log routes under /api/logs
    app.use('/api/logs', logRoutes);

    console.log('RBAC log routes registered at /api/logs');
}

export default { registerLogRoutes }; 