import { performance } from 'perf_hooks';
import { performanceThresholds } from '../animation/medieval/utils';

// Extend Performance interface to include memory property
interface ExtendedPerformance extends Performance {
  memory?: {
    usedJSHeapSize: number;
    totalJSHeapSize: number;
    jsHeapSizeLimit: number;
  };
}

export interface PerformanceTestResult {
  component: string;
  renderTime: number;
  fps: number;
  memoryUsage: number | null;
  layoutShifts: number;
  longTasks: number;
  score: number;
  issues: string[];
}

export interface PerformanceTestOptions {
  duration?: number;
  iterations?: number;
  deviceProfile?: 'mobile' | 'tablet' | 'desktop';
  connection?: 'slow-3g' | '4g' | 'wifi';
}

const deviceProfiles = {
  mobile: {
    viewport: { width: 375, height: 667 },
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)',
    deviceMemory: 2,
  },
  tablet: {
    viewport: { width: 768, height: 1024 },
    userAgent: 'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X)',
    deviceMemory: 4,
  },
  desktop: {
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    deviceMemory: 8,
  },
};

const connectionProfiles = {
  'slow-3g': {
    downloadThroughput: 500000, // 500kb/s
    uploadThroughput: 500000,   // 500kb/s
    latency: 100,               // 100ms
  },
  '4g': {
    downloadThroughput: 4000000, // 4mb/s
    uploadThroughput: 2000000,   // 2mb/s
    latency: 20,                 // 20ms
  },
  'wifi': {
    downloadThroughput: 20000000, // 20mb/s
    uploadThroughput: 10000000,   // 10mb/s
    latency: 5,                   // 5ms
  },
};

export interface PerformanceMetrics {
  renderTime: number;
  fps: number;
  memoryUsage: number;
  interactionLatency: number;
  loadTime: number;
}

export interface PerformanceThresholds {
  maxRenderTime: number;
  minFps: number;
  maxMemoryUsage: number;
  maxInteractionLatency: number;
  maxLoadTime: number;
}

export interface DeviceProfile {
  name: string;
  viewport: {
    width: number;
    height: number;
  };
  devicePixelRatio: number;
  connection: {
    type: 'slow-2g' | '2g' | '3g' | '4g';
    downlink: number;
    rtt: number;
  };
}

const DEFAULT_THRESHOLDS: PerformanceThresholds = {
  maxRenderTime: 100, // ms
  minFps: 30,
  maxMemoryUsage: 50 * 1024 * 1024, // 50MB
  maxInteractionLatency: 100, // ms
  maxLoadTime: 3000, // ms
};

export class PerformanceTester {
  private metrics: PerformanceMetrics = {
    renderTime: 0,
    fps: 0,
    memoryUsage: 0,
    interactionLatency: 0,
    loadTime: 0,
  };

  private fpsHistory: number[] = [];
  private lastFrameTime: number = 0;
  private frameCount: number = 0;
  private startTime: number = 0;
  private thresholds: PerformanceThresholds;

  constructor(thresholds: Partial<PerformanceThresholds> = {}) {
    this.thresholds = { ...DEFAULT_THRESHOLDS, ...thresholds };
  }

  public startTest(): void {
    this.startTime = performance.now();
    this.lastFrameTime = this.startTime;
    this.frameCount = 0;
    this.fpsHistory = [];
    this.metrics = {
      renderTime: 0,
      fps: 0,
      memoryUsage: 0,
      interactionLatency: 0,
      loadTime: 0,
    };
  }

  public recordFrame(): void {
    const now = performance.now();
    const frameDuration = now - this.lastFrameTime;
    const fps = 1000 / frameDuration;

    this.fpsHistory.push(fps);
    if (this.fpsHistory.length > 60) {
      this.fpsHistory.shift();
    }

    this.frameCount++;
    this.lastFrameTime = now;
    this.metrics.fps = this.fpsHistory.reduce((a, b) => a + b, 0) / this.fpsHistory.length;
  }

  public recordRenderTime(callback: () => void): number {
    const start = performance.now();
    callback();
    const duration = performance.now() - start;
    this.metrics.renderTime = duration;
    return duration;
  }

  public recordInteractionLatency(callback: () => void): number {
    const start = performance.now();
    callback();
    const duration = performance.now() - start;
    this.metrics.interactionLatency = duration;
    return duration;
  }

  public recordLoadTime(): void {
    this.metrics.loadTime = performance.now() - this.startTime;
  }

  public recordMemoryUsage(): void {
    if (typeof window !== 'undefined') {
      const perf = window.performance as ExtendedPerformance;
      if (perf?.memory) {
        this.metrics.memoryUsage = perf.memory.usedJSHeapSize;
      }
    }
  }

  public getMetrics(): PerformanceMetrics {
    return { ...this.metrics };
  }

