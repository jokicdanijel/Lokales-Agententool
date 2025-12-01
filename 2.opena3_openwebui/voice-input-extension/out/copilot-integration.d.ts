import * as vscode from 'vscode';
/**
 * Copilot Integration Handler
 * Manages communication with GitHub Copilot
 */
export declare class CopilotIntegrationHandler {
    private outputChannel;
    constructor(outputChannel: vscode.OutputChannel);
    /**
     * Send transcript to Copilot Chat
     */
    sendToCopilotChat(transcript: string): Promise<boolean>;
    /**
     * Insert transcript into editor at cursor
     */
    insertIntoEditor(transcript: string): Promise<boolean>;
    /**
     * Process transcript (auto-send or insert based on config)
     */
    processTranscript(transcript: string, autoSend: boolean): Promise<void>;
    /**
     * Detect if transcript is a Copilot command
     */
    isCopilotCommand(transcript: string): boolean;
    /**
     * Format transcript for Copilot
     */
    formatForCopilot(transcript: string): string;
    /**
     * Log success message
     */
    private logSuccess;
    /**
     * Log error message
     */
    private logError;
    /**
     * Log info message
     */
    logInfo(message: string): void;
}
//# sourceMappingURL=copilot-integration.d.ts.map