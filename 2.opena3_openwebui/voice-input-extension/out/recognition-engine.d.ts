/**
 * Advanced Voice Recognition Engine
 * Handles speech-to-text with real-time processing
 */
export declare class VoiceRecognitionEngine {
    private recognition;
    private isActive;
    private currentTranscript;
    private silenceTimer;
    private silenceThreshold;
    private onTranscriptCallback;
    onTranscript?: (transcript: string, isFinal: boolean) => void;
    onError?: (error: string) => void;
    onEnd?: () => void;
    onStart?: () => void;
    constructor(language?: string);
    private initializeRecognition;
    private setupRecognitionListeners;
    private handleRecognitionResult;
    start(): void;
    stop(): void;
    abort(): void;
    setLanguage(language: string): void;
    setSilenceThreshold(threshold: number): void;
    isRecognizing(): boolean;
    getTranscript(): string;
    clearTranscript(): void;
}
//# sourceMappingURL=recognition-engine.d.ts.map