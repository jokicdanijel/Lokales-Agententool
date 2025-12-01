#!/usr/bin/env python3
"""
🤖 AI Reply Engine - PORTIER PAS-6.0
OpenAI-powered intelligent email response generation
"""

import json
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Any, Callable, Coroutine

try:
    import openai
    openai_available: bool = True
except ImportError:
    openai_available = False

if TYPE_CHECKING:
    from openai import OpenAI

logger = logging.getLogger(__name__)

class AIReplyEngine:
    """AI-powered email reply generation and classification"""
    
    def __init__(self, openai_api_key: str = "", model: str = "gpt-4o-mini"):
        self.openai_api_key = openai_api_key
        self.model = model
        self.client = None
        self.available = False
        
        if openai_available and openai_api_key:
            try:
                self.client = openai.OpenAI(api_key=openai_api_key)
                self.available = True
                logger.info("🤖 AI Reply Engine initialized with OpenAI")
            except Exception as e:
                logger.error(f"❌ OpenAI initialization failed: {e}")
        else:
            logger.warning("⚠️ AI Reply Engine running in mock mode (no OpenAI key)")
    
    async def handle_specialized(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle specialized AI actions"""
        try:
            action = payload.get("action", "")
            
            logger.info(f"🤖 Processing AI action: {action}")
            
            action_handlers = {
                "generate_reply": self._generate_reply,
                "classify_email": self._classify_email,
                "extract_info": self._extract_info,
                "sentiment_analysis": self._sentiment_analysis,
                "priority_score": self._priority_score,
                "auto_response": self._auto_response,
            }
            handler = action_handlers.get(action)
            if handler:
                return await handler(payload)
            else:
                return {
                    "error": "unknown_ai_action",
                    "message": f"Action '{action}' not recognized",
                    "available_actions": list(action_handlers.keys())
                }
                
        except Exception as e:
            logger.error(f"❌ AI action failed: {e}")
            return {
                "error": "ai_processing_failed",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _generate_reply(self, payload: Dict) -> Dict[str, Any]:
        """Generate AI reply to email"""
        try:
            email_text = payload.get("email_text", "")
            context = payload.get("context", "")
            tone = payload.get("tone", "professional")
            language = payload.get("language", "german")
            
            if not email_text:
                return {"error": "missing_email_text", "message": "Email text is required"}
            
            if self.available and self.client:
                # Real OpenAI API call
                response = await self._call_openai(
                    prompt=self._build_reply_prompt(email_text, context, tone, language),
                    max_tokens=500
                )
                
                return {
                    "status": "success",
                    "reply": response.get("content", ""),
                    "model": self.model,
                    "tone": tone,
                    "language": language,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Mock response
                return {
                    "status": "success",
                    "reply": f"Vielen Dank für Ihre E-Mail. Wir haben Ihre Nachricht erhalten und werden uns umgehend bei Ihnen melden. (Mock-Antwort auf: {email_text[:50]}...)",
                    "model": "mock",
                    "tone": tone,
                    "language": language,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {"error": "reply_generation_failed", "message": str(e)}
    
    async def _classify_email(self, payload: Dict) -> Dict[str, Any]:
        """Classify email type and category"""
        try:
            email_text = payload.get("email_text", "")
            subject = payload.get("subject", "")
            
            if not email_text and not subject:
                return {"error": "missing_content", "message": "Email text or subject required"}
            
            if self.available and self.client:
                # Real classification
                response = await self._call_openai(
                    prompt=self._build_classification_prompt(email_text, subject),
                    max_tokens=200
                )
                
                try:
                    classification = json.loads(response.get("content", "{}"))
                except json.JSONDecodeError:
                    classification = {"category": "unknown", "confidence": 0.0}
            else:
                # Mock classification
                classification = {
                    "category": "inquiry",
                    "subcategory": "general_question",
                    "confidence": 0.85,
                    "urgency": "medium",
                    "requires_human": False
                }
            
            return {
                "status": "success",
                "classification": classification,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": "classification_failed", "message": str(e)}
    
    async def _extract_info(self, payload: Dict) -> Dict[str, Any]:
        """Extract structured information from email"""
        try:
            email_text = payload.get("email_text", "")
            fields = payload.get("fields", ["contact", "intent", "deadline"])
            
            if not email_text:
                return {"error": "missing_email_text"}
            
            if self.available and self.client:
                # Real extraction
                response = await self._call_openai(
                    prompt=self._build_extraction_prompt(email_text, fields),
                    max_tokens=300
                )
                
                try:
                    extracted = json.loads(response.get("content", "{}"))
                except json.JSONDecodeError:
                    extracted = {field: None for field in fields}
            else:
                # Mock extraction
                extracted = {
                    "contact": "Max Mustermann",
                    "intent": "Information request",
                    "deadline": None,
                    "phone": None,
                    "company": "Example GmbH"
                }
            
            return {
                "status": "success",
                "extracted": extracted,
                "fields": fields,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": "extraction_failed", "message": str(e)}
    
    async def _sentiment_analysis(self, payload: Dict) -> Dict[str, Any]:
        """Analyze email sentiment"""
        try:
            email_text = payload.get("email_text", "") # type: ignore
            
            if not email_text:
                return {"error": "missing_email_text"}
            
            if self.available and self.client:
                # Real sentiment analysis
                response = await self._call_openai(
                    prompt=self._build_sentiment_prompt(email_text),
                    max_tokens=150
                )
                
                try:
                    sentiment = json.loads(response.get("content", "{}"))
                except json.JSONDecodeError:
                    sentiment = {"sentiment": "neutral", "confidence": 0.0}
            else:
                # Mock sentiment
                sentiment = {
                    "sentiment": "neutral",
                    "confidence": 0.75,
                    "emotions": ["curiosity", "professionalism"],
                    "politeness": 0.8
                }
            
            return {
                "status": "success",
                "sentiment": sentiment,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": "sentiment_analysis_failed", "message": str(e)}
    
    async def _priority_score(self, payload: Dict) -> Dict[str, Any]:
        """Calculate email priority score"""
        try:
            email_text = payload.get("email_text", "")
            subject = payload.get("subject", "")
            sender = payload.get("sender", "")
            
            if self.available and self.client:
                # Real priority scoring
                response = await self._call_openai(
                    prompt=self._build_priority_prompt(email_text, subject, sender),
                    max_tokens=100
                )
                
                try:
                    priority = json.loads(response.get("content", "{}"))
                except json.JSONDecodeError:
                    priority = {"score": 5, "reasoning": "Unable to parse"}
            else:
                # Mock priority
                priority = {
                    "score": 6,  # 1-10 scale
                    "level": "medium",
                    "reasoning": "Standard business inquiry, no urgency indicators",
                    "factors": ["professional_tone", "no_deadline", "general_inquiry"]
                }
            
            return {
                "status": "success",
                "priority": priority,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": "priority_scoring_failed", "message": str(e)}
    
    async def _auto_response(self, payload: Dict) -> Dict[str, Any]:
        """Generate automatic response with classification"""
        try:
            email_text = payload.get("email_text", "")
            
            if not email_text:
                return {"error": "missing_email_text"}
            
            # Combine classification and reply generation
            classification_result = await self._classify_email({"email_text": email_text})
            
            if classification_result.get("status") == "success":
                classification = classification_result.get("classification", {})
                
                # Generate contextual reply based on classification
                reply_result = await self._generate_reply({
                    "email_text": email_text,
                    "context": f"This is classified as: {classification.get('category', 'unknown')}",
                    "tone": "friendly_professional"
                })
                
                return {
                    "status": "success",
                    "classification": classification,
                    "reply": reply_result.get("reply", ""),
                    "should_send": not classification.get("requires_human", True),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": "classification_failed", "message": "Could not classify email for auto-response"}
                
        except Exception as e:
            return {"error": "auto_response_failed", "message": str(e)}
    
    async def _call_openai(self, prompt: str, max_tokens: int = 500) -> Dict[str, str]:
        """Make async OpenAI API call"""
        try:
            if not self.client:
                return {"content": "OpenAI client not available"}
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an intelligent email assistant. Provide accurate, helpful responses in the requested format."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            return {"content": response.choices[0].message.content}
            
        except Exception as e:
            logger.error(f"❌ OpenAI API call failed: {e}")
            return {"content": f"API Error: {str(e)}"}
    
    def _build_reply_prompt(self, email_text: str, context: str, tone: str, language: str) -> str:
        """Build prompt for reply generation"""
        return f"""
        Generate a professional email reply in {language}.
        
        Original email: {email_text}
        Context: {context}
        Tone: {tone}
        
        Requirements:
        - Be helpful and professional
        - Address the main points
        - Keep it concise
        - Use appropriate greeting and closing
        
        Reply:
        """
    
    def _build_classification_prompt(self, email_text: str, subject: str) -> str:
        """Build prompt for email classification"""
        return f"""
        Classify this email and return JSON format:
        
        Subject: {subject}
        Content: {email_text}
        
        Return JSON with these fields:
        - category: (inquiry, complaint, order, support, etc.)
        - subcategory: specific type
        - confidence: 0.0-1.0
        - urgency: low/medium/high
        - requires_human: boolean
        
        JSON:
        """
    
    def _build_extraction_prompt(self, email_text: str, fields: List[str]) -> str:
        """Build prompt for information extraction"""
        return f"""
        Extract structured information from this email:
        
        Email: {email_text}
        
        Extract these fields: {', '.join(fields)}
        
        Return JSON format with field names as keys.
        Use null for missing information.
        
        JSON:
        """
    
    def _build_sentiment_prompt(self, email_text: str) -> str:
        """Build prompt for sentiment analysis"""
        return f"""
        Analyze the sentiment of this email:
        
        Email: {email_text}
        
        Return JSON with:
        - sentiment: positive/negative/neutral
        - confidence: 0.0-1.0
        - emotions: array of detected emotions
        - politeness: 0.0-1.0
        
        JSON:
        """
    
    def _build_priority_prompt(self, email_text: str, subject: str, sender: str) -> str:
        """Build prompt for priority scoring"""
        return f"""
        Score the priority of this email (1-10 scale):
        
        From: {sender}
        Subject: {subject}
        Content: {email_text}
        
        Return JSON with:
        - score: 1-10 (1=lowest, 10=highest priority)
        - level: low/medium/high
        - reasoning: brief explanation
        - factors: array of priority factors
        
        JSON:
        """
    
    def get_status(self) -> Dict[str, Any]:
        """Get AI engine status"""
        return {
            "available": self.available,
            "model": self.model,
            "openai_configured": bool(self.openai_api_key),
            "version": "6.0.0",
            "timestamp": datetime.now().isoformat()
        }