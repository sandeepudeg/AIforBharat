#!/usr/bin/env python3
"""
Language Agent using Strands Framework

This agent handles language translation, common phrases, and language guides for travel.
"""

import logging
from strands import Agent
from strands.models import BedrockModel
from strands.session.s3_session_manager import S3SessionManager

logger = logging.getLogger(__name__)


class LanguageAgent(Agent):
    """Language specialist agent using Strands framework."""
    
    def __init__(self, session_manager: S3SessionManager = None):
        """Initialize Language Agent with Bedrock model and tools."""
        
        model = BedrockModel(
            model_id="us.amazon.nova-pro-v1:0",
            temperature=0.3
        )
        
        system_prompt = """You are a travel language expert. Your responsibilities:
1. Translate text between languages
2. Provide common travel phrases
3. Create language guides for destinations
4. Offer pronunciation guidance
5. Provide cultural communication tips

When users ask about languages, use the available tools to translate,
provide phrases, and help with communication."""
        
        super().__init__(
            model=model,
            system_prompt=system_prompt,
            session_manager=session_manager,
            tools=[
                self.translate_text,
                self.get_common_phrases,
                self.get_language_guide,
                self.get_pronunciation
            ]
        )
    
    def translate_text(self, text: str, source_language: str, 
                      target_language: str) -> dict:
        """
        Translate text between languages.
        
        Args:
            text: Text to translate
            source_language: Source language (e.g., "English")
            target_language: Target language (e.g., "French")
            
        Returns:
            Translated text
        """
        logger.info(f"Translating from {source_language} to {target_language}")
        
        # Mock translations
        translations = {
            ("English", "French"): {
                "hello": "Bonjour",
                "thank you": "Merci",
                "goodbye": "Au revoir",
                "please": "S'il vous plaît",
                "excuse me": "Excusez-moi"
            },
            ("English", "Japanese"): {
                "hello": "こんにちは (Konnichiwa)",
                "thank you": "ありがとう (Arigatou)",
                "goodbye": "さようなら (Sayounara)",
                "please": "お願いします (Onegaishimasu)",
                "excuse me": "すみません (Sumimasen)"
            },
            ("English", "Italian"): {
                "hello": "Ciao",
                "thank you": "Grazie",
                "goodbye": "Arrivederci",
                "please": "Per favore",
                "excuse me": "Scusa"
            }
        }
        
        key = (source_language, target_language)
        translation_dict = translations.get(key, {})
        translated = translation_dict.get(text.lower(), f"[Translation of '{text}' not available]")
        
        return {
            "original_text": text,
            "source_language": source_language,
            "translated_text": translated,
            "target_language": target_language
        }
    
    def get_common_phrases(self, destination: str, language: str) -> list:
        """
        Get common travel phrases for a destination.
        
        Args:
            destination: City name
            language: Language code
            
        Returns:
            List of common phrases
        """
        logger.info(f"Getting common phrases for {destination} in {language}")
        
        phrases = {
            "French": [
                {"english": "Hello", "local": "Bonjour", "pronunciation": "bon-ZHOOR"},
                {"english": "Thank you", "local": "Merci", "pronunciation": "mer-SEE"},
                {"english": "Where is the bathroom?", "local": "Où sont les toilettes?", "pronunciation": "oo sohn lay twah-LET"},
                {"english": "How much?", "local": "Combien?", "pronunciation": "kom-bee-YAN"},
                {"english": "I don't understand", "local": "Je ne comprends pas", "pronunciation": "zhuh nuh kom-PRAHN pah"}
            ],
            "Japanese": [
                {"english": "Hello", "local": "こんにちは", "pronunciation": "Konnichiwa"},
                {"english": "Thank you", "local": "ありがとう", "pronunciation": "Arigatou"},
                {"english": "Where is the bathroom?", "local": "トイレはどこですか?", "pronunciation": "Toire wa doko desu ka?"},
                {"english": "How much?", "local": "いくらですか?", "pronunciation": "Ikura desu ka?"},
                {"english": "I don't understand", "local": "わかりません", "pronunciation": "Wakarimasen"}
            ],
            "Italian": [
                {"english": "Hello", "local": "Ciao", "pronunciation": "CHOW"},
                {"english": "Thank you", "local": "Grazie", "pronunciation": "GRAHT-see-eh"},
                {"english": "Where is the bathroom?", "local": "Dov'è il bagno?", "pronunciation": "doh-VEH eel BAH-nyoh"},
                {"english": "How much?", "local": "Quanto costa?", "pronunciation": "KWAN-toh KOS-tah"},
                {"english": "I don't understand", "local": "Non capisco", "pronunciation": "nohn kah-PEES-koh"}
            ]
        }
        
        return phrases.get(language, [])
    
    def get_language_guide(self, destination: str) -> dict:
        """
        Get a language guide for a destination.
        
        Args:
            destination: City name
            
        Returns:
            Language guide information
        """
        logger.info(f"Getting language guide for {destination}")
        
        guides = {
            "Paris": {
                "primary_language": "French",
                "english_spoken": "Moderate (in tourist areas)",
                "useful_phrases": 5,
                "tips": [
                    "Learn basic French phrases - locals appreciate the effort",
                    "English is spoken in hotels and tourist areas",
                    "Carry a translation app",
                    "Use hand gestures when needed",
                    "Be polite and say 'Bonjour' when entering shops"
                ]
            },
            "Tokyo": {
                "primary_language": "Japanese",
                "english_spoken": "Limited (in tourist areas)",
                "useful_phrases": 5,
                "tips": [
                    "Learn basic Japanese phrases",
                    "Download a translation app",
                    "Use Google Translate camera feature",
                    "Carry a phrasebook",
                    "Many signs have English in tourist areas"
                ]
            },
            "Rome": {
                "primary_language": "Italian",
                "english_spoken": "Moderate (in tourist areas)",
                "useful_phrases": 5,
                "tips": [
                    "Learn basic Italian phrases",
                    "English is common in hotels and restaurants",
                    "Use hand gestures - Italians are expressive",
                    "Carry a translation app",
                    "Be respectful in religious sites"
                ]
            }
        }
        
        return guides.get(destination, {
            "primary_language": "Unknown",
            "english_spoken": "Variable",
            "useful_phrases": 0,
            "tips": ["Download a translation app", "Carry a phrasebook"]
        })
    
    def get_pronunciation(self, phrase: str, language: str) -> dict:
        """
        Get pronunciation guide for a phrase.
        
        Args:
            phrase: Phrase to pronounce
            language: Language
            
        Returns:
            Pronunciation information
        """
        logger.info(f"Getting pronunciation for '{phrase}' in {language}")
        
        pronunciations = {
            "French": {
                "bonjour": "bon-ZHOOR",
                "merci": "mer-SEE",
                "s'il vous plaît": "see voo PLEH"
            },
            "Japanese": {
                "konnichiwa": "kon-nee-chee-WAH",
                "arigatou": "ah-ree-gah-TOH",
                "sumimasen": "soo-mee-mah-SEN"
            },
            "Italian": {
                "ciao": "CHOW",
                "grazie": "GRAHT-see-eh",
                "per favore": "pair fah-VOR-eh"
            }
        }
        
        lang_dict = pronunciations.get(language, {})
        pronunciation = lang_dict.get(phrase.lower(), "Pronunciation not available")
        
        return {
            "phrase": phrase,
            "language": language,
            "pronunciation": pronunciation,
            "tips": "Break the phrase into syllables and practice slowly"
        }
