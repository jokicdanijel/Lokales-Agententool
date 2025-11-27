import * as vscode from 'vscode';

interface VoiceInputConfig {
    language: string;
    autoSend: boolean;
    silenceTimeout: number;
    feedbackVolume: number;
}

class VoiceInputManager {
    private recognition: any;
    private isListening: boolean = false;
    private statusBarItem: vscode.StatusBarItem;
    private outputChannel: vscode.OutputChannel;
    private transcriptBuffer: string = '';
    private config: VoiceInputConfig;

    constructor(context: vscode.ExtensionContext) {
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        this.outputChannel = vscode.window.createOutputChannel('Voice Input');
        this.config = this.loadConfig();
        this.initRecognition();
    }

    private loadConfig(): VoiceInputConfig {
        const config = vscode.workspace.getConfiguration('voice-input');
        return {
            language: config.get('language') || 'de-DE',
            autoSend: config.get('autoSend') || false,
            silenceTimeout: config.get('silenceTimeout') || 2000,
            feedbackVolume: config.get('feedbackVolume') || 0.5
        };
    }

    private initRecognition() {
        // Web Speech API
        const SpeechRecognition = (window as any).SpeechRecognition ||
                                  (window as any).webkitSpeechRecognition;

        if (!SpeechRecognition) {
            vscode.window.showErrorMessage(
                'Speech Recognition not supported in your environment'
            );
            return;
        }

        this.recognition = new SpeechRecognition();
        this.recognition.continuous = true;
        this.recognition.interimResults = true;
        this.recognition.lang = this.config.language;

        this.setupRecognitionHandlers();
    }

    private setupRecognitionHandlers() {
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateStatusBar('🎙️ Listening...', true);
            this.outputChannel.appendLine(`[${new Date().toLocaleTimeString()}] Started listening`);
        };

        this.recognition.onresult = (event: any) => {
            let interimTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;

                if (event.results[i].isFinal) {
                    this.transcriptBuffer += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }

            this.updateStatusBar(
                `🎤 ${interimTranscript || this.transcriptBuffer}`,
                true
            );
        };

        this.recognition.onerror = (event: any) => {
            this.outputChannel.appendLine(`[ERROR] ${event.error}`);
            vscode.window.showErrorMessage(`Speech error: ${event.error}`);
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.updateStatusBar('🎤 Ready', false);
            this.handleTranscript();
        };
    }

    private handleTranscript() {
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

    private sendToCopilot(text: string) {
        // Simulate sending to Copilot Chat
        try {
            vscode.commands.executeCommand(
                'github.copilot.interactiveEditor.makeRequest',
                text
            );
        } catch {
            // Fallback: Show in output
            this.outputChannel.appendLine(`[To Copilot] ${text}`);
        }
    }

    public start() {
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

    public stop() {
        if (!this.isListening) {
            return;
        }
        this.recognition.stop();
    }

    public toggle() {
        if (this.isListening) {
            this.stop();
        } else {
            this.start();
        }
    }

    private updateStatusBar(text: string, isActive: boolean) {
        this.statusBarItem.text = text;
        this.statusBarItem.show();

        if (isActive) {
            this.statusBarItem.backgroundColor = new vscode.ThemeColor(
                'statusBarItem.warningBackground'
            );
        } else {
            this.statusBarItem.backgroundColor = undefined;
        }
    }

    public getOutputChannel(): vscode.OutputChannel {
        return this.outputChannel;
    }
}

export function activate(context: vscode.ExtensionContext) {
    const voiceManager = new VoiceInputManager(context);

    const startCommand = vscode.commands.registerCommand(
        'voice-input.start',
        () => voiceManager.start()
    );

    const stopCommand = vscode.commands.registerCommand(
        'voice-input.stop',
        () => voiceManager.stop()
    );

    const toggleCommand = vscode.commands.registerCommand(
        'voice-input.toggle',
        () => voiceManager.toggle()
    );

    context.subscriptions.push(startCommand, stopCommand, toggleCommand);

    vscode.window.showInformationMessage(
        '🎤 Voice Input Extension loaded! Press Ctrl+Shift+V to toggle.'
    );
}

export function deactivate() {}
