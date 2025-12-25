"use strict";
var __createBinding =
  (this && this.__createBinding) ||
  (Object.create
    ? function (o, m, k, k2) {
        if (k2 === undefined) k2 = k;
        var desc = Object.getOwnPropertyDescriptor(m, k);
        if (
          !desc ||
          ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)
        ) {
          desc = {
            enumerable: true,
            get: function () {
              return m[k];
            },
          };
        }
        Object.defineProperty(o, k2, desc);
      }
    : function (o, m, k, k2) {
        if (k2 === undefined) k2 = k;
        o[k2] = m[k];
      });
var __setModuleDefault =
  (this && this.__setModuleDefault) ||
  (Object.create
    ? function (o, v) {
        Object.defineProperty(o, "default", { enumerable: true, value: v });
      }
    : function (o, v) {
        o["default"] = v;
      });
var __importStar =
  (this && this.__importStar) ||
  (function () {
    var ownKeys = function (o) {
      ownKeys =
        Object.getOwnPropertyNames ||
        function (o) {
          var ar = [];
          for (var k in o)
            if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
          return ar;
        };
      return ownKeys(o);
    };
    return function (mod) {
      if (mod && mod.__esModule) return mod;
      var result = {};
      if (mod != null)
        for (var k = ownKeys(mod), i = 0; i < k.length; i++)
          if (k[i] !== "default") __createBinding(result, mod, k[i]);
      __setModuleDefault(result, mod);
      return result;
    };
  })();
Object.defineProperty(exports, "__esModule", { value: true });
exports.VoiceInputSettings = void 0;
const vscode = __importStar(require("vscode"));
/**
 * Settings Management for Voice Input Extension
 */
class VoiceInputSettings {
  constructor() {
    this.config = vscode.workspace.getConfiguration("voiceInput");
  }
  // ===== RECOGNITION SETTINGS =====
  /**
   * Get enabled languages for recognition
   */
  getLanguages() {
    return this.config.get("languages", ["de", "en"]);
  }
  /**
   * Get default language
   */
  getDefaultLanguage() {
    return this.config.get("defaultLanguage", "de");
  }
  /**
   * Get silence threshold in ms
   */
  getSilenceThreshold() {
    return this.config.get("silenceThreshold", 2000);
  }
  /**
   * Get max recording duration in seconds
   */
  getMaxDuration() {
    return this.config.get("maxDuration", 60);
  }
  // ===== COPILOT INTEGRATION SETTINGS =====
  /**
   * Check if auto-send to Copilot is enabled
   */
  isAutoSendEnabled() {
    return this.config.get("autoSend", false);
  }
  /**
   * Check if Copilot command detection is enabled
   */
  isCopilotCommandDetectionEnabled() {
    return this.config.get("detectCopilotCommands", true);
  }
  /**
   * Check if auto-focus editor after insertion
   */
  isAutoFocusEditorEnabled() {
    return this.config.get("autoFocusEditor", true);
  }
  // ===== UI/UX SETTINGS =====
  /**
   * Check if status bar is enabled
   */
  isStatusBarEnabled() {
    return this.config.get("showStatusBar", true);
  }
  /**
   * Get status bar position
   */
  getStatusBarPosition() {
    return this.config.get("statusBarPosition", "right");
  }
  /**
   * Check if output channel should be shown
   */
  isOutputChannelVisible() {
    return this.config.get("showOutput", true);
  }
  /**
   * Check if sounds are enabled
   */
  areSoundsEnabled() {
    return this.config.get("enableSounds", true);
  }
  /**
   * Get sound volume (0-1)
   */
  getSoundVolume() {
    const volume = this.config.get("soundVolume", 0.5);
    return Math.max(0, Math.min(1, volume));
  }
  /**
   * Check if notification on end is enabled
   */
  isNotificationOnEndEnabled() {
    return this.config.get("notifyOnEnd", true);
  }
  // ===== ADVANCED SETTINGS =====
  /**
   * Get continuous mode (keep listening between transcripts)
   */
  isContinuousModeEnabled() {
    return this.config.get("continuousMode", false);
  }
  /**
   * Get interim results display (show partial transcripts)
   */
  isInterimResultsEnabled() {
    return this.config.get("showInterimResults", true);
  }
  /**
   * Get confidence threshold (0-1)
   */
  getConfidenceThreshold() {
    const threshold = this.config.get("confidenceThreshold", 0.5);
    return Math.max(0, Math.min(1, threshold));
  }
  /**
   * Get keyboard shortcut custom key
   */
  getCustomKeybinding() {
    return this.config.get("customKeybinding", "ctrl+shift+v");
  }
  // ===== SETTER METHODS =====
  /**
   * Update setting value
   */
  async updateSetting(key, value, global = false) {
    const target = global
      ? vscode.ConfigurationTarget.Global
      : vscode.ConfigurationTarget.Workspace;
    await this.config.update(key, value, target);
    // Refresh config reference
    this.config = vscode.workspace.getConfiguration("voiceInput");
  }
  /**
   * Get all settings as object
   */
  getAllSettings() {
    return {
      // Recognition
      languages: this.getLanguages(),
      defaultLanguage: this.getDefaultLanguage(),
      silenceThreshold: this.getSilenceThreshold(),
      maxDuration: this.getMaxDuration(),
      // Copilot
      autoSend: this.isAutoSendEnabled(),
      detectCopilotCommands: this.isCopilotCommandDetectionEnabled(),
      autoFocusEditor: this.isAutoFocusEditorEnabled(),
      // UI/UX
      showStatusBar: this.isStatusBarEnabled(),
      statusBarPosition: this.getStatusBarPosition(),
      showOutput: this.isOutputChannelVisible(),
      enableSounds: this.areSoundsEnabled(),
      soundVolume: this.getSoundVolume(),
      notifyOnEnd: this.isNotificationOnEndEnabled(),
      // Advanced
      continuousMode: this.isContinuousModeEnabled(),
      showInterimResults: this.isInterimResultsEnabled(),
      confidenceThreshold: this.getConfidenceThreshold(),
      customKeybinding: this.getCustomKeybinding(),
    };
  }
  /**
   * Reset all settings to defaults
   */
  async resetToDefaults() {
    const settings = [
      "languages",
      "defaultLanguage",
      "silenceThreshold",
      "maxDuration",
      "autoSend",
      "detectCopilotCommands",
      "autoFocusEditor",
      "showStatusBar",
      "statusBarPosition",
      "showOutput",
      "enableSounds",
      "soundVolume",
      "notifyOnEnd",
      "continuousMode",
      "showInterimResults",
      "confidenceThreshold",
      "customKeybinding",
    ];
    for (const setting of settings) {
      await this.config.update(
        setting,
        undefined,
        vscode.ConfigurationTarget.Workspace,
      );
    }
    this.config = vscode.workspace.getConfiguration("voiceInput");
  }
  /**
   * Watch for setting changes
   */
  onSettingsChanged(callback) {
    return vscode.workspace.onDidChangeConfiguration((event) => {
      if (event.affectsConfiguration("voiceInput")) {
        this.config = vscode.workspace.getConfiguration("voiceInput");
        callback();
      }
    });
  }
}
exports.VoiceInputSettings = VoiceInputSettings;
//# sourceMappingURL=settings.js.map