  public checkThresholds(): { passed: boolean; violations: string[] } {
    const violations: string[] = [];

    if (this.metrics.renderTime > this.thresholds.maxRenderTime) {
      violations.push(`Render time (${this.metrics.renderTime}ms) exceeds threshold (${this.thresholds.maxRenderTime}ms)`);
    }

    if (this.metrics.fps < this.thresholds.minFps) {
      violations.push(`FPS (${this.metrics.fps}) below threshold (${this.thresholds.minFps})`);
    }

    if (this.metrics.memoryUsage > this.thresholds.maxMemoryUsage) {
      violations.push(`Memory usage (${this.metrics.memoryUsage}B) exceeds threshold (${this.thresholds.maxMemoryUsage}B)`);
    }

    if (this.metrics.interactionLatency > this.thresholds.maxInteractionLatency) {
      violations.push(`Interaction latency (${this.metrics.interactionLatency}ms) exceeds threshold (${this.thresholds.maxInteractionLatency}ms)`);
    }

    if (this.metrics.loadTime > this.thresholds.maxLoadTime) {
      violations.push(`Load time (${this.metrics.loadTime}ms) exceeds threshold (${this.thresholds.maxLoadTime}ms)`);
    }

    return {
      passed: violations.length === 0,
      violations,
    };
  }

  public simulateDeviceProfile(profile: DeviceProfile): void {
    if (typeof window !== 'undefined') {
      // Set viewport
      const viewport = document.querySelector('meta[name="viewport"]');
      if (viewport) {
        viewport.setAttribute('content', `width=${profile.viewport.width}, initial-scale=${1/profile.devicePixelRatio}`);
      }

      // Simulate network conditions using the Network Information API
      if ('connection' in navigator) {
        Object.defineProperty(navigator, 'connection', {
          value: {
            effectiveType: profile.connection.type,
            downlink: profile.connection.downlink,
            rtt: profile.connection.rtt,
          },
        });
      }
    }
  }
}

/**
 * Measures component render performance
 */
export const measureComponentPerformance = async (
  component: string,
  options: PerformanceTestOptions = {}
): Promise<PerformanceTestResult> => {
  const {
    duration = 5000,
    iterations = 3,
    deviceProfile = 'desktop',
    connection = 'wifi',
  } = options;

  const issues: string[] = [];
  let totalRenderTime = 0;
  let totalFps = 0;
  let totalLayoutShifts = 0;
  let totalLongTasks = 0;

  // Simulate device conditions
  if (typeof window !== 'undefined') {
    Object.defineProperty(window.navigator, 'userAgent', {
      value: deviceProfiles[deviceProfile].userAgent,
      configurable: true,
    });
  }

  // Run performance measurements
  for (let i = 0; i < iterations; i++) {
    const startTime = performance.now();
    const frames: number[] = [];
    let layoutShifts = 0;
    let longTasks = 0;

    // Create PerformanceObserver for layout shifts
    const layoutObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.entryType === 'layout-shift') {
          layoutShifts++;
        }
      }
    });
    layoutObserver.observe({ entryTypes: ['layout-shift'] });

    // Create PerformanceObserver for long tasks
    const longTaskObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.duration > 50) { // Tasks longer than 50ms
          longTasks++;
        }
      }
    });
    longTaskObserver.observe({ entryTypes: ['longtask'] });

    // Measure FPS
    const measureFps = () => {
      frames.push(performance.now());
      requestAnimationFrame(measureFps);
    };
    requestAnimationFrame(measureFps);

    // Wait for test duration
    await new Promise(resolve => setTimeout(resolve, duration));

    // Calculate metrics
    const endTime = performance.now();
    const renderTime = endTime - startTime;
    const fps = (frames.length / (duration / 1000));

    // Cleanup observers
    layoutObserver.disconnect();
    longTaskObserver.disconnect();

    // Accumulate results
    totalRenderTime += renderTime;
    totalFps += fps;
    totalLayoutShifts += layoutShifts;
    totalLongTasks += longTasks;

    // Check for issues
    if (fps < performanceThresholds.minFps) {
      issues.push(`Low FPS detected: ${fps.toFixed(1)} FPS (minimum: ${performanceThresholds.minFps})`);
    }
    if (layoutShifts > 0) {
      issues.push(`${layoutShifts} layout shifts detected`);
    }
    if (longTasks > 0) {
      issues.push(`${longTasks} long tasks detected (>50ms)`);
    }
  }

  // Calculate averages
  const avgRenderTime = totalRenderTime / iterations;
  const avgFps = totalFps / iterations;
  const avgLayoutShifts = totalLayoutShifts / iterations;
  const avgLongTasks = totalLongTasks / iterations;

  // Calculate performance score (0-100)
  const fpsScore = Math.min(100, (avgFps / performanceThresholds.targetFps) * 100);
  const layoutScore = Math.max(0, 100 - (avgLayoutShifts * 10));
  const taskScore = Math.max(0, 100 - (avgLongTasks * 20));
  const renderScore = Math.max(0, 100 - (avgRenderTime / 100));
  const score = Math.round((fpsScore + layoutScore + taskScore + renderScore) / 4);

  // Get memory usage if available
  let memoryUsage: number | null = null;
  if ((performance as ExtendedPerformance).memory) {
    memoryUsage = (performance as ExtendedPerformance).memory!.usedJSHeapSize / (1024 * 1024); // MB
  }

  return {
    component,
    renderTime: avgRenderTime,
    fps: avgFps,
    memoryUsage,
    layoutShifts: avgLayoutShifts,
    longTasks: avgLongTasks,
    score,
    issues,
  };
};

