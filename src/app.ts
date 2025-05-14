import logRoutes from './core/logs/routes/logRoutes';

// Register routes
app.use('/api', apiRoutes);
app.use('/api/logs', logRoutes); 