import { pinyin } from 'pinyin-pro';

export interface PinyinToken {
  char: string;
  pinyin: string;
  translation?: string; // Optional per-token or per-group translation
}

export interface PinyinGroup {
  tokens: PinyinToken[];
  translation?: string;
}

export const pinyinService = {
  /**
   * Generates pinyin for a given Chinese text
   */
  generatePinyinTokens: (text: string): PinyinToken[] => {
    if (!text) return [];
    
    // Get pinyin as an array of strings
    const pinyinList = pinyin(text, { type: 'array', toneType: 'symbol' });
    
    // Split text into characters to match with pinyin
    const chars = Array.from(text);
    
    return chars.map((char, index) => ({
      char,
      pinyin: pinyinList[index] || '',
    }));
  },

  /**
   * Group tokens based on punctuation or length for better display
   */
  groupTokens: (tokens: PinyinToken[], maxGroupSize: number = 8): PinyinGroup[] => {
    const groups: PinyinGroup[] = [];
    let currentTokens: PinyinToken[] = [];
    
    const punctuation = new Set([
      '。', '！', '？', '；', '，', '、', '：', '“', '”', '‘', '’', '（', '）', '【', '】', '—', '…',
      '.', '!', '?', ';', ',', ':', '"', "'", '(', ')', '[', ']', '-', '…', ' '
    ]);

    tokens.forEach((token, index) => {
      // Clean up whitespace-only tokens if they are not intentional
      if (token.char.trim() === '' && token.char !== ' ') return;

      currentTokens.push(token);
      
      const isPunc = punctuation.has(token.char);
      const nextToken = tokens[index + 1];
      const isNextPunc = nextToken ? punctuation.has(nextToken.char) : false;

      // Logic to close group:
      // 1. If we reach max size and NEXT isn't punctuation (to keep punc with word)
      // 2. OR if current is punc AND we have reached a decent size (at least 3-4 chars)
      // 3. OR if current is punctuation like period/exclamation (end of sentence)
      const endOfSentence = ['。', '！', '？', '.', '!', '?'].includes(token.char);
      const isLargeEnough = currentTokens.length >= 4;
      
      const shouldClose = (currentTokens.length >= maxGroupSize && !isNextPunc) || 
                          (endOfSentence) ||
                          (isPunc && isLargeEnough && !['“', '‘', '（', '【'].includes(token.char));

      if (shouldClose && currentTokens.length > 0) {
        // Merge into groups if they have content
        groups.push({ tokens: [...currentTokens] });
        currentTokens = [];
      }
    });

    if (currentTokens.length > 0) {
      // If the last group is very small (like just punctuation) and we have previous groups,
      // try to merge it into the last one to avoid a "jump" or empty line
      const lastGroupTokens = currentTokens;
      const hasChinese = lastGroupTokens.some(t => /[\u4e00-\u9fff]/.test(t.char));
      
      if (!hasChinese && groups.length > 0) {
        groups[groups.length - 1].tokens.push(...lastGroupTokens);
      } else {
        groups.push({ tokens: lastGroupTokens });
      }
    }

    return groups;
  }
};
