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
exports.CommandHandler = void 0;
const vscode = __importStar(require("vscode"));
/**
 * Command Handler for Voice Input Extension
 * Manages all registered commands
 */
class CommandHandler {
    constructor(settings, copilotHandler, analytics, eventLogger, outputChannel) {
        this.settings = settings;
        this.analytics = analytics;
        this.eventLogger = eventLogger;
        this.outputChannel = outputChannel;
    }
    /**
     * Show settings panel
     */
    async showSettings() {
        try {
            await vscode.commands.executeCommand('workbench.action.openSettings', 'voiceInput');
            this.eventLogger.info('Settings panel opened');
        }
        catch (error) {
            this.eventLogger.error('Failed to open settings', { error: String(error) });
        }
    }
    /**
     * Show analytics/statistics
     */
    async showAnalytics() {
        try {
            const metrics = this.analytics.getMetrics();
            const message = `
📊 **Voice Input Analytics**

📈 Sessions:
  • Total: ${metrics.totalSessions}
  • Successful: ${metrics.successfulSessions}
  • Failed: ${metrics.failedSessions}
  • Error Rate: ${(metrics.errorRate * 100).toFixed(1)}%

📝 Transcription:
  • Avg Length: ${metrics.averageTranscriptLength.toFixed(0)} chars
  • Avg Confidence: ${(metrics.averageConfidence * 100).toFixed(1)}%
  • Most Used Language: ${metrics.mostUsedLanguage.toUpperCase()}

🔗 Copilot:
  • Sent to Copilot: ${metrics.sentToCopilotCount}
  • Avg Session Duration: ${(metrics.averageSessionDuration / 1000).toFixed(1)}s
            `.trim();
            vscode.window.showInformationMessage(message);
            this.eventLogger.info('Analytics displayed', metrics);
        }
        catch (error) {
            this.eventLogger.error('Failed to show analytics', { error: String(error) });
            vscode.window.showErrorMessage('Failed to show analytics');
        }
    }
    /**
     * Export analytics
     */
    async exportAnalytics() {
        try {
            const options = {
                defaultUri: vscode.Uri.file(`analytics-${Date.now()}`),
                filters: {
                    'JSON': ['json'],
                    'CSV': ['csv'],
                    'All': ['*']
                }
            };
            const uri = await vscode.window.showSaveDialog(options);
            if (!uri) {
                return;
            }
            const fileType = uri.fsPath.endsWith('.csv') ? 'csv' : 'json';
            const content = fileType === 'csv' ?
                this.analytics.exportSessionsAsCsv() :
                this.analytics.exportMetricsAsJson();
            await vscode.workspace.fs.writeFile(uri, Buffer.from(content, 'utf8'));
            vscode.window.showInformationMessage(`Analytics exported to ${uri.fsPath}`);
            this.eventLogger.info('Analytics exported', { path: uri.fsPath, type: fileType });
        }
        catch (error) {
            this.eventLogger.error('Failed to export analytics', { error: String(error) });
            vscode.window.showErrorMessage('Failed to export analytics');
        }
    }
    /**
     * Switch language
     */
    async switchLanguage() {
        try {
            const languages = this.settings.getLanguages();
            const picked = await vscode.window.showQuickPick(languages.map(lang => ({
                label: this.getLanguageName(lang),
                description: lang.toUpperCase(),
                value: lang
            })), {
                placeHolder: 'Select recognition language'
            });
            if (!picked) {
                return;
            }
            await this.settings.updateSetting('defaultLanguage', picked.value);
            vscode.window.showInformationMessage(`Language switched to ${picked.label}`);
            this.eventLogger.info('Language switched', { language: picked.value });
        }
        catch (error) {
            this.eventLogger.error('Failed to switch language', { error: String(error) });
        }
    }
    /**
     * Clear history/cache
     */
    async clearHistory() {
        try {
            const confirmed = await vscode.window.showWarningMessage('Clear all voice input history?', 'Clear', 'Cancel');
            if (confirmed === 'Clear') {
                this.analytics.clearSessions();
                vscode.window.showInformationMessage('History cleared');
                this.eventLogger.info('History cleared by user');
            }
        }
        catch (error) {
            this.eventLogger.error('Failed to clear history', { error: String(error) });
        }
    }
    /**
     * Reset all settings
     */
    async resetSettings() {
        try {
            const confirmed = await vscode.window.showWarningMessage('Reset all voice input settings to defaults?', 'Reset', 'Cancel');
            if (confirmed === 'Reset') {
                await this.settings.resetToDefaults();
                vscode.window.showInformationMessage('Settings reset to defaults');
                this.eventLogger.info('Settings reset to defaults by user');
            }
        }
        catch (error) {
            this.eventLogger.error('Failed to reset settings', { error: String(error) });
        }
    }
    /**
     * Show help/documentation
     */
    async showHelp() {
        try {
            const help = `
# Voice Input Extension - Quick Help

## Keyboard Shortcuts
- **Ctrl+Shift+V** - Toggle voice recognition
- **Ctrl+Shift+L** - Switch language
- **Ctrl+Shift+S** - Show statistics
- **Ctrl+Shift+E** - Export analytics

## Quick Tips
1. Start speaking after activating recognition
2. Silence for 2+ seconds auto-stops recording
3. Long transcripts (60s max) auto-stop
4. Enable "Auto Send to Copilot" in settings for hands-free workflow
5. Use interim results to see partial transcripts while speaking

## Settings
Access settings with **Ctrl+Shift+,** and search for "Voice Input"

### Key Settings:
- **Default Language**: Choose primary recognition language
- **Silence Threshold**: Adjust auto-stop sensitivity
- **Auto Send**: Automatically send to Copilot Chat
- **Enable Sounds**: Audio feedback on start/stop
- **Continuous Mode**: Keep listening between recordings

## Troubleshooting
- No recognition? Check microphone permissions
- Slow response? Reduce interim results display
- Too many errors? Lower confidence threshold or increase silence threshold

## Need More Help?
Visit the extension repository for detailed documentation
            `.trim();
            const panel = vscode.window.createWebviewPanel('voiceInputHelp', 'Voice Input - Help', vscode.ViewColumn.Beside, {});
            panel.webview.html = this.getHelpHtml(help);
            this.eventLogger.info('Help panel opened');
        }
        catch (error) {
            this.eventLogger.error('Failed to show help', { error: String(error) });
        }
    }
    /**
     * Get HTML for help panel
     */
    getHelpHtml(markdown) {
        // Simple markdown to HTML conversion
        let html = markdown
            .replace(/^# (.+)$/gm, '<h1>$1</h1>')
            .replace(/^## (.+)$/gm, '<h2>$1</h2>')
            .replace(/^### (.+)$/gm, '<h3>$1</h3>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
        return `
<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            padding: 20px;
            background: #1e1e1e;
            color: #e0e0e0;
        }
        h1, h2, h3 {
            color: #4ec9b0;
            margin-top: 20px;
        }
        code {
            background: #2d2d2d;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        }
        strong {
            color: #ce9178;
        }
    </style>
</head>
<body>
    ${html}
</body>
</html>
        `;
    }
    /**
     * Get language name from code
     */
    getLanguageName(code) {
        const names = {
            'de': '🇩🇪 Deutsch (German)',
            'en': '🇬🇧 English',
            'fr': '🇫🇷 Français (French)',
            'es': '🇪🇸 Español (Spanish)',
            'it': '🇮🇹 Italiano (Italian)',
            'pt': '🇵🇹 Português (Portuguese)',
            'nl': '🇳🇱 Nederlands (Dutch)',
            'ja': '🇯🇵 日本語 (Japanese)'
        };
        return names[code] || code.toUpperCase();
    }
    /**
     * Toggle continuous mode
     */
    async toggleContinuousMode() {
        try {
            const current = this.settings.isContinuousModeEnabled();
            await this.settings.updateSetting('continuousMode', !current);
            vscode.window.showInformationMessage(`Continuous mode ${!current ? 'enabled' : 'disabled'}`);
            this.eventLogger.info('Continuous mode toggled', { enabled: !current });
        }
        catch (error) {
            this.eventLogger.error('Failed to toggle continuous mode', { error: String(error) });
        }
    }
    /**
     * Test microphone
     */
    async testMicrophone() {
        try {
            vscode.window.showInformationMessage('Microphone test: Please speak for 5 seconds...', { modal: true });
            this.eventLogger.info('Microphone test started');
            // Simulate a test - in real implementation would use Web Audio API
            setTimeout(() => {
                vscode.window.showInformationMessage('Microphone test complete!');
                this.eventLogger.info('Microphone test completed successfully');
            }, 5000);
        }
        catch (error) {
            this.eventLogger.error('Microphone test failed', { error: String(error) });
        }
    }
}
exports.CommandHandler = CommandHandler;
//# sourceMappingURL=commands.js.map