/**
 * Tests accessibility of medieval UI components
 */
export const testAccessibility = async (component: string): Promise<{
  issues: string[];
  score: number;
}> => {
  const issues: string[] = [];
  let score = 100;

  // Check color contrast
  const checkColorContrast = () => {
    const elements = document.querySelectorAll(`${component} *`);
    elements.forEach(el => {
      const style = window.getComputedStyle(el);
      const backgroundColor = style.backgroundColor;
      const color = style.color;
      // TODO: Implement color contrast calculation
      // For now, just checking if colors are defined
      if (!backgroundColor || !color) {
        issues.push(`Missing color or background-color in element: ${el.tagName}`);
        score -= 5;
      }
    });
  };

  // Check interactive element sizes
  const checkInteractiveElements = () => {
    const interactiveElements = document.querySelectorAll(
      `${component} button, ${component} a, ${component} input, ${component} select`
    );
    interactiveElements.forEach(el => {
      const rect = el.getBoundingClientRect();
      if (rect.width < 44 || rect.height < 44) {
        issues.push(`Interactive element too small: ${el.tagName} (${rect.width}x${rect.height}px)`);
        score -= 5;
      }
    });
  };

  // Check ARIA attributes
  const checkAriaAttributes = () => {
    const elements = document.querySelectorAll(`${component} [role]`);
    elements.forEach(el => {
      const role = el.getAttribute('role');
      if (role && !['button', 'link', 'heading', 'navigation'].includes(role)) {
        issues.push(`Invalid ARIA role: ${role}`);
        score -= 5;
      }
    });
  };

  // Check heading hierarchy
  const checkHeadingHierarchy = () => {
    const headings = document.querySelectorAll(`${component} h1, ${component} h2, ${component} h3, ${component} h4, ${component} h5, ${component} h6`);
    let lastLevel = 0;
    headings.forEach(heading => {
      const level = parseInt(heading.tagName.charAt(1));
      if (level - lastLevel > 1) {
        issues.push(`Skipped heading level: from h${lastLevel} to h${level}`);
        score -= 5;
      }
      lastLevel = level;
    });
  };

  // Run checks
  try {
    checkColorContrast();
    checkInteractiveElements();
    checkAriaAttributes();
    checkHeadingHierarchy();
  } catch (error) {
    issues.push(`Error running accessibility tests: ${error}`);
    score = 0;
  }

  return {
    issues,
    score: Math.max(0, score),
  };
};

/**
 * Generates a comprehensive performance and accessibility report
 */
export const generateReport = async (
  component: string,
  options?: PerformanceTestOptions
): Promise<string> => {
  const perfResults = await measureComponentPerformance(component, options);
  const accessResults = await testAccessibility(component);

  const report = `
Performance and Accessibility Report for ${component}
=================================================

Performance Metrics
-----------------
- Render Time: ${perfResults.renderTime.toFixed(2)}ms
- FPS: ${perfResults.fps.toFixed(1)}
- Memory Usage: ${perfResults.memoryUsage ? perfResults.memoryUsage.toFixed(2) + 'MB' : 'N/A'}
- Layout Shifts: ${perfResults.layoutShifts}
- Long Tasks: ${perfResults.longTasks}
- Performance Score: ${perfResults.score}/100

${perfResults.issues.length > 0 ? `\nPerformance Issues:\n${perfResults.issues.map(issue => `- ${issue}`).join('\n')}` : ''}

Accessibility Results
-------------------
- Accessibility Score: ${accessResults.score}/100

${accessResults.issues.length > 0 ? `\nAccessibility Issues:\n${accessResults.issues.map(issue => `- ${issue}`).join('\n')}` : ''}

Recommendations
-------------
${[
  perfResults.fps < performanceThresholds.targetFps ? '- Consider optimizing animations and reducing visual complexity' : '',
  perfResults.layoutShifts > 0 ? '- Fix layout shifts by pre-allocating space for dynamic content' : '',
  perfResults.longTasks > 0 ? '- Break up long-running tasks into smaller chunks' : '',
  accessResults.score < 90 ? '- Address accessibility issues to improve usability' : '',
].filter(Boolean).join('\n')}

Test Configuration
----------------
- Device Profile: ${options?.deviceProfile || 'desktop'}
- Connection Type: ${options?.connection || 'wifi'}
- Test Duration: ${options?.duration || 5000}ms
- Iterations: ${options?.iterations || 3}
`;

  return report;
}; 