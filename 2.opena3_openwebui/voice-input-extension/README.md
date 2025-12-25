# Voice Input for Copilot - VS Code Extension

🎤 Real-time voice input integration for GitHub Copilot in VS Code

## Features

✨ **Real-time Voice Recognition**

- Continuous speech-to-text conversion
- Multi-language support (DE, EN, FR, ES)
- Interim results preview

✨ **Copilot Integration**

- Direct voice input to Copilot Chat
- Auto-send capability
- Seamless workflow

✨ **Accessibility**

- Keyboard shortcuts
- Status bar indicators
- Output logging

✨ **Customization**

- Language selection
- Silence timeout
- Feedback volume
- Auto-send toggle

## Installation

### From VS Code Marketplace

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Voice Input for Copilot"
4. Click Install

### From Source

```bash
git clone https://github.com/portier/voice-input-copilot.git
cd voice-input-copilot
npm install
npm run compile
# Press F5 in VS Code to launch extension
```

## Usage

### Start Recording

**Keyboard Shortcut:** `Ctrl+Shift+V` (Windows/Linux) or `Cmd+Shift+V` (macOS)

Or use Command Palette:

- `Ctrl+Shift+P` → "Voice Input: Toggle Voice Input"
- `Ctrl+Shift+P` → "Voice Input: Start Voice Input"
- `Ctrl+Shift+P` → "Voice Input: Stop Voice Input"

### Status Bar

When recording, the status bar shows:

- 🎙️ Listening... (active recording)
- 🎤 Ready (ready to record)
- Transcript preview

### Send to Copilot

Once recording stops:

1. Transcript is inserted into editor
2. If `autoSend` is enabled, automatically sent to Copilot
3. Check Output channel for logs

## Configuration

Open `settings.json` (Ctrl+Shift+P → "Preferences: Open Settings (JSON)")

```json
{
  "voice-input.language": "de-DE",
  "voice-input.autoSend": false,
  "voice-input.silenceTimeout": 2000,
  "voice-input.feedbackVolume": 0.5
}
```

### Settings Explained

| Setting          | Type    | Default | Description                     |
| ---------------- | ------- | ------- | ------------------------------- |
| `language`       | string  | `de-DE` | Speech recognition language     |
| `autoSend`       | boolean | `false` | Auto-send transcript to Copilot |
| `silenceTimeout` | number  | `2000`  | Silence timeout in ms           |
| `feedbackVolume` | number  | `0.5`   | Feedback volume (0-1)           |

### Supported Languages

- 🇩🇪 German (de-DE)
- 🇺🇸 English US (en-US)
- 🇬🇧 English UK (en-GB)
- 🇫🇷 French (fr-FR)
- 🇪🇸 Spanish (es-ES)

## Examples

### Example 1: Quick Copilot Prompt

1. Press `Ctrl+Shift+V`
2. Say: "Create a function to calculate fibonacci"
3. Extension sends to Copilot
4. Copilot generates code

### Example 2: Code Comment via Voice

1. Position cursor in code
2. Press `Ctrl+Shift+V`
3. Say: "Function that handles user authentication"
4. Transcript inserted as comment
5. Continue typing

### Example 3: Multi-language Support

1. Open Settings
2. Change `voice-input.language` to `en-US`
3. Press `Ctrl+Shift+V`
4. Speak in English
5. Transcript recognized in English

## Keyboard Shortcuts

| Shortcut                              | Action             |
| ------------------------------------- | ------------------ |
| `Ctrl+Shift+V`                        | Toggle Voice Input |
| `Ctrl+Shift+P` → "Voice Input: Start" | Start Recording    |
| `Ctrl+Shift+P` → "Voice Input: Stop"  | Stop Recording     |

## Output Logging

Access logs via Output Panel:

1. Open Output Panel: `Ctrl+Shift+U`
2. Select "Voice Input" from dropdown
3. View real-time logs

Log includes:

- Started/stopped timestamps
- Recognition events
- Transcripts
- Errors

## Requirements

- VS Code 1.80.0+
- Modern browser engine (Chromium-based)
- Microphone access permission
- Internet connection (for cloud-based recognition)

## Troubleshooting

### "Speech Recognition not supported"

- Use a Chromium-based browser or VS Code
- Check microphone permissions
- Enable experimental features if needed

### Transcript not appearing

- Check microphone is working
- Verify microphone permissions
- Check language setting matches speech language
- Review Output channel for errors

### Connection issues

- Check internet connection
- Verify microphone is not blocked by firewall
- Restart VS Code
- Check if service is available

### Incorrect recognition

- Speak clearly and slowly
- Check language setting matches spoken language
- Reduce background noise
- Adjust microphone settings

## Performance Tips

1. **Reduce latency**
   - Increase `silenceTimeout` value
   - Use wired microphone instead of wireless

2. **Better accuracy**
   - Reduce background noise
   - Speak clearly
   - Match language setting to spoken language

3. **Save resources**
   - Disable `autoSend` if not needed
   - Close output channel when not debugging

## Privacy & Security

- ✅ Microphone data sent directly to recognition service
- ✅ No data stored locally beyond current session
- ✅ No tracking or analytics
- ✅ Compliant with VS Code privacy policies

## Development

### Build Extension

```bash
npm run compile
```

### Watch Mode

```bash
npm run watch
```

### Run Tests

```bash
npm test
```

### Lint Code

```bash
npm run lint
```

## Contributing

Contributions welcome! Please:

1. Fork repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## License

MIT License - See LICENSE file

## Support

- 📧 Email: support@portier.dev
- 🐛 Issues: GitHub Issues
- 💬 Discussions: GitHub Discussions
- 📖 Docs: https://portier.dev/voice-input

## Changelog

### Version 1.0.0 (2025-11-25)

- ✨ Initial release
- 🎤 Real-time voice recognition
- 🤖 Copilot integration
- 🌍 Multi-language support
- ⌨️ Keyboard shortcuts
- 📊 Output logging

---

Made with ❤️ by Portier HyperSuite
