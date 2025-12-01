import * as vscode from 'vscode';

/**
 * Copilot Integration Handler
 * Manages communication with GitHub Copilot
 */
export class CopilotIntegrationHandler {
    private outputChannel: vscode.OutputChannel;

    constructor(outputChannel: vscode.OutputChannel) {
        this.outputChannel = outputChannel;
    }

    /**
     * Send transcript to Copilot Chat
     */
    public async sendToCopilotChat(transcript: string): Promise<boolean> {
        try {
            // Method 1: Try Copilot Chat API
            try {
                await vscode.commands.executeCommand(
                    'github.copilot.chat.openSymbolFromWorkspace',
                    transcript
                );
            } catch {
                // Method 2: Fallback to inline chat
                await vscode.commands.executeCommand(
                    'github.copilot.interactiveEditor.makeRequest',
                    transcript
                );
            }

            this.logSuccess('Sent to Copilot', transcript);
            return true;
        } catch (error) {
            this.logError('Failed to send to Copilot', error);
            return false;
        }
    }

    /**
     * Insert transcript into editor at cursor
     */
    public async insertIntoEditor(transcript: string): Promise<boolean> {
        const editor = vscode.window.activeTextEditor;

        if (!editor) {
            this.logError('No active editor', new Error('No active editor found'));
            return false;
        }

        try {
            await editor.edit((editBuilder) => {
                editBuilder.insert(editor.selection.active, transcript + ' ');
            });

            this.logSuccess('Inserted into editor', transcript);
            return true;
        } catch (error) {
            this.logError('Failed to insert into editor', error);
            return false;
        }
    }

    /**
     * Process transcript (auto-send or insert based on config)
     */
    public async processTranscript(
        transcript: string,
        autoSend: boolean
    ): Promise<void> {
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
    public isCopilotCommand(transcript: string): boolean {
        const copilotKeywords = [
            'generate',
            'create',
            'write',
            'explain',
            'refactor',
            'optimize',
            'fix',
            'debug',
            'test',
            'document',
            'comment',
            'function',
            'class',
            'method'
        ];

        const lowerTranscript = transcript.toLowerCase();
        return copilotKeywords.some(keyword =>
            lowerTranscript.includes(keyword)
        );
    }

    /**
     * Format transcript for Copilot
     */
    public formatForCopilot(transcript: string): string {
        // Remove extra spaces
        let formatted = transcript.replace(/\s+/g, ' ').trim();

        // Capitalize first letter
        if (formatted.length > 0) {
            formatted = formatted.charAt(0).toUpperCase() + formatted.slice(1);
        }

        // Add punctuation if missing
        if (!/[.!?]$/.test(formatted)) {
            formatted += '.';
        }

        return formatted;
    }

    /**
     * Log success message
     */
    private logSuccess(action: string, details: string): void {
        const timestamp = new Date().toLocaleTimeString();
        this.outputChannel.appendLine(
            `[${timestamp}] ✅ ${action}: ${details}`
        );
    }

    /**
     * Log error message
     */
    private logError(action: string, error: any): void {
        const timestamp = new Date().toLocaleTimeString();
        const errorMsg = error instanceof Error ? error.message : String(error);
        this.outputChannel.appendLine(
            `[${timestamp}] ❌ ${action}: ${errorMsg}`
        );
    }

    /**
     * Log info message
     */
    public logInfo(message: string): void {
        const timestamp = new Date().toLocaleTimeString();
        this.outputChannel.appendLine(`[${timestamp}] ℹ️ ${message}`);
    }
}
