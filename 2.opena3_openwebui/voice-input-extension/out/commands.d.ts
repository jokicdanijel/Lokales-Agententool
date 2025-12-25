import * as vscode from "vscode";
import { AnalyticsManager, EventLogger } from "./analytics";
import { CopilotIntegrationHandler } from "./copilot-integration";
import { VoiceInputSettings } from "./settings";
/**
 * Command Handler for Voice Input Extension
 * Manages all registered commands
 */
export declare class CommandHandler {
  private settings;
  private analytics;
  private eventLogger;
  private outputChannel;
  constructor(
    settings: VoiceInputSettings,
    copilotHandler: CopilotIntegrationHandler,
    analytics: AnalyticsManager,
    eventLogger: EventLogger,
    outputChannel: vscode.OutputChannel,
  );
  /**
   * Show settings panel
   */
  showSettings(): Promise<void>;
  /**
   * Show analytics/statistics
   */
  showAnalytics(): Promise<void>;
  /**
   * Export analytics
   */
  exportAnalytics(): Promise<void>;
  /**
   * Switch language
   */
  switchLanguage(): Promise<void>;
  /**
   * Clear history/cache
   */
  clearHistory(): Promise<void>;
  /**
   * Reset all settings
   */
  resetSettings(): Promise<void>;
  /**
   * Show help/documentation
   */
  showHelp(): Promise<void>;
  /**
   * Get HTML for help panel
   */
  private getHelpHtml;
  /**
   * Get language name from code
   */
  private getLanguageName;
  /**
   * Toggle continuous mode
   */
  toggleContinuousMode(): Promise<void>;
  /**
   * Test microphone
   */
  testMicrophone(): Promise<void>;
}
//# sourceMappingURL=commands.d.ts.map
