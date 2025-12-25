const vscode = require("vscode");
const { PortierAPI } = require("./src/api");

let api;
let statusBarItem;
let outputChannel;
let isConnected = false;

/**
 * 🚀 PORTIER VSCode Extension 3.0 Activation
 * Enterprise AI-Dev Assistant mit opena5_vscode Integration
 */
async function activate(context) {
  console.log("🔥 PORTIER VSCode Extension 3.0 aktiviert!");

  // Initialisierung
  outputChannel = vscode.window.createOutputChannel("PORTIER");
  outputChannel.appendLine("🚀 PORTIER Extension 3.0 gestartet");

  // Konfiguration laden
  const config = vscode.workspace.getConfiguration("portier");
  const agentUrl = config.get("agentUrl", "http://127.0.0.1:12348");
  const bearerToken = config.get("bearerToken", "");

  // API Client initialisieren
  api = new PortierAPI(agentUrl, bearerToken);

  // Status Bar Setup
  setupStatusBar(context);

  // Commands registrieren
  registerCommands(context);

  // CodeLens Provider registrieren
  if (config.get("codeLensEnabled", true)) {
    registerCodeLensProvider(context);
  }

  // Auto-Connect
  if (config.get("autoConnect", true)) {
    await connectToAgent();
    setInterval(updateAgentStatus, 5000); // Alle 5 Sekunden
  }

  outputChannel.appendLine("✅ PORTIER Extension vollständig initialisiert");
}

/**
 * Status Bar Setup & Management
 */
function setupStatusBar(context) {
  statusBarItem = vscode.window.createStatusBarItem(
    vscode.StatusBarAlignment.Left,
    100,
  );

  statusBarItem.command = "portier.dashboard";
  statusBarItem.tooltip = "Click to open PORTIER Dashboard";
  statusBarItem.text = "$(loading~spin) PORTIER connecting...";
  statusBarItem.show();

  context.subscriptions.push(statusBarItem);
}

/**
 * Agent Status Update
 */
async function updateAgentStatus() {
  try {
    const health = await api.health();

    if (health && health.status === "ok") {
      isConnected = true;
      statusBarItem.text = "$(check) PORTIER opena5";
      statusBarItem.backgroundColor = undefined;
      vscode.commands.executeCommand("setContext", "portier:connected", true);
    } else {
      throw new Error("Agent not responding");
    }
  } catch (error) {
    isConnected = false;
    statusBarItem.text = "$(alert) PORTIER Disconnected";
    statusBarItem.backgroundColor = new vscode.ThemeColor(
      "statusBarItem.errorBackground",
    );
    vscode.commands.executeCommand("setContext", "portier:connected", false);

    outputChannel.appendLine(`❌ Connection error: ${error.message}`);
  }
}

/**
 * Initial Agent Connection
 */
async function connectToAgent() {
  outputChannel.appendLine("🔌 Connecting to PORTIER opena5_vscode agent...");

  try {
    const health = await api.health();
    outputChannel.appendLine(
      `✅ Connected to ${health.agent || "opena5_vscode"} agent`,
    );

    const status = await api.status();
    outputChannel.appendLine(
      `📊 Agent Status: ${JSON.stringify(status, null, 2)}`,
    );

    return true;
  } catch (error) {
    outputChannel.appendLine(`❌ Failed to connect: ${error.message}`);
    vscode.window.showErrorMessage(
      `PORTIER Connection Failed: ${error.message}`,
    );
    return false;
  }
}

/**
 * Commands Registration
 */
