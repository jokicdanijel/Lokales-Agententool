"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
exports.deactivate = deactivate;
const vscode = __importStar(require("vscode"));
class VoiceInputManager {
    constructor(context) {
        this.isListening = false;
        this.transcriptBuffer = '';
        this.statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
        this.outputChannel = vscode.window.createOutputChannel('Voice Input');
        this.config = this.loadConfig();
        this.initRecognition();
    }
    loadConfig() {
        const config = vscode.workspace.getConfiguration('voice-input');
        return {
            language: config.get('language') || 'de-DE',
            autoSend: config.get('autoSend') || false,
            silenceTimeout: config.get('silenceTimeout') || 2000,
            feedbackVolume: config.get('feedbackVolume') || 0.5
        };
    }
    initRecognition() {
        // Web Speech API
        const SpeechRecognition = window.SpeechRecognition ||
            window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            vscode.window.showErrorMessage('Speech Recognition not supported in your environment');
            return;
        }
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = this.config.language;
        this.setupRecognitionHandlers();
    }
    setupRecognitionHandlers() {
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateStatusBar('🎙️ Listening...', true);
            this.outputChannel.appendLine(`[${new Date().toLocaleTimeString()}] Started listening`);
        };
        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    this.transcriptBuffer += transcript + ' ';
                }
                else {
                    interimTranscript += transcript;
                }
            }
            this.updateStatusBar(`🎤 ${interimTranscript || this.transcriptBuffer}`, true);
        };
        this.recognition.onerror = (event) => {
            this.outputChannel.appendLine(`[ERROR] ${event.error}`);
            vscode.window.showErrorMessage(`Speech error: ${event.error}`);
        };
        this.recognition.onend = () => {
            this.isListening = false;
            this.updateStatusBar('🎤 Ready', false);
            this.handleTranscript();
        };
    }
    handleTranscript() {
        if (!this.transcriptBuffer.trim()) {
            return;
        }
        const transcript = this.transcriptBuffer.trim();
        this.outputChannel.appendLine(`[Transcript] ${transcript}`);
        // Insert into editor
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            editor.edit(editBuilder => {
                editBuilder.insert(editor.selection.active, transcript + ' ');
            });
        }
        // Auto-send to Copilot if enabled
        if (this.config.autoSend) {
            this.sendToCopilot(transcript);
        }
        this.transcriptBuffer = '';
    }
    sendToCopilot(text) {
        // Simulate sending to Copilot Chat
        try {
            vscode.commands.executeCommand('github.copilot.interactiveEditor.makeRequest', text);
        }
        catch {
            // Fallback: Show in output
            this.outputChannel.appendLine(`[To Copilot] ${text}`);
        }
    }
    start() {
        if (this.isListening) {
            return;
        }
        if (!this.recognition) {
            vscode.window.showErrorMessage('Speech Recognition not available');
            return;
        }
        this.transcriptBuffer = '';
        this.recognition.start();
    }
    stop() {
        if (!this.isListening) {
            return;
        }
        this.recognition.stop();
    }
    toggle() {
        if (this.isListening) {
            this.stop();
        }
        else {
            this.start();
        }
    }
    updateStatusBar(text, isActive) {
        this.statusBarItem.text = text;
        this.statusBarItem.show();
        if (isActive) {
            this.statusBarItem.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
        }
        else {
            this.statusBarItem.backgroundColor = undefined;
        }
    }
    getOutputChannel() {
        return this.outputChannel;
    }
}
function activate(context) {
    const voiceManager = new VoiceInputManager(context);
    const startCommand = vscode.commands.registerCommand('voice-input.start', () => voiceManager.start());
    const stopCommand = vscode.commands.registerCommand('voice-input.stop', () => voiceManager.stop());
    const toggleCommand = vscode.commands.registerCommand('voice-input.toggle', () => voiceManager.toggle());
    context.subscriptions.push(startCommand, stopCommand, toggleCommand);
    vscode.window.showInformationMessage('🎤 Voice Input Extension loaded! Press Ctrl+Shift+V to toggle.');
}
function deactivate() { }
//# sourceMappingURL=extension.js.map