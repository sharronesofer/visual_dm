import { WeatherPerformanceMonitor } from '../core/performance/WeatherPerformanceMonitor';
import { WeatherEffectSystem } from './WeatherEffectSystem';

/**
 * WeatherPerformanceVisualizer: Developer tool for real-time weather system performance visualization.
 * - Real-time line graphs for frame time, memory, GPU usage
 * - Color-coded overlays for weather effects
 * - Timeline and heatmap views
 * - CSV export for offline analysis
 * - Toggleable visualization modes
 */
export class WeatherPerformanceVisualizer {
    private monitor: WeatherPerformanceMonitor;
    private effectSystem: WeatherEffectSystem;
    private canvas: HTMLCanvasElement;
    private ctx: CanvasRenderingContext2D;
    private mode: 'graph' | 'overlay' | 'heatmap' | 'timeline' = 'graph';
    private history: any[] = [];
    private maxHistory: number = 300;
    private overlayEnabled: boolean = false;
    private heatmapEnabled: boolean = false;
    private timelineEnabled: boolean = false;

    constructor(monitor: WeatherPerformanceMonitor, effectSystem: WeatherEffectSystem, canvas?: HTMLCanvasElement) {
        this.monitor = monitor;
        this.effectSystem = effectSystem;
        this.canvas = canvas || document.createElement('canvas');
        this.ctx = this.canvas.getContext('2d')!;
        // Optionally, attach to DOM or debug UI
        this.start();
    }

    /** Start collecting and rendering performance data */
    public start() {
        this.history = [];
        setInterval(() => {
            const data = this.monitor.getCurrentMetrics();
            if (data) {
                this.history.push(data);
                if (this.history.length > this.maxHistory) this.history.shift();
                this.render();
            }
        }, 100); // Poll every 100ms (adjust as needed)
    }

    /** Render the current visualization mode */
    public render() {
        switch (this.mode) {
            case 'graph':
                this.renderGraphs();
                break;
            case 'overlay':
                this.renderOverlay();
                break;
            case 'heatmap':
                this.renderHeatmap();
                break;
            case 'timeline':
                this.renderTimeline();
                break;
        }
    }

    /** Render real-time line graphs for key metrics */
    private renderGraphs() {
        // Stub: Draw frame time, memory, GPU usage as line graphs
        // Use this.history for data
        // Use this.ctx for drawing
    }

    /** Render color-coded overlays on weather effects */
    private renderOverlay() {
        // Stub: Draw overlays on active weather effects based on resource usage
        // Use this.effectSystem.state.activeEffects
    }

    /** Render heatmap for spatial distribution of effect costs */
    private renderHeatmap() {
        // Stub: Draw heatmap using effect positions and cost data
    }

    /** Render timeline view of recent performance history */
    private renderTimeline() {
        // Stub: Draw scrollable, zoomable timeline of performance data
    }

    /** Export performance data as CSV */
    public exportCSV(): string {
        const keys = Object.keys(this.history[0] || {});
        const rows = this.history.map(row => keys.map(k => row[k]).join(','));
        return [keys.join(','), ...rows].join('\n');
    }

    /** Toggle visualization modes */
    public setMode(mode: 'graph' | 'overlay' | 'heatmap' | 'timeline') {
        this.mode = mode;
        this.render();
    }

    /** Enable or disable overlays */
    public toggleOverlay(enabled?: boolean) {
        this.overlayEnabled = enabled !== undefined ? enabled : !this.overlayEnabled;
        if (this.overlayEnabled) this.setMode('overlay');
    }

    /** Enable or disable heatmap */
    public toggleHeatmap(enabled?: boolean) {
        this.heatmapEnabled = enabled !== undefined ? enabled : !this.heatmapEnabled;
        if (this.heatmapEnabled) this.setMode('heatmap');
    }

    /** Enable or disable timeline view */
    public toggleTimeline(enabled?: boolean) {
        this.timelineEnabled = enabled !== undefined ? enabled : !this.timelineEnabled;
        if (this.timelineEnabled) this.setMode('timeline');
    }

    /** Attach the visualizer canvas to a DOM element (for web/debug UI) */
    public attachTo(element: HTMLElement) {
        element.appendChild(this.canvas);
    }

    /** Detach the visualizer canvas from its parent */
    public detach() {
        if (this.canvas.parentElement) {
            this.canvas.parentElement.removeChild(this.canvas);
        }
    }
} 