function registerCommands(context) {
  // PORTIER: Run Command
  context.subscriptions.push(
    vscode.commands.registerCommand("portier.runCommand", async () => {
      const cmd = await vscode.window.showInputBox({
        prompt: "Enter PORTIER Command (JSON payload)",
        placeHolder: '{"action": "analyze", "language": "python"}',
        validateInput: (value) => {
          try {
            JSON.parse(value);
            return null;
          } catch {
            return "Invalid JSON format";
          }
        },
      });

      if (cmd) {
        try {
          const response = await api.command(JSON.parse(cmd));
          outputChannel.appendLine(`📤 Command: ${cmd}`);
          outputChannel.appendLine(
            `📥 Response: ${JSON.stringify(response, null, 2)}`,
          );
          vscode.window.showInformationMessage(
            "PORTIER Command executed successfully",
          );
        } catch (error) {
          outputChannel.appendLine(`❌ Command failed: ${error.message}`);
          vscode.window.showErrorMessage(`Command failed: ${error.message}`);
        }
      }
    }),
  );

  // PORTIER: Analyze File
  context.subscriptions.push(
    vscode.commands.registerCommand("portier.analyzeFile", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showWarningMessage("No active editor");
        return;
      }

      const document = editor.document;
      const selection = editor.selection;
      const text = selection.isEmpty
        ? document.getText()
        : document.getText(selection);

      try {
        vscode.window.withProgress(
          {
            location: vscode.ProgressLocation.Notification,
            title: "🔍 PORTIER analyzing code...",
            cancellable: false,
          },
          async () => {
            const response = await api.specialized({
              action: "analyze",
              language: document.languageId,
              source: text,
              filename: document.fileName,
            });

            outputChannel.appendLine(
              `🔍 Analysis Result: ${JSON.stringify(response, null, 2)}`,
            );

            // Show analysis in new document
            const analysisDoc = await vscode.workspace.openTextDocument({
              content: `# PORTIER Code Analysis\\n\\n${response.analysis || response.result || "No analysis available"}`,
              language: "markdown",
            });
            await vscode.window.showTextDocument(analysisDoc);
          },
        );
      } catch (error) {
        outputChannel.appendLine(`❌ Analysis failed: ${error.message}`);
        vscode.window.showErrorMessage(`Analysis failed: ${error.message}`);
      }
    }),
  );

  // PORTIER: Auto-Refactor
  context.subscriptions.push(
    vscode.commands.registerCommand("portier.refactor", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showWarningMessage("No active editor");
        return;
      }

      const document = editor.document;
      const selection = editor.selection;
      const text = selection.isEmpty
        ? document.getText()
        : document.getText(selection);

      try {
        vscode.window.withProgress(
          {
            location: vscode.ProgressLocation.Notification,
            title: "🛠️ PORTIER refactoring code...",
            cancellable: false,
          },
          async () => {
            const response = await api.specialized({
              action: "refactor",
              language: document.languageId,
              source: text,
              filename: document.fileName,
            });

            if (response.output || response.refactored_code) {
              const newCode = response.output || response.refactored_code;
              await applyCodeChanges(editor, selection, newCode);
              vscode.window.showInformationMessage(
                "✅ Code refactored successfully",
              );
            } else {
              vscode.window.showWarningMessage(
                "No refactoring suggestions available",
              );
            }
          },
        );
      } catch (error) {
        outputChannel.appendLine(`❌ Refactoring failed: ${error.message}`);
        vscode.window.showErrorMessage(`Refactoring failed: ${error.message}`);
      }
    }),
  );

  // PORTIER: Explain Code
  context.subscriptions.push(
    vscode.commands.registerCommand("portier.explain", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showWarningMessage("No active editor");
        return;
      }

      const document = editor.document;
      const selection = editor.selection;
      const text = selection.isEmpty
        ? document.getText()
        : document.getText(selection);

      try {
        const response = await api.specialized({
          action: "explain",
          language: document.languageId,
          source: text,
          filename: document.fileName,
        });

        const explanation =
          response.explanation || response.result || "No explanation available";

        // Show in information message with option to open in new document
        const action = await vscode.window.showInformationMessage(
          explanation.substring(0, 200) + "...",
          "Show Full Explanation",
        );

        if (action === "Show Full Explanation") {
          const explanationDoc = await vscode.workspace.openTextDocument({
            content: `# PORTIER Code Explanation\\n\\n${explanation}`,
            language: "markdown",
          });
          await vscode.window.showTextDocument(explanationDoc);
        }
      } catch (error) {
        outputChannel.appendLine(`❌ Explanation failed: ${error.message}`);
        vscode.window.showErrorMessage(`Explanation failed: ${error.message}`);
      }
    }),
  );

  // PORTIER: Generate Tests
  context.subscriptions.push(
    vscode.commands.registerCommand("portier.tests", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showWarningMessage("No active editor");
        return;
      }

      const document = editor.document;
      const text = document.getText();

      try {
        vscode.window.withProgress(
          {
            location: vscode.ProgressLocation.Notification,
            title: "🧪 PORTIER generating tests...",
            cancellable: false,
          },
          async () => {
            const response = await api.specialized({
              action: "generate_tests",
              language: document.languageId,
              source: text,
              filename: document.fileName,
            });

            if (response.tests || response.test_code) {
              const testCode = response.tests || response.test_code;
              const testDoc = await vscode.workspace.openTextDocument({
                content: testCode,
                language: document.languageId,
              });
              await vscode.window.showTextDocument(testDoc);
              vscode.window.showInformationMessage("✅ Unit tests generated");
            } else {
              vscode.window.showWarningMessage("Could not generate tests");
            }
          },
        );
      } catch (error) {
        outputChannel.appendLine(`❌ Test generation failed: ${error.message}`);
        vscode.window.showErrorMessage(
          `Test generation failed: ${error.message}`,
        );
      }
    }),
  );

  // PORTIER: Format File
  context.subscriptions.push(
    vscode.commands.registerCommand("portier.format", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showWarningMessage("No active editor");
        return;
      }

      const document = editor.document;
      const text = document.getText();

      try {
        const response = await api.specialized({
          action: "format",
          language: document.languageId,
          source: text,
        });

        if (response.formatted_code || response.output) {
          const formattedCode = response.formatted_code || response.output;
          const fullRange = new vscode.Range(
            document.positionAt(0),
            document.positionAt(text.length),
          );

          await editor.edit((editBuilder) => {
            editBuilder.replace(fullRange, formattedCode);
          });

          vscode.window.showInformationMessage("✅ File formatted");
        }
      } catch (error) {
        outputChannel.appendLine(`❌ Formatting failed: ${error.message}`);
        vscode.window.showErrorMessage(`Formatting failed: ${error.message}`);
      }
    }),
  );

  // PORTIER: Fix Issues
  context.subscriptions.push(
    vscode.commands.registerCommand("portier.fix", async () => {
      const editor = vscode.window.activeTextEditor;
      if (!editor) {
        vscode.window.showWarningMessage("No active editor");
        return;
      }

      const document = editor.document;
      const selection = editor.selection;
      const text = selection.isEmpty
        ? document.getText()
        : document.getText(selection);

      try {
        const response = await api.specialized({
          action: "fix",
          language: document.languageId,
          source: text,
          filename: document.fileName,
        });

        if (response.fixed_code || response.output) {
          const fixedCode = response.fixed_code || response.output;
          await applyCodeChanges(editor, selection, fixedCode);
          vscode.window.showInformationMessage("✅ Issues fixed");
        } else {
          vscode.window.showInformationMessage("No issues found to fix");
        }
      } catch (error) {
        outputChannel.appendLine(`❌ Fix failed: ${error.message}`);
        vscode.window.showErrorMessage(`Fix failed: ${error.message}`);
      }
    }),
  );

  // PORTIER: Open Dashboard
  context.subscriptions.push(
    vscode.commands.registerCommand("portier.dashboard", async () => {
      const config = vscode.workspace.getConfiguration("portier");
      const dashboardUrl = config.get("dashboardUrl", "http://127.0.0.1:12349");

      try {
        await vscode.env.openExternal(vscode.Uri.parse(dashboardUrl));
        outputChannel.appendLine(`🌐 Dashboard opened: ${dashboardUrl}`);
      } catch (error) {
        vscode.window.showErrorMessage(
          `Failed to open dashboard: ${error.message}`,
        );
      }
    }),
  );

  // PORTIER: View Logs
  context.subscriptions.push(
    vscode.commands.registerCommand("portier.logs", () => {
      outputChannel.show();
    }),
  );

  // PORTIER: Reload Status
  context.subscriptions.push(
    vscode.commands.registerCommand("portier.reload", async () => {
      await updateAgentStatus();
      vscode.window.showInformationMessage("PORTIER status reloaded");
    }),
  );

  // PORTIER: Create File (AI)
  context.subscriptions.push(
    vscode.commands.registerCommand("portier.createFile", async () => {
      const description = await vscode.window.showInputBox({
        prompt: "Describe the file you want to create",
        placeHolder: "e.g., Python script to calculate fibonacci numbers",
      });

      if (description) {
        try {
          const response = await api.specialized({
            action: "create_file",
            description: description,
          });

          if (response.content || response.code) {
            const content = response.content || response.code;
            const language = response.language || "text";

            const doc = await vscode.workspace.openTextDocument({
              content: content,
              language: language,
            });
            await vscode.window.showTextDocument(doc);
            vscode.window.showInformationMessage("✅ File created");
          }
        } catch (error) {
          outputChannel.appendLine(`❌ File creation failed: ${error.message}`);
          vscode.window.showErrorMessage(
            `File creation failed: ${error.message}`,
          );
        }
      }
    }),
  );
}

