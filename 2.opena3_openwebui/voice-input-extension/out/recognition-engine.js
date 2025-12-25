"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.VoiceRecognitionEngine = void 0;
/**
 * Advanced Voice Recognition Engine
 * Handles speech-to-text with real-time processing
 */
class VoiceRecognitionEngine {
  constructor(language = "de-DE") {
    this.isActive = false;
    this.currentTranscript = "";
    this.silenceTimer = null;
    this.silenceThreshold = 2000;
    this.onTranscriptCallback = (transcript, isFinal) => {
      // Default callback
    };
    this.initializeRecognition(language);
  }
  initializeRecognition(language) {
    try {
      // Web Speech API
      const SpeechRecognition =
        window.SpeechRecognition || window.webkitSpeechRecognition;
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
  setupRecognitionListeners(language) {
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
    this.recognition.onresult = (event) => {
      this.handleRecognitionResult(event);
    };
    this.recognition.onerror = (event) => {
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
  handleRecognitionResult(event) {
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
  start() {
    if (!this.isActive && this.recognition) {
      this.recognition.start();
    }
  }
  stop() {
    if (this.isActive && this.recognition) {
      this.recognition.stop();
    }
    if (this.silenceTimer) {
      clearTimeout(this.silenceTimer);
    }
  }
  abort() {
    if (this.recognition) {
      this.recognition.abort();
    }
    this.isActive = false;
  }
  setLanguage(language) {
    this.abort();
    this.initializeRecognition(language);
  }
  setSilenceThreshold(threshold) {
    this.silenceThreshold = threshold;
  }
  isRecognizing() {
    return this.isActive;
  }
  getTranscript() {
    return this.currentTranscript;
  }
  clearTranscript() {
    this.currentTranscript = "";
  }
}
exports.VoiceRecognitionEngine = VoiceRecognitionEngine;
//# sourceMappingURL=recognition-engine.js.map
