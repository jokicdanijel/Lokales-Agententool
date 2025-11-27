import * as vscode from 'vscode';
import { AnalyticsManager, EventLogger, VoiceSession, globalAnalytics, globalEventLogger } from './analytics';
import { CommandHandler } from './commands';
import { CopilotIntegrationHandler } from './copilot-integration';
import { VoiceRecognitionEngine } from './recognition-engine';
import { VoiceInputSettings } from './settings';

interface Transcript {
    text: string;
    isFinal: boolean;
    confidence: number;
    timestamp: Date;
}

/**
 * Advanced Voice Input Manager for VS Code
 * Full integration with all modules: recognition, settings, Copilot, commands, analytics
 */
class AdvancedVoiceInputManager {
    private recognitionEngine: VoiceRecognitionEngine;
    private settings: VoiceInputSettings;
    private copilotHandler: CopilotIntegrationHandler;
    private commandHandler: CommandHandler;
    private statusBar: vscode.StatusBarItem;
    private outputChannel: vscode.OutputChannel;
    private isRecording: boolean = false;
    private sessionId: string = '';
    private sessionStartTime: Date = new Date();
    private analytics: AnalyticsManager;
    private eventLogger: EventLogger;

    constructor() {
        // Initialize dependencies
        this.outputChannel = vscode.window.createOutputChannel('Voice Input');
        this.settings = new VoiceInputSettings();
        this.copilotHandler = new CopilotIntegrationHandler(this.outputChannel);
        this.analytics = globalAnalytics;
        this.eventLogger = globalEventLogger;

        // Initialize recognition engine
        const defaultLanguage = this.settings.getDefaultLanguage();
        this.recognitionEngine = new VoiceRecognitionEngine(defaultLanguage);

        // Create command handler
        this.commandHandler = new CommandHandler(
            this.settings,
            this.copilotHandler,
            this.analytics,
            this.eventLogger,
            this.outputChannel
        );

        // Create status bar item
        this.statusBar = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        this.statusBar.command = 'voiceInput.toggle';
        this.updateStatusBar();

        this.setupRecognitionHandlers();
        this.setupSettingsWatcher();

        this.log('🚀 Advanced Voice Input Manager initialized');
    }

    /**
     * Setup recognition engine handlers
     */
    private setupRecognitionHandlers(): void {
        this.recognitionEngine.onTranscript = (transcript: string, isFinal: boolean) => {
            this.handleTranscript(transcript, isFinal);
        };

        this.recognitionEngine.onError = (error: string) => {
            this.handleError(error);
        };

        this.recognitionEngine.onEnd = () => {
            this.handleEnd();
        };

        this.recognitionEngine.onStart = () => {
            this.sessionId = this.generateSessionId();
            this.sessionStartTime = new Date();
            this.log('🎙️ Recording session started: ' + this.sessionId);
        };
    }

    /**
     * Setup settings watcher
     */
    private setupSettingsWatcher(): void {
        this.settings.onSettingsChanged(() => {
            this.log('⚙️ Settings updated');
            this.updateStatusBar();
        });
    }

