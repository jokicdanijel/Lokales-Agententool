import * as vscode from 'vscode';

/**
 * Settings Management for Voice Input Extension
 */
export class VoiceInputSettings {
    private config: vscode.WorkspaceConfiguration;

    constructor() {
        this.config = vscode.workspace.getConfiguration('voiceInput');
    }

    // ===== RECOGNITION SETTINGS =====

    /**
     * Get enabled languages for recognition
     */
    public getLanguages(): string[] {
        return this.config.get<string[]>('languages', ['de', 'en']);
    }

    /**
     * Get default language
     */
    public getDefaultLanguage(): string {
        return this.config.get<string>('defaultLanguage', 'de');
    }

    /**
     * Get silence threshold in ms
     */
    public getSilenceThreshold(): number {
        return this.config.get<number>('silenceThreshold', 2000);
    }

    /**
     * Get max recording duration in seconds
     */
    public getMaxDuration(): number {
        return this.config.get<number>('maxDuration', 60);
    }

    // ===== COPILOT INTEGRATION SETTINGS =====

    /**
     * Check if auto-send to Copilot is enabled
     */
    public isAutoSendEnabled(): boolean {
        return this.config.get<boolean>('autoSend', false);
    }

    /**
     * Check if Copilot command detection is enabled
     */
    public isCopilotCommandDetectionEnabled(): boolean {
        return this.config.get<boolean>('detectCopilotCommands', true);
    }

    /**
     * Check if auto-focus editor after insertion
     */
    public isAutoFocusEditorEnabled(): boolean {
        return this.config.get<boolean>('autoFocusEditor', true);
    }

    // ===== UI/UX SETTINGS =====

    /**
     * Check if status bar is enabled
     */
    public isStatusBarEnabled(): boolean {
        return this.config.get<boolean>('showStatusBar', true);
    }

    /**
     * Get status bar position
     */
    public getStatusBarPosition(): 'left' | 'right' {
        return this.config.get<'left' | 'right'>('statusBarPosition', 'right');
    }

    /**
     * Check if output channel should be shown
     */
    public isOutputChannelVisible(): boolean {
        return this.config.get<boolean>('showOutput', true);
    }

    /**
     * Check if sounds are enabled
     */
    public areSoundsEnabled(): boolean {
        return this.config.get<boolean>('enableSounds', true);
    }

    /**
     * Get sound volume (0-1)
     */
    public getSoundVolume(): number {
        const volume = this.config.get<number>('soundVolume', 0.5);
        return Math.max(0, Math.min(1, volume));
    }

    /**
     * Check if notification on end is enabled
     */
    public isNotificationOnEndEnabled(): boolean {
        return this.config.get<boolean>('notifyOnEnd', true);
    }

    // ===== ADVANCED SETTINGS =====

    /**
     * Get continuous mode (keep listening between transcripts)
     */
    public isContinuousModeEnabled(): boolean {
        return this.config.get<boolean>('continuousMode', false);
    }

    /**
     * Get interim results display (show partial transcripts)
     */
    public isInterimResultsEnabled(): boolean {
        return this.config.get<boolean>('showInterimResults', true);
    }

    /**
     * Get confidence threshold (0-1)
     */
    public getConfidenceThreshold(): number {
        const threshold = this.config.get<number>('confidenceThreshold', 0.5);
        return Math.max(0, Math.min(1, threshold));
    }

    /**
     * Get keyboard shortcut custom key
     */
    public getCustomKeybinding(): string {
        return this.config.get<string>('customKeybinding', 'ctrl+shift+v');
    }

    // ===== SETTER METHODS =====

    /**
     * Update setting value
     */
    public async updateSetting(
        key: string,
        value: any,
        global: boolean = false
    ): Promise<void> {
        const target = global ?
            vscode.ConfigurationTarget.Global :
            vscode.ConfigurationTarget.Workspace;

        await this.config.update(key, value, target);

        // Refresh config reference
        this.config = vscode.workspace.getConfiguration('voiceInput');
    }

    /**
     * Get all settings as object
     */
    public getAllSettings(): Record<string, any> {
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
            customKeybinding: this.getCustomKeybinding()
        };
    }

    /**
     * Reset all settings to defaults
     */
    public async resetToDefaults(): Promise<void> {
        const settings = [
            'languages', 'defaultLanguage', 'silenceThreshold', 'maxDuration',
            'autoSend', 'detectCopilotCommands', 'autoFocusEditor',
            'showStatusBar', 'statusBarPosition', 'showOutput',
            'enableSounds', 'soundVolume', 'notifyOnEnd',
            'continuousMode', 'showInterimResults', 'confidenceThreshold',
            'customKeybinding'
        ];

        for (const setting of settings) {
            await this.config.update(setting, undefined, vscode.ConfigurationTarget.Workspace);
        }

        this.config = vscode.workspace.getConfiguration('voiceInput');
    }

    /**
     * Watch for setting changes
     */
    public onSettingsChanged(callback: () => void): vscode.Disposable {
        return vscode.workspace.onDidChangeConfiguration((event) => {
            if (event.affectsConfiguration('voiceInput')) {
                this.config = vscode.workspace.getConfiguration('voiceInput');
                callback();
            }
        });
    }
}