/**
 * CodeLens Provider für Inline Actions
 */
function registerCodeLensProvider(context) {
  const codeLensProvider = {
    provideCodeLenses(document) {
      if (!isConnected) return [];

      const codeLenses = [];

      // Add CodeLens at the top of the file
      const topRange = new vscode.Range(0, 0, 0, 1);

      codeLenses.push(
        new vscode.CodeLens(topRange, {
          title: "💡 Explain",
          command: "portier.explain",
        }),
        new vscode.CodeLens(topRange, {
          title: "🛠️ Refactor",
          command: "portier.refactor",
        }),
        new vscode.CodeLens(topRange, {
          title: "✨ Fix",
          command: "portier.fix",
        }),
        new vscode.CodeLens(topRange, {
          title: "🧪 Tests",
          command: "portier.tests",
        }),
      );

      return codeLenses;
    },
  };

  // Register for all languages
  const selector = { scheme: "file" };
  context.subscriptions.push(
    vscode.languages.registerCodeLensProvider(selector, codeLensProvider),
  );
}

/**
 * Utility: Apply Code Changes
 */
async function applyCodeChanges(editor, selection, newCode) {
  const range = selection.isEmpty
    ? new vscode.Range(
        editor.document.positionAt(0),
        editor.document.positionAt(editor.document.getText().length),
      )
    : selection;

  return editor.edit((editBuilder) => {
    editBuilder.replace(range, newCode);
  });
}

/**
 * Extension Deactivation
 */
function deactivate() {
  outputChannel.appendLine("🛑 PORTIER Extension deactivated");
  if (statusBarItem) {
    statusBarItem.dispose();
  }
  if (outputChannel) {
    outputChannel.dispose();
  }
}

module.exports = {
  activate,
  deactivate,
};