    /**
     * Generate session ID
     */
    private generateSessionId(): string {
        return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Start voice recognition
     */
    public start(): void {
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
        this.eventLogger.info('Voice recognition started', { language });
    }

    /**
     * Stop voice recognition
     */
    public stop(): void {
        if (!this.isRecording) {
            return;
        }

        this.isRecording = false;
        this.recognitionEngine.stop();
        this.updateStatusBar();
        this.eventLogger.info('Voice recognition stopped');
    }

    /**
     * Toggle voice recognition
     */
    public toggle(): void {
        if (this.isRecording) {
            this.stop();
        } else {
            this.start();
        }
    }

    /**
     * Handle transcript from recognition engine
     */
    private async handleTranscript(transcript: string, isFinal: boolean): Promise<void> {
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
    private handleError(error: string): void {
        this.log(`❌ Error: ${error}`);
        this.eventLogger.error('Recognition error', { error });

        // Record failed session
        this.recordSession('', false, error);

        if (this.settings.isNotificationOnEndEnabled()) {
            vscode.window.showErrorMessage(`Voice Input Error: ${error}`);
        }
    }

    /**
     * Handle recognition end
     */
    private handleEnd(): void {
        this.isRecording = false;
        this.updateStatusBar();
        this.log('🛑 Voice recognition stopped');
        this.eventLogger.info('Recognition session ended');
    }

    /**
     * Record session for analytics
     */
    private recordSession(transcript: string, success: boolean, error?: string): void {
        const session: VoiceSession = {
            sessionId: this.sessionId,
            startTime: this.sessionStartTime,
            endTime: new Date(),
            language: this.settings.getDefaultLanguage(),
            transcriptLength: transcript.length,
            isFinal: success,
            confidence: success ? 0.95 : 0,
            sentToCopilot: this.settings.isAutoSendEnabled() && success,
            errorMessage: error
        };

        this.analytics.recordSession(session);
    }

    /**
     * Get command handler
     */
    public getCommandHandler(): CommandHandler {
        return this.commandHandler;
    }

    /**
     * Update status bar
     */
    private updateStatusBar(): void {
        const statusBar = this.settings.isStatusBarEnabled();

        if (!statusBar) {
            this.statusBar.hide();
            return;
        }

        const status = this.isRecording ? '🎙️ Recording...' : '🎤 Ready';
        this.statusBar.text = status;
        this.statusBar.tooltip = 'Click to toggle voice recognition (Ctrl+Shift+V)';
        this.statusBar.show();
    }

    /**
     * Log message to output channel
     */
    private log(message: string): void {
        const timestamp = new Date().toLocaleTimeString();
        this.outputChannel.appendLine(`[${timestamp}] ${message}`);

        if (this.settings.isOutputChannelVisible()) {
            this.outputChannel.show(true);
        }
    }

    /**
     * Show output channel
     */
    public showOutput(): void {
        this.outputChannel.show();
    }

    /**
     * Dispose resources
     */
    public dispose(): void {
        this.statusBar.dispose();
        this.outputChannel.dispose();
        if (this.recognitionEngine) {
            this.recognitionEngine.abort();
        }
    }
}

let manager: AdvancedVoiceInputManager;

/**
 * Extension activation - Advanced Version
 */
export function activate(context: vscode.ExtensionContext) {
    manager = new AdvancedVoiceInputManager();
    const commandHandler = manager.getCommandHandler();

    // Register core commands
    context.subscriptions.push(
        vscode.commands.registerCommand('voiceInput.toggle', () => {
            manager.toggle();
        }),
        vscode.commands.registerCommand('voiceInput.start', () => {
            manager.start();
        }),
        vscode.commands.registerCommand('voiceInput.stop', () => {
            manager.stop();
        }),
        vscode.commands.registerCommand('voiceInput.showOutput', () => {
            manager.showOutput();
        }),

        // Settings and configuration commands
        vscode.commands.registerCommand('voiceInput.showSettings', () => {
            commandHandler.showSettings();
        }),
        vscode.commands.registerCommand('voiceInput.switchLanguage', () => {
            commandHandler.switchLanguage();
        }),
        vscode.commands.registerCommand('voiceInput.toggleContinuousMode', () => {
            commandHandler.toggleContinuousMode();
        }),

        // Analytics commands
        vscode.commands.registerCommand('voiceInput.showAnalytics', () => {
            commandHandler.showAnalytics();
        }),
        vscode.commands.registerCommand('voiceInput.exportAnalytics', () => {
            commandHandler.exportAnalytics();
        }),
        vscode.commands.registerCommand('voiceInput.clearHistory', () => {
            commandHandler.clearHistory();
        }),

        // Help and utilities
        vscode.commands.registerCommand('voiceInput.showHelp', () => {
            commandHandler.showHelp();
        }),
        vscode.commands.registerCommand('voiceInput.testMicrophone', () => {
            commandHandler.testMicrophone();
        }),
        vscode.commands.registerCommand('voiceInput.resetSettings', () => {
            commandHandler.resetSettings();
        })
    );

    console.log('✅ Advanced Voice Input Extension activated');
    globalEventLogger.info('Advanced extension activated successfully');
}

/**
 * Extension deactivation
 */
export function deactivate() {
    if (manager) {
        manager.dispose();
    }
    console.log('✅ Voice Input Extension deactivated');
    globalEventLogger.info('Extension deactivated');
}
