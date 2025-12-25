/**
 * Advanced Voice Recognition Engine
 * Handles speech-to-text with real-time processing
 */
export class VoiceRecognitionEngine {
  private recognition: any;
  private isActive: boolean = false;
  private currentTranscript: string = "";
  private silenceTimer: NodeJS.Timeout | null = null;
  private silenceThreshold: number = 2000;
  private onTranscriptCallback: (transcript: string, isFinal: boolean) => void;
  public onTranscript?: (transcript: string, isFinal: boolean) => void;
  public onError?: (error: string) => void;
  public onEnd?: () => void;
  public onStart?: () => void;

  constructor(language: string = "de-DE") {
    this.onTranscriptCallback = (transcript: string, isFinal: boolean) => {
      // Default callback
    };
    this.initializeRecognition(language);
  }

  private initializeRecognition(language: string) {
    try {
      // Web Speech API
      const SpeechRecognition =
        (window as any).SpeechRecognition ||
        (window as any).webkitSpeechRecognition;

      if (!SpeechRecognition) {
        throw new Error("Speech Recognition API not available");
      }

      this.recognition = new SpeechRecognition();
      this.setupRecognitionListeners(language);
    } catch (error) {
      console.error("Failed to initialize recognition:", error);
      throw error;
    }
  }

  private setupRecognitionListeners(language: string) {
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = language;

    this.recognition.onstart = () => {
      this.isActive = true;
      this.currentTranscript = "";
      if (this.onStart) {
        this.onStart();
      }
    };

    this.recognition.onresult = (event: any) => {
      this.handleRecognitionResult(event);
    };

    this.recognition.onerror = (event: any) => {
      console.error("Recognition error:", event.error);
      if (this.onError) {
        this.onError(event.error);
      }
    };

    this.recognition.onend = () => {
      this.isActive = false;
      if (this.currentTranscript.trim()) {
        this.onTranscriptCallback(this.currentTranscript, true);
      }
      if (this.onEnd) {
        this.onEnd();
      }
    };
  }

  private handleRecognitionResult(event: any) {
    let interimTranscript = "";

    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;

      if (event.results[i].isFinal) {
        this.currentTranscript += transcript + " ";
      } else {
        interimTranscript += transcript;
      }
    }

    // Reset silence timer
    if (this.silenceTimer) {
      clearTimeout(this.silenceTimer);
    }

    if (interimTranscript || this.currentTranscript) {
      const fullTranscript = this.currentTranscript + interimTranscript;
      this.onTranscriptCallback(fullTranscript, false);
      if (this.onTranscript) {
        this.onTranscript(fullTranscript, false);
      }

      // Auto-stop on silence
      this.silenceTimer = setTimeout(() => {
        this.stop();
      }, this.silenceThreshold);
    }
  }

  public start(): void {
    if (!this.isActive && this.recognition) {
      this.recognition.start();
    }
  }

  public stop(): void {
    if (this.isActive && this.recognition) {
      this.recognition.stop();
    }
    if (this.silenceTimer) {
      clearTimeout(this.silenceTimer);
    }
  }

  public abort(): void {
    if (this.recognition) {
      this.recognition.abort();
    }
    this.isActive = false;
  }

  public setLanguage(language: string): void {
    this.abort();
    this.initializeRecognition(language);
  }

  public setSilenceThreshold(threshold: number): void {
    this.silenceThreshold = threshold;
  }

  public isRecognizing(): boolean {
    return this.isActive;
  }

  public getTranscript(): string {
    return this.currentTranscript;
  }

  public clearTranscript(): void {
    this.currentTranscript = "";
  }
}
