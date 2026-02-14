import { useState, useCallback } from 'react';
import { translationService, Language } from '../services/translationService';
import { pinyinService, PinyinGroup } from '../services/pinyinService';

export const useTranslator = () => {
  const [inputText, setInputText] = useState('');
  const [translatedText, setTranslatedText] = useState('');
  const [pinyinGroups, setPinyinGroups] = useState<PinyinGroup[]>([]);
  const [targetLang, setTargetLang] = useState<Language>('es');
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const handleTranslate = useCallback(async (textOverride?: string) => {
    const textToTranslate = textOverride ?? inputText;
    
    if (!textToTranslate.trim()) return;

    setIsLoading(true);
    setProgress(5);
    setError(null);

    try {
      // 1. Generate Pinyin and Groups
      const tokens = pinyinService.generatePinyinTokens(textToTranslate);
      const groups = pinyinService.groupTokens(tokens);
      setProgress(15);
      
      // 2. Main Translation
      const mainResult = await translationService.translate(textToTranslate, targetLang);
      setTranslatedText(mainResult.text);
      setProgress(30);

      // 3. Batch translate groups to English (for the interlinear gloss)
      const totalGroups = groups.length;
      const groupResults: PinyinGroup[] = [];

      for (let i = 0; i < totalGroups; i++) {
        const group = groups[i];
        const groupText = group.tokens.map(t => t.char).join('');
        
        // Only translate if it contains actual content (avoiding purely punctuation/space groups)
        const purePunctuation = /^[。！？；，、：“”‘’（）【】—…!?;,.:"'[\]\s-]+$/.test(groupText);
        
        if (purePunctuation) {
          groupResults.push(group);
        } else {
          const glossResult = await translationService.translate(groupText, targetLang);
          groupResults.push({
            ...group,
            translation: glossResult.text
          });
        }

        // Increment progress: from 30% to 100%
        const currentProgress = 30 + Math.floor(((i + 1) / totalGroups) * 70);
        setProgress(currentProgress);
      }

      setPinyinGroups(groupResults);
      setProgress(100);

    } catch (err) {
      setError('No se pudo completar la traducción.');
      console.error(err);
    } finally {
      setIsLoading(false);
      // Keep 100% for a moment then hide
      setTimeout(() => setProgress(0), 1000);
    }
  }, [inputText, targetLang]);

  const clear = () => {
    setInputText('');
    setTranslatedText('');
    setPinyinGroups([]);
    setError(null);
  };

  return {
    inputText,
    setInputText,
    translatedText,
    pinyinGroups,
    targetLang,
    setTargetLang,
    isLoading,
    progress,
    error,
    handleTranslate,
    clear
  };
};
