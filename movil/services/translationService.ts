export type Language = 'es' | 'en';

export interface TranslationResult {
  text: string;
  explanation?: string;
  sourceLang: string;
  targetLang: Language;
}

export const translationService = {
  /**
   * Translates text from Chinese to Spanish or English
   * In a production app, this would call a backend or an LLM API directly
   */
  translate: async (
    text: string, 
    targetLang: Language = 'es'
  ): Promise<TranslationResult> => {
    try {
      if (!text.trim()) {
        return { text: '', sourceLang: 'zh', targetLang };
      }

      // Simulated API call - In a real scenario, use Gemini, OpenAI or a Translator API
      // Using MyMemory API (Free, no key required for small volumes)
      const langPair = `zh|${targetLang}`;
      const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${langPair}`;
      
      const response = await fetch(url);
      const data = await response.json();

      if (data.responseStatus === 200) {
        return {
          text: data.responseData.translatedText,
          sourceLang: 'zh',
          targetLang,
          explanation: "Traducción realizada con motor estadístico. Para mayor precisión se recomienda revisión por IA."
        };
      } else {
        throw new Error('Error en el servicio de traducción');
      }
    } catch (error) {
      console.error('Translation Error:', error);
      return {
        text: 'Error en la traducción. Inténtalo de nuevo.',
        sourceLang: 'zh',
        targetLang,
      };
    }
  },

  /**
   * Advanced translation using an LLM (Ready for expansion)
   */
  translateWithAI: async (text: string, targetLang: Language): Promise<TranslationResult> => {
    // This is where you would integrate Gemini 1.5 Flash
    // For now, it calls the same service, but can be expanded
    return translationService.translate(text, targetLang);
  }
};
