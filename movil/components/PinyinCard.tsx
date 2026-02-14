import React from 'react';
import { Text, StyleSheet, TouchableOpacity } from 'react-native';
import { COLORS, SPACING, BORDER_RADIUS } from '../constants/Theme';
import { PinyinToken } from '../services/pinyinService';

interface PinyinCardProps {
  token: PinyinToken;
  textColor?: string;
  fontSizeMultiplier?: number;
  onPress?: () => void;
}

export const PinyinCard: React.FC<PinyinCardProps> = ({ token, textColor, fontSizeMultiplier = 1, onPress }) => {
  const isChineseChar = /[\u4e00-\u9fff]/.test(token.char);

  return (
    <TouchableOpacity 
      activeOpacity={0.7}
      disabled={!isChineseChar || !onPress}
      onPress={onPress}
      style={[
        styles.container, 
        !isChineseChar && styles.punctuationContainer,
        { 
            minWidth: 40 * fontSizeMultiplier,
            padding: SPACING.xs * fontSizeMultiplier
        }
      ]}
    >
      {isChineseChar && (
        <Text style={[styles.pinyin, { fontSize: 10 * fontSizeMultiplier }]} numberOfLines={1}>
          {token.pinyin}
        </Text>
      )}
      <Text style={[
        styles.char, 
        { 
            color: textColor || COLORS.black, 
            fontSize: 18 * fontSizeMultiplier 
        }, 
        !isChineseChar && styles.punctuationText
      ]}>
        {token.char}
      </Text>
    </TouchableOpacity>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: BORDER_RADIUS.md,
    margin: 2,
    borderWidth: 1,
    borderColor: 'rgba(128,128,128,0.2)',
    backgroundColor: 'rgba(128,128,128,0.05)',
  },
  punctuationContainer: {
    backgroundColor: 'transparent',
    borderWidth: 0,
    elevation: 0,
    minWidth: 10,
    padding: 2,
    margin: 1,
  },
  pinyin: {
    color: COLORS.primary,
    fontWeight: '600',
    marginBottom: 1,
  },
  char: {
    fontWeight: 'bold',
  },
  punctuationText: {
    fontSize: 16,
    color: '#64748b',
  },
});
