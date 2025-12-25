import * as vscode from "vscode";
/**
 * Settings Management for Voice Input Extension
 */
export declare class VoiceInputSettings {
  private config;
  constructor();
  /**
   * Get enabled languages for recognition
   */
  getLanguages(): string[];
  /**
   * Get default language
   */
  getDefaultLanguage(): string;
  /**
   * Get silence threshold in ms
   */
  getSilenceThreshold(): number;
  /**
   * Get max recording duration in seconds
   */
  getMaxDuration(): number;
  /**
   * Check if auto-send to Copilot is enabled
   */
  isAutoSendEnabled(): boolean;
  /**
   * Check if Copilot command detection is enabled
   */
  isCopilotCommandDetectionEnabled(): boolean;
  /**
   * Check if auto-focus editor after insertion
   */
  isAutoFocusEditorEnabled(): boolean;
  /**
   * Check if status bar is enabled
   */
  isStatusBarEnabled(): boolean;
  /**
   * Get status bar position
   */
  getStatusBarPosition(): "left" | "right";
  /**
   * Check if output channel should be shown
   */
  isOutputChannelVisible(): boolean;
  /**
   * Check if sounds are enabled
   */
  areSoundsEnabled(): boolean;
  /**
   * Get sound volume (0-1)
   */
  getSoundVolume(): number;
  /**
   * Check if notification on end is enabled
   */
  isNotificationOnEndEnabled(): boolean;
  /**
   * Get continuous mode (keep listening between transcripts)
   */
  isContinuousModeEnabled(): boolean;
  /**
   * Get interim results display (show partial transcripts)
   */
  isInterimResultsEnabled(): boolean;
  /**
   * Get confidence threshold (0-1)
   */
  getConfidenceThreshold(): number;
  /**
   * Get keyboard shortcut custom key
   */
  getCustomKeybinding(): string;
  /**
   * Update setting value
   */
  updateSetting(key: string, value: any, global?: boolean): Promise<void>;
  /**
   * Get all settings as object
   */
  getAllSettings(): Record<string, any>;
  /**
   * Reset all settings to defaults
   */
  resetToDefaults(): Promise<void>;
  /**
   * Watch for setting changes
   */
  onSettingsChanged(callback: () => void): vscode.Disposable;
}
//# sourceMappingURL=settings.d.ts.map
