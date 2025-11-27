/**
 * Analytics & Logging Module for Voice Input Extension
 * Tracks usage, performance, and errors
 */
export interface VoiceSession {
    sessionId: string;
    startTime: Date;
    endTime?: Date;
    language: string;
    transcriptLength: number;
    isFinal: boolean;
    confidence: number;
    sentToCopilot: boolean;
    errorMessage?: string;
}
export interface PerformanceMetrics {
    totalSessions: number;
    successfulSessions: number;
    failedSessions: number;
    averageTranscriptLength: number;
    averageConfidence: number;
    averageSessionDuration: number;
    mostUsedLanguage: string;
    sentToCopilotCount: number;
    errorRate: number;
}
/**
 * Analytics Manager for Voice Input
 */
export declare class AnalyticsManager {
    private sessions;
    private maxSessions;
    /**
     * Record a voice session
     */
    recordSession(session: VoiceSession): void;
    /**
     * Get performance metrics
     */
    getMetrics(): PerformanceMetrics;
    /**
     * Get sessions in date range
     */
    getSessionsInRange(startDate: Date, endDate: Date): VoiceSession[];
    /**
     * Get sessions by language
     */
    getSessionsByLanguage(language: string): VoiceSession[];
    /**
     * Get failed sessions with errors
     */
    getFailedSessions(): VoiceSession[];
    /**
     * Clear all sessions
     */
    clearSessions(): void;
    /**
     * Export metrics as JSON
     */
    exportMetricsAsJson(): string;
    /**
     * Export sessions as CSV
     */
    exportSessionsAsCsv(): string;
}
/**
 * Event Logger
 */
export declare class EventLogger {
    private logs;
    private maxLogs;
    /**
     * Log info message
     */
    info(message: string, details?: Record<string, any>): void;
    /**
     * Log warning message
     */
    warn(message: string, details?: Record<string, any>): void;
    /**
     * Log error message
     */
    error(message: string, details?: Record<string, any>): void;
    /**
     * Add log entry
     */
    private addLog;
    /**
     * Get all logs
     */
    getAllLogs(): {
        timestamp: Date;
        level: "info" | "warn" | "error";
        message: string;
        details?: Record<string, any>;
    }[];
    /**
     * Get logs by level
     */
    getLogsByLevel(level: 'info' | 'warn' | 'error'): {
        timestamp: Date;
        level: "info" | "warn" | "error";
        message: string;
        details?: Record<string, any>;
    }[];
    /**
     * Get logs in date range
     */
    getLogsInRange(startDate: Date, endDate: Date): {
        timestamp: Date;
        level: "info" | "warn" | "error";
        message: string;
        details?: Record<string, any>;
    }[];
    /**
     * Export logs as JSON
     */
    exportLogsAsJson(): string;
    /**
     * Export logs as formatted text
     */
    exportLogsAsText(): string;
    /**
     * Clear all logs
     */
    clearLogs(): void;
}
/**
 * Global Analytics Instance
 */
export declare const globalAnalytics: AnalyticsManager;
export declare const globalEventLogger: EventLogger;
//# sourceMappingURL=analytics.d.ts.map