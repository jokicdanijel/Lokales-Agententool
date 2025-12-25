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
exports.CopilotIntegrationHandler = void 0;
const vscode = __importStar(require("vscode"));
/**
 * Copilot Integration Handler
 * Manages communication with GitHub Copilot
 */
class CopilotIntegrationHandler {
  constructor(outputChannel) {
    this.outputChannel = outputChannel;
  }
  /**
   * Send transcript to Copilot Chat
   */
  async sendToCopilotChat(transcript) {
    try {
      // Method 1: Try Copilot Chat API
      try {
        await vscode.commands.executeCommand(
          "github.copilot.chat.openSymbolFromWorkspace",
          transcript,
        );
      } catch {
        // Method 2: Fallback to inline chat
        await vscode.commands.executeCommand(
          "github.copilot.interactiveEditor.makeRequest",
          transcript,
        );
      }
      this.logSuccess("Sent to Copilot", transcript);
      return true;
    } catch (error) {
      this.logError("Failed to send to Copilot", error);
      return false;
    }
  }
  /**
   * Insert transcript into editor at cursor
   */
  async insertIntoEditor(transcript) {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      this.logError("No active editor", new Error("No active editor found"));
      return false;
    }
    try {
      await editor.edit((editBuilder) => {
        editBuilder.insert(editor.selection.active, transcript + " ");
      });
      this.logSuccess("Inserted into editor", transcript);
      return true;
    } catch (error) {
      this.logError("Failed to insert into editor", error);
      return false;
    }
  }
  /**
   * Process transcript (auto-send or insert based on config)
   */
  async processTranscript(transcript, autoSend) {
    const trimmed = transcript.trim();
    if (!trimmed) {
      return;
    }
    // Always insert into editor
    await this.insertIntoEditor(trimmed);
    // Send to Copilot if auto-send enabled
    if (autoSend) {
      setTimeout(() => {
        this.sendToCopilotChat(trimmed);
      }, 500);
    }
  }
  /**
   * Detect if transcript is a Copilot command
   */
  isCopilotCommand(transcript) {
    const copilotKeywords = [
      "generate",
      "create",
      "write",
      "explain",
      "refactor",
      "optimize",
      "fix",
      "debug",
      "test",
      "document",
      "comment",
      "function",
      "class",
      "method",
    ];
    const lowerTranscript = transcript.toLowerCase();
    return copilotKeywords.some((keyword) => lowerTranscript.includes(keyword));
  }
  /**
   * Format transcript for Copilot
   */
  formatForCopilot(transcript) {
    // Remove extra spaces
    let formatted = transcript.replace(/\s+/g, " ").trim();
    // Capitalize first letter
    if (formatted.length > 0) {
      formatted = formatted.charAt(0).toUpperCase() + formatted.slice(1);
    }
    // Add punctuation if missing
    if (!/[.!?]$/.test(formatted)) {
      formatted += ".";
    }
    return formatted;
  }
  /**
   * Log success message
   */
  logSuccess(action, details) {
    const timestamp = new Date().toLocaleTimeString();
    this.outputChannel.appendLine(`[${timestamp}] ✅ ${action}: ${details}`);
  }
  /**
   * Log error message
   */
  logError(action, error) {
    const timestamp = new Date().toLocaleTimeString();
    const errorMsg = error instanceof Error ? error.message : String(error);
    this.outputChannel.appendLine(`[${timestamp}] ❌ ${action}: ${errorMsg}`);
  }
  /**
   * Log info message
   */
  logInfo(message) {
    const timestamp = new Date().toLocaleTimeString();
    this.outputChannel.appendLine(`[${timestamp}] ℹ️ ${message}`);
  }
}
exports.CopilotIntegrationHandler = CopilotIntegrationHandler;
//# sourceMappingURL=copilot-integration.js.map
