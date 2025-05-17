// HardwareProfiler.ts
// Hardware detection and profiling for LOD and performance-aware systems

export interface HardwareProfile {
    gpuVendor: string;
    gpuModel: string;
    vramMB: number;
    shaderModel: string;
    cpuCores: number;
    deviceType: 'desktop' | 'laptop' | 'mobile' | 'server' | 'unknown';
    score: number; // Calculated performance score
    timestamp: number;
}

export interface PerformanceMetrics {
    frameTime: number;
    memoryUsage: number;
    gpuUtilization?: number;
}

export type HardwareTier = 'ultra' | 'high' | 'medium' | 'low' | 'verylow';

export class HardwareProfiler {
    private static instance: HardwareProfiler;
    private profile: HardwareProfile | null = null;
    private metrics: PerformanceMetrics = { frameTime: 0, memoryUsage: 0 };
    private listeners: Array<(metrics: PerformanceMetrics) => void> = [];

    private constructor() { }

    public static getInstance(): HardwareProfiler {
        if (!HardwareProfiler.instance) {
            HardwareProfiler.instance = new HardwareProfiler();
        }
        return HardwareProfiler.instance;
    }

    // Detect hardware profile (async, platform-specific)
    public async detectHardwareProfile(): Promise<HardwareProfile> {
        // TODO: Implement platform-specific detection
        // - Browser: Use WebGL/WebGPU APIs
        // - Node.js: Use os, process, and optional native modules
        // - Fallback: Use user agent or default values
        // Example stub:
        const profile: HardwareProfile = {
            gpuVendor: 'Unknown',
            gpuModel: 'Unknown',
            vramMB: 0,
            shaderModel: 'Unknown',
            cpuCores: 1,
            deviceType: 'unknown',
            score: 1000,
            timestamp: Date.now(),
        };
        this.profile = profile;
        await this.saveProfile(profile);
        return profile;
    }

    // Get cached or detected hardware profile
    public async getHardwareProfile(): Promise<HardwareProfile> {
        if (this.profile) return this.profile;
        const cached = await this.loadProfile();
        if (cached) {
            this.profile = cached;
            return cached;
        }
        return this.detectHardwareProfile();
    }

    // Save profile to persistent storage
    private async saveProfile(profile: HardwareProfile): Promise<void> {
        // TODO: Implement platform-specific storage
        // - Browser: localStorage/IndexedDB
        // - Node.js: file system
        // Example stub:
        if (typeof window !== 'undefined' && window.localStorage) {
            window.localStorage.setItem('hardwareProfile', JSON.stringify(profile));
        }
        // else: implement Node.js file storage
    }

    // Load profile from persistent storage
    private async loadProfile(): Promise<HardwareProfile | null> {
        // TODO: Implement platform-specific storage
        if (typeof window !== 'undefined' && window.localStorage) {
            const raw = window.localStorage.getItem('hardwareProfile');
            if (raw) {
                try {
                    return JSON.parse(raw) as HardwareProfile;
                } catch {
                    return null;
                }
            }
        }
        // else: implement Node.js file storage
        return null;
    }

    // Update runtime performance metrics
    public updateMetrics(metrics: PerformanceMetrics) {
        this.metrics = metrics;
        this.listeners.forEach(fn => fn(metrics));
    }

    // Subscribe to metric updates
    public onMetricsUpdate(fn: (metrics: PerformanceMetrics) => void) {
        this.listeners.push(fn);
    }

    // Get current metrics
    public getCurrentMetrics(): PerformanceMetrics {
        return this.metrics;
    }

    // Score hardware profile for tiering
    public static scoreProfile(profile: HardwareProfile): number {
        // TODO: Implement a real scoring algorithm
        // Example: weighted sum of VRAM, CPU cores, etc.
        let score = 0;
        score += profile.vramMB * 2;
        score += profile.cpuCores * 100;
        // ... add more factors
        return score;
    }

    // Categorize hardware into a tier
    public static getTier(profile: HardwareProfile): HardwareTier {
        const score = HardwareProfiler.scoreProfile(profile);
        if (score >= 8000) return 'ultra';
        if (score >= 4000) return 'high';
        if (score >= 2000) return 'medium';
        if (score >= 1000) return 'low';
        return 'verylow';
    }
}

// --- UNIT TEST STUBS (to be implemented) ---
// describe('HardwareProfiler', () => {
//   it('should detect and store hardware profile', async () => {
//     // TODO: Mock detection and storage
//   });
//   it('should emit metric updates', () => {
//     // TODO: Test event system
//   });
// }); 