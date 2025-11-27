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
export class AnalyticsManager {
    private sessions: VoiceSession[] = [];
    private maxSessions: number = 1000;

    /**
     * Record a voice session
     */
    public recordSession(session: VoiceSession): void {
        this.sessions.push(session);

        // Keep only recent sessions in memory
        if (this.sessions.length > this.maxSessions) {
            this.sessions = this.sessions.slice(-this.maxSessions);
        }
    }

    /**
     * Get performance metrics
     */
    public getMetrics(): PerformanceMetrics {
        if (this.sessions.length === 0) {
            return {
                totalSessions: 0,
                successfulSessions: 0,
                failedSessions: 0,
                averageTranscriptLength: 0,
                averageConfidence: 0,
                averageSessionDuration: 0,
                mostUsedLanguage: 'unknown',
                sentToCopilotCount: 0,
                errorRate: 0
            };
        }

        const successful = this.sessions.filter(s => !s.errorMessage);
        const failed = this.sessions.filter(s => s.errorMessage);

        const totalLength = successful.reduce((sum, s) => sum + s.transcriptLength, 0);
        const totalConfidence = successful.reduce((sum, s) => sum + s.confidence, 0);
        const totalDuration = this.sessions.reduce((sum, s) => {
            const duration = (s.endTime || new Date()).getTime() - s.startTime.getTime();
            return sum + duration;
        }, 0);

        const languageCounts: Record<string, number> = {};
        this.sessions.forEach(s => {
            languageCounts[s.language] = (languageCounts[s.language] || 0) + 1;
        });

        const mostUsedLanguage = Object.entries(languageCounts).sort(
            ([, a], [, b]) => b - a
        )[0]?.[0] || 'unknown';

        const sentToCopilot = this.sessions.filter(s => s.sentToCopilot).length;

        return {
            totalSessions: this.sessions.length,
            successfulSessions: successful.length,
            failedSessions: failed.length,
            averageTranscriptLength: totalLength / successful.length || 0,
            averageConfidence: totalConfidence / successful.length || 0,
            averageSessionDuration: totalDuration / this.sessions.length || 0,
            mostUsedLanguage,
            sentToCopilotCount: sentToCopilot,
            errorRate: failed.length / this.sessions.length || 0
        };
    }

    /**
     * Get sessions in date range
     */
    public getSessionsInRange(startDate: Date, endDate: Date): VoiceSession[] {
        return this.sessions.filter(s =>
            s.startTime >= startDate && s.startTime <= endDate
        );
    }

    /**
     * Get sessions by language
     */
    public getSessionsByLanguage(language: string): VoiceSession[] {
        return this.sessions.filter(s => s.language === language);
    }

    /**
     * Get failed sessions with errors
     */
    public getFailedSessions(): VoiceSession[] {
        return this.sessions.filter(s => s.errorMessage);
    }

    /**
     * Clear all sessions
     */
    public clearSessions(): void {
        this.sessions = [];
    }

    /**
     * Export metrics as JSON
     */
    public exportMetricsAsJson(): string {
        return JSON.stringify({
            timestamp: new Date().toISOString(),
            metrics: this.getMetrics(),
            sessions: this.sessions.length
        }, null, 2);
    }

    /**
     * Export sessions as CSV
     */
    public exportSessionsAsCsv(): string {
        const headers = [
            'Session ID',
            'Start Time',
            'End Time',
            'Language',
            'Transcript Length',
            'Is Final',
            'Confidence',
            'Sent to Copilot',
            'Error'
        ].join(',');

        const rows = this.sessions.map(s =>
            [
                s.sessionId,
                s.startTime.toISOString(),
                s.endTime?.toISOString() || '',
                s.language,
                s.transcriptLength,
                s.isFinal ? 'yes' : 'no',
                s.confidence.toFixed(2),
                s.sentToCopilot ? 'yes' : 'no',
                s.errorMessage || ''
            ].map(v => `"${v}"`).join(',')
        );

        return [headers, ...rows].join('\n');
    }
}

/**
 * Event Logger
 */
export class EventLogger {
    private logs: Array<{
        timestamp: Date;
        level: 'info' | 'warn' | 'error';
        message: string;
        details?: Record<string, any>;
    }> = [];

    private maxLogs: number = 5000;

    /**
     * Log info message
     */
    public info(message: string, details?: Record<string, any>): void {
        this.addLog('info', message, details);
    }

    /**
     * Log warning message
     */
    public warn(message: string, details?: Record<string, any>): void {
        this.addLog('warn', message, details);
    }

    /**
     * Log error message
     */
    public error(message: string, details?: Record<string, any>): void {
        this.addLog('error', message, details);
    }

    /**
     * Add log entry
     */
    private addLog(
        level: 'info' | 'warn' | 'error',
        message: string,
        details?: Record<string, any>
    ): void {
        this.logs.push({
            timestamp: new Date(),
            level,
            message,
            details
        });

        // Keep only recent logs
        if (this.logs.length > this.maxLogs) {
            this.logs = this.logs.slice(-this.maxLogs);
        }

        // Console output for debugging
        const logFn = level === 'error' ? console.error :
                      level === 'warn' ? console.warn :
                      console.log;

        logFn(`[Voice Input ${level.toUpperCase()}] ${message}`, details);
    }

    /**
     * Get all logs
     */
    public getAllLogs() {
        return [...this.logs];
    }

    /**
     * Get logs by level
     */
    public getLogsByLevel(level: 'info' | 'warn' | 'error') {
        return this.logs.filter(log => log.level === level);
    }

    /**
     * Get logs in date range
     */
    public getLogsInRange(startDate: Date, endDate: Date) {
        return this.logs.filter(log =>
            log.timestamp >= startDate && log.timestamp <= endDate
        );
    }

    /**
     * Export logs as JSON
     */
    public exportLogsAsJson(): string {
        return JSON.stringify(this.logs, null, 2);
    }

    /**
     * Export logs as formatted text
     */
    public exportLogsAsText(): string {
        return this.logs.map(log =>
            `[${log.timestamp.toISOString()}] ${log.level.toUpperCase()} - ${log.message}${
                log.details ? '\nDetails: ' + JSON.stringify(log.details, null, 2) : ''
            }`
        ).join('\n\n');
    }

    /**
     * Clear all logs
     */
    public clearLogs(): void {
        this.logs = [];
    }
}

/**
 * Global Analytics Instance
 */
export const globalAnalytics = new AnalyticsManager();
export const globalEventLogger = new EventLogger();
