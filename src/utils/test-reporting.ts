import { PerformanceMetrics } from './performance-testing';
import { AccessibilityReport } from './accessibility-testing';

export interface TestReport {
  timestamp: string;
  component: string;
  performance: {
    metrics: PerformanceMetrics;
    thresholdsPassed: boolean;
    violations: string[];
  };
  accessibility: {
    report: AccessibilityReport;
    recommendations: string[];
  };
  deviceProfile?: {
    name: string;
    viewport: {
      width: number;
      height: number;
    };
    connection: string;
  };
  summary: {
    overallScore: number;
    status: 'pass' | 'warn' | 'fail';
    criticalIssues: number;
  };
}

export function generateReport(
  componentName: string,
  performanceMetrics: PerformanceMetrics,
  performanceViolations: string[],
  accessibilityReport: AccessibilityReport,
  deviceProfile?: {
    name: string;
    viewport: { width: number; height: number };
    connection: string;
  }
): TestReport {
  // Generate accessibility recommendations
  const recommendations = generateAccessibilityRecommendations(accessibilityReport);

  // Calculate overall score
  const performanceScore = calculatePerformanceScore(performanceMetrics);
  const overallScore = Math.round(
    (performanceScore + accessibilityReport.score) / 2
  );

  // Count critical issues
  const criticalIssues =
    performanceViolations.length +
    accessibilityReport.violations.filter(v => v.impact === 'critical').length;

  // Determine overall status
  const status = determineStatus(overallScore, criticalIssues);

  return {
    timestamp: new Date().toISOString(),
    component: componentName,
    performance: {
      metrics: performanceMetrics,
      thresholdsPassed: performanceViolations.length === 0,
      violations: performanceViolations,
    },
    accessibility: {
      report: accessibilityReport,
      recommendations,
    },
    deviceProfile,
    summary: {
      overallScore,
      status,
      criticalIssues,
    },
  };
}

function calculatePerformanceScore(metrics: PerformanceMetrics): number {
  // Weight different metrics
  const weights = {
    renderTime: 0.3,
    fps: 0.3,
    interactionLatency: 0.2,
    loadTime: 0.1,
    memoryUsage: 0.1,
  };

  // Calculate individual scores (0-100)
  const scores = {
    renderTime: Math.max(0, 100 - (metrics.renderTime / 2)), // 200ms = 0
    fps: Math.min(100, (metrics.fps / 60) * 100), // 60fps = 100
    interactionLatency: Math.max(0, 100 - metrics.interactionLatency), // 100ms = 0
    loadTime: Math.max(0, 100 - (metrics.loadTime / 30)), // 3000ms = 0
    memoryUsage: Math.max(0, 100 - (metrics.memoryUsage / (50 * 1024 * 1024)) * 100), // 50MB = 0
  };

  // Calculate weighted average
  return Math.round(
    Object.entries(weights).reduce(
      (total, [metric, weight]) =>
        total + scores[metric as keyof typeof scores] * weight,
      0
    )
  );
}

function generateAccessibilityRecommendations(
  report: AccessibilityReport
): string[] {
  const recommendations: string[] = [];

  // Process violations
  report.violations.forEach(violation => {
    switch (violation.impact) {
      case 'critical':
        recommendations.push(
          `🚨 Critical: ${violation.description}. This must be fixed immediately.`
        );
        break;
      case 'serious':
        recommendations.push(
          `⚠️ Serious: ${violation.description}. High priority fix needed.`
        );
        break;
      case 'moderate':
        recommendations.push(
          `ℹ️ Moderate: ${violation.description}. Should be addressed.`
        );
        break;
      case 'minor':
        recommendations.push(
          `📝 Minor: ${violation.description}. Consider improving.`
        );
        break;
    }
  });

  // Process incomplete tests
  if (report.incomplete.length > 0) {
    recommendations.push(
      '🔍 Some accessibility tests were inconclusive and require manual verification:'
    );
    report.incomplete.forEach(issue => {
      recommendations.push(`  - ${issue.description}`);
    });
  }

  // Add general recommendations based on score
  if (report.score < 70) {
    recommendations.push(
      '🔧 Major accessibility improvements needed. Consider a comprehensive audit.'
    );
  } else if (report.score < 90) {
    recommendations.push(
      '📈 Good accessibility foundation, but room for improvement.'
    );
  }

  return recommendations;
}

function determineStatus(
  overallScore: number,
  criticalIssues: number
): 'pass' | 'warn' | 'fail' {
  if (criticalIssues > 0 || overallScore < 70) {
    return 'fail';
  }
  if (overallScore < 90) {
    return 'warn';
  }
  return 'pass';
}

export function generateMarkdownReport(report: TestReport): string {
  return `
# Test Report: ${report.component}
Generated on: ${new Date(report.timestamp).toLocaleString()}

## Summary
- Overall Score: ${report.summary.overallScore}/100
- Status: ${report.summary.status.toUpperCase()}
- Critical Issues: ${report.summary.criticalIssues}

${
  report.deviceProfile
    ? `## Device Profile
- Device: ${report.deviceProfile.name}
- Viewport: ${report.deviceProfile.viewport.width}x${report.deviceProfile.viewport.height}
- Connection: ${report.deviceProfile.connection}`
    : ''
}

## Performance Metrics
- Render Time: ${report.performance.metrics.renderTime.toFixed(2)}ms
- FPS: ${report.performance.metrics.fps.toFixed(2)}
- Interaction Latency: ${report.performance.metrics.interactionLatency.toFixed(2)}ms
- Load Time: ${report.performance.metrics.loadTime.toFixed(2)}ms
- Memory Usage: ${(report.performance.metrics.memoryUsage / (1024 * 1024)).toFixed(2)}MB

${
  report.performance.violations.length > 0
    ? `### Performance Violations
${report.performance.violations.map(v => `- ${v}`).join('\n')}`
    : '### Performance: All thresholds passed ✅'
}

## Accessibility
Score: ${report.accessibility.report.score}/100

### Violations
${
  report.accessibility.report.violations.length > 0
    ? report.accessibility.report.violations
        .map(
          v => `- [${v.impact.toUpperCase()}] ${v.description}
  - Help: ${v.helpUrl}
  - Affected elements: ${v.nodes.length}`
        )
        .join('\n')
    : '- No violations found ✅'
}

### Recommendations
${report.accessibility.recommendations.map(r => `- ${r}`).join('\n')}

### Passed Tests
${report.accessibility.report.passes.map(p => `- ${p}`).join('\n')}
`;
} 