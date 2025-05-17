module.exports = {
    require: [
        'ts-node/register'
    ],
    extension: ['ts'],
    spec: 'src/**/*.test.ts',
    loader: 'ts-node/esm',
    timeout: 5000,
}; 