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
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
const analytics_1 = require("./analytics");
const commands_1 = require("./commands");
const copilot_integration_1 = require("./copilot-integration");
const recognition_engine_1 = require("./recognition-engine");
const settings_1 = require("./settings");
/**
 * Advanced Voice Input Manager for VS Code
 * Full integration with all modules: recognition, settings, Copilot, commands, analytics
 */
class AdvancedVoiceInputManager {
  constructor() {
    this.isRecording = false;
    this.sessionId = "";
    this.sessionStartTime = new Date();
    // Initialize dependencies
    this.outputChannel = vscode.window.createOutputChannel("Voice Input");
    this.settings = new settings_1.VoiceInputSettings();
    this.copilotHandler = new copilot_integration_1.CopilotIntegrationHandler(
      this.outputChannel,
    );
    this.analytics = analytics_1.globalAnalytics;
    this.eventLogger = analytics_1.globalEventLogger;
    // Initialize recognition engine
    const defaultLanguage = this.settings.getDefaultLanguage();
    this.recognitionEngine = new recognition_engine_1.VoiceRecognitionEngine(
      defaultLanguage,
    );
    // Create command handler
    this.commandHandler = new commands_1.CommandHandler(
      this.settings,
      this.copilotHandler,
      this.analytics,
      this.eventLogger,
      this.outputChannel,
    );
    // Create status bar item
    this.statusBar = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      100,
    );
    this.statusBar.command = "voiceInput.toggle";
    this.updateStatusBar();
    this.setupRecognitionHandlers();
    this.setupSettingsWatcher();
    this.log("🚀 Advanced Voice Input Manager initialized");
  }
  /**
   * Setup recognition engine handlers
   */
  setupRecognitionHandlers() {
    this.recognitionEngine.onTranscript = (transcript, isFinal) => {
      this.handleTranscript(transcript, isFinal);
    };
    this.recognitionEngine.onError = (error) => {
      this.handleError(error);
    };
    this.recognitionEngine.onEnd = () => {
      this.handleEnd();
    };
    this.recognitionEngine.onStart = () => {
      this.sessionId = this.generateSessionId();
      this.sessionStartTime = new Date();
      this.log("🎙️ Recording session started: " + this.sessionId);
    };
  }
  /**
   * Setup settings watcher
   */
  setupSettingsWatcher() {
    this.settings.onSettingsChanged(() => {
      this.log("⚙️ Settings updated");
      this.updateStatusBar();
    });
  }
  /**
   * Generate session ID
   */
  generateSessionId() {
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }
  /**
   * Start voice recognition
   */
  start() {
    if (this.isRecording) {
      return;
    }
    this.isRecording = true;
    this.updateStatusBar();
    // Set language from settings
    const language = this.settings.getDefaultLanguage();
    this.recognitionEngine.setLanguage(language);
    // Set silence threshold
    const threshold = this.settings.getSilenceThreshold();
    this.recognitionEngine.setSilenceThreshold(threshold);
    this.recognitionEngine.start();
    this.eventLogger.info("Voice recognition started", { language });
  }
  /**
   * Stop voice recognition
   */
  stop() {
    if (!this.isRecording) {
      return;
    }
    this.isRecording = false;
    this.recognitionEngine.stop();
    this.updateStatusBar();
    this.eventLogger.info("Voice recognition stopped");
  }
  /**
   * Toggle voice recognition
   */
  toggle() {
    if (this.isRecording) {
      this.stop();
    } else {
      this.start();
    }
  }
  /**
   * Handle transcript from recognition engine
   */
  async handleTranscript(transcript, isFinal) {
    if (isFinal) {
      this.log(`✅ Final: ${transcript}`);
      // Process the transcript
      const autoSend = this.settings.isAutoSendEnabled();
      await this.copilotHandler.processTranscript(transcript, autoSend);
      // Record session for analytics
      this.recordSession(transcript, true);
    } else {
      // Show interim results if enabled
      if (this.settings.isInterimResultsEnabled()) {
        this.log(`📝 Interim: ${transcript}`);
      }
    }
  }
  /**
   * Handle recognition error
   */
  handleError(error) {
    this.log(`❌ Error: ${error}`);
    this.eventLogger.error("Recognition error", { error });
    // Record failed session
    this.recordSession("", false, error);
    if (this.settings.isNotificationOnEndEnabled()) {
      vscode.window.showErrorMessage(`Voice Input Error: ${error}`);
    }
  }
  /**
   * Handle recognition end
   */
  handleEnd() {
    this.isRecording = false;
    this.updateStatusBar();
    this.log("🛑 Voice recognition stopped");
    this.eventLogger.info("Recognition session ended");
  }
  /**
   * Record session for analytics
   */
  recordSession(transcript, success, error) {
    const session = {
      sessionId: this.sessionId,
      startTime: this.sessionStartTime,
      endTime: new Date(),
      language: this.settings.getDefaultLanguage(),
      transcriptLength: transcript.length,
      isFinal: success,
      confidence: success ? 0.95 : 0,
      sentToCopilot: this.settings.isAutoSendEnabled() && success,
      errorMessage: error,
    };
    this.analytics.recordSession(session);
  }
  /**
   * Get command handler
   */
  getCommandHandler() {
    return this.commandHandler;
  }
  /**
   * Update status bar
   */
  updateStatusBar() {
    const statusBar = this.settings.isStatusBarEnabled();
    if (!statusBar) {
      this.statusBar.hide();
      return;
    }
    const status = this.isRecording ? "🎙️ Recording..." : "🎤 Ready";
    this.statusBar.text = status;
    this.statusBar.tooltip = "Click to toggle voice recognition (Ctrl+Shift+V)";
    this.statusBar.show();
  }
  /**
   * Log message to output channel
   */
  log(message) {
    const timestamp = new Date().toLocaleTimeString();
    this.outputChannel.appendLine(`[${timestamp}] ${message}`);
    if (this.settings.isOutputChannelVisible()) {
      this.outputChannel.show(true);
    }
  }
  /**
   * Show output channel
   */
  showOutput() {
    this.outputChannel.show();
  }
  /**
   * Dispose resources
   */
  dispose() {
    this.statusBar.dispose();
    this.outputChannel.dispose();
    if (this.recognitionEngine) {
      this.recognitionEngine.abort();
    }
  }
}
let manager;
/**
 * Extension activation - Advanced Version
 */
