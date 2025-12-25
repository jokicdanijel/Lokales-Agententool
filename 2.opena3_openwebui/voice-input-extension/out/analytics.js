"use strict";
/**
 * Analytics & Logging Module for Voice Input Extension
 * Tracks usage, performance, and errors
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.globalEventLogger =
  exports.globalAnalytics =
  exports.EventLogger =
  exports.AnalyticsManager =
    void 0;
/**
 * Analytics Manager for Voice Input
 */
class AnalyticsManager {
  constructor() {
    this.sessions = [];
    this.maxSessions = 1000;
  }
  /**
   * Record a voice session
   */
  recordSession(session) {
    this.sessions.push(session);
    // Keep only recent sessions in memory
    if (this.sessions.length > this.maxSessions) {
      this.sessions = this.sessions.slice(-this.maxSessions);
    }
  }
  /**
   * Get performance metrics
   */
  getMetrics() {
    if (this.sessions.length === 0) {
      return {
        totalSessions: 0,
        successfulSessions: 0,
        failedSessions: 0,
        averageTranscriptLength: 0,
        averageConfidence: 0,
        averageSessionDuration: 0,
        mostUsedLanguage: "unknown",
        sentToCopilotCount: 0,
        errorRate: 0,
      };
    }
    const successful = this.sessions.filter((s) => !s.errorMessage);
    const failed = this.sessions.filter((s) => s.errorMessage);
    const totalLength = successful.reduce(
      (sum, s) => sum + s.transcriptLength,
      0,
    );
    const totalConfidence = successful.reduce(
      (sum, s) => sum + s.confidence,
      0,
    );
    const totalDuration = this.sessions.reduce((sum, s) => {
      const duration =
        (s.endTime || new Date()).getTime() - s.startTime.getTime();
      return sum + duration;
    }, 0);
    const languageCounts = {};
    this.sessions.forEach((s) => {
      languageCounts[s.language] = (languageCounts[s.language] || 0) + 1;
    });
    const mostUsedLanguage =
      Object.entries(languageCounts).sort(([, a], [, b]) => b - a)[0]?.[0] ||
      "unknown";
    const sentToCopilot = this.sessions.filter((s) => s.sentToCopilot).length;
    return {
      totalSessions: this.sessions.length,
      successfulSessions: successful.length,
      failedSessions: failed.length,
      averageTranscriptLength: totalLength / successful.length || 0,
      averageConfidence: totalConfidence / successful.length || 0,
      averageSessionDuration: totalDuration / this.sessions.length || 0,
      mostUsedLanguage,
      sentToCopilotCount: sentToCopilot,
      errorRate: failed.length / this.sessions.length || 0,
    };
  }
  /**
   * Get sessions in date range
   */
  getSessionsInRange(startDate, endDate) {
    return this.sessions.filter(
      (s) => s.startTime >= startDate && s.startTime <= endDate,
    );
  }
  /**
   * Get sessions by language
   */
  getSessionsByLanguage(language) {
    return this.sessions.filter((s) => s.language === language);
  }
  /**
   * Get failed sessions with errors
   */
  getFailedSessions() {
    return this.sessions.filter((s) => s.errorMessage);
  }
  /**
   * Clear all sessions
   */
  clearSessions() {
    this.sessions = [];
  }
  /**
   * Export metrics as JSON
   */
  exportMetricsAsJson() {
    return JSON.stringify(
      {
        timestamp: new Date().toISOString(),
        metrics: this.getMetrics(),
        sessions: this.sessions.length,
      },
      null,
      2,
    );
  }
  /**
   * Export sessions as CSV
   */
  exportSessionsAsCsv() {
    const headers = [
      "Session ID",
      "Start Time",
      "End Time",
      "Language",
      "Transcript Length",
      "Is Final",
      "Confidence",
      "Sent to Copilot",
      "Error",
    ].join(",");
    const rows = this.sessions.map((s) =>
      [
        s.sessionId,
        s.startTime.toISOString(),
        s.endTime?.toISOString() || "",
        s.language,
        s.transcriptLength,
        s.isFinal ? "yes" : "no",
        s.confidence.toFixed(2),
        s.sentToCopilot ? "yes" : "no",
        s.errorMessage || "",
      ]
        .map((v) => `"${v}"`)
        .join(","),
    );
    return [headers, ...rows].join("\n");
  }
}
exports.AnalyticsManager = AnalyticsManager;
/**
 * Event Logger
 */
class EventLogger {
  constructor() {
    this.logs = [];
    this.maxLogs = 5000;
  }
  /**
   * Log info message
   */
  info(message, details) {
    this.addLog("info", message, details);
  }
  /**
   * Log warning message
   */
  warn(message, details) {
    this.addLog("warn", message, details);
  }
  /**
   * Log error message
   */
  error(message, details) {
    this.addLog("error", message, details);
  }
  /**
   * Add log entry
   */
  addLog(level, message, details) {
    this.logs.push({
      timestamp: new Date(),
      level,
      message,
      details,
    });
    // Keep only recent logs
    if (this.logs.length > this.maxLogs) {
      this.logs = this.logs.slice(-this.maxLogs);
    }
    // Console output for debugging
    const logFn =
      level === "error"
        ? console.error
        : level === "warn"
          ? console.warn
          : console.log;
    logFn(`[Voice Input ${level.toUpperCase()}] ${message}`, details);
  }
  /**
   * Get all logs
   */
  getAllLogs() {
    return [...this.logs];
  }
  /**
   * Get logs by level
   */
  getLogsByLevel(level) {
    return this.logs.filter((log) => log.level === level);
  }
  /**
   * Get logs in date range
   */
  getLogsInRange(startDate, endDate) {
    return this.logs.filter(
      (log) => log.timestamp >= startDate && log.timestamp <= endDate,
    );
  }
  /**
   * Export logs as JSON
   */
  exportLogsAsJson() {
    return JSON.stringify(this.logs, null, 2);
  }
  /**
   * Export logs as formatted text
   */
  exportLogsAsText() {
    return this.logs
      .map(
        (log) =>
          `[${log.timestamp.toISOString()}] ${log.level.toUpperCase()} - ${log.message}${log.details ? "\nDetails: " + JSON.stringify(log.details, null, 2) : ""}`,
      )
      .join("\n\n");
  }
  /**
   * Clear all logs
   */
  clearLogs() {
    this.logs = [];
  }
}
exports.EventLogger = EventLogger;
/**
 * Global Analytics Instance
 */
exports.globalAnalytics = new AnalyticsManager();
exports.globalEventLogger = new EventLogger();
//# sourceMappingURL=analytics.js.map