function activate(context) {
  manager = new AdvancedVoiceInputManager();
  const commandHandler = manager.getCommandHandler();
  // Register core commands
  context.subscriptions.push(
    vscode.commands.registerCommand("voiceInput.toggle", () => {
      manager.toggle();
    }),
    vscode.commands.registerCommand("voiceInput.start", () => {
      manager.start();
    }),
    vscode.commands.registerCommand("voiceInput.stop", () => {
      manager.stop();
    }),
    vscode.commands.registerCommand("voiceInput.showOutput", () => {
      manager.showOutput();
    }),
    // Settings and configuration commands
    vscode.commands.registerCommand("voiceInput.showSettings", () => {
      commandHandler.showSettings();
    }),
    vscode.commands.registerCommand("voiceInput.switchLanguage", () => {
      commandHandler.switchLanguage();
    }),
    vscode.commands.registerCommand("voiceInput.toggleContinuousMode", () => {
      commandHandler.toggleContinuousMode();
    }),
    // Analytics commands
    vscode.commands.registerCommand("voiceInput.showAnalytics", () => {
      commandHandler.showAnalytics();
    }),
    vscode.commands.registerCommand("voiceInput.exportAnalytics", () => {
      commandHandler.exportAnalytics();
    }),
    vscode.commands.registerCommand("voiceInput.clearHistory", () => {
      commandHandler.clearHistory();
    }),
    // Help and utilities
    vscode.commands.registerCommand("voiceInput.showHelp", () => {
      commandHandler.showHelp();
    }),
    vscode.commands.registerCommand("voiceInput.testMicrophone", () => {
      commandHandler.testMicrophone();
    }),
    vscode.commands.registerCommand("voiceInput.resetSettings", () => {
      commandHandler.resetSettings();
    }),
  );
  console.log("✅ Advanced Voice Input Extension activated");
  analytics_1.globalEventLogger.info(
    "Advanced extension activated successfully",
  );
}
/**
 * Extension deactivation
 */
function deactivate() {
  if (manager) {
    manager.dispose();
  }
  console.log("✅ Voice Input Extension deactivated");
  analytics_1.globalEventLogger.info("Extension deactivated");
}
//# sourceMappingURL=extension-advanced.js.map
