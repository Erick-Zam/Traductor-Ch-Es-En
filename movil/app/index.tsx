import React, { useState, useRef, useCallback, useLayoutEffect } from 'react';
import { 
  View, 
  Text, 
  StyleSheet, 
  TextInput, 
  TouchableOpacity, 
  ScrollView, 
  ActivityIndicator, 
  KeyboardAvoidingView, 
  Platform, 
  StatusBar, 
  PanResponder, 
  Dimensions,
  Modal,
  Pressable,
  Animated
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from 'expo-router';
import { LinearGradient } from 'expo-linear-gradient';
import { 
  Languages, 
  Trash2, 
  Send, 
  Sun, 
  Moon, 
  ChevronUp, 
  ChevronDown, 
  ArrowUp, 
  GripHorizontal,
  X,
  BookOpen,
  Settings,
  Type,
  Info
} from 'lucide-react-native';
import { 
  COLORS, 
  SPACING, 
  BORDER_RADIUS, 
  LIGHT_THEME, 
  DARK_THEME 
} from '../constants/Theme';
import { useTranslator } from '../hooks/useTranslator';
import { PinyinCard } from '../components/PinyinCard';

const { height: SCREEN_HEIGHT } = Dimensions.get('window');
const MIN_HEIGHT = 120;
const MAX_HEIGHT = SCREEN_HEIGHT * 0.7;

// Shared Header Action Icon Component
const ActionIcon = ({ onPress, icon: Icon, color, size = 20 }: any) => (
  <TouchableOpacity 
    onPress={onPress} 
    style={[styles.headerIconBtn]}
  >
    <Icon size={size} color={color} />
  </TouchableOpacity>
);

export default function Index() {
  const [isDark, setIsDark] = useState(false);
  const [isInputCollapsed, setIsInputCollapsed] = useState(false);
  const [showScrollTop, setShowScrollTop] = useState(false);
  
  // Optimization: Use Animated for topHeight
  const topHeightAnim = useRef(new Animated.Value(250)).current;
  const currentTopHeight = useRef(250);
  
  // Font Size State
  const [fontSize, setFontSize] = useState(17);
  const [isSettingsVisible, setIsSettingsVisible] = useState(false);
  const [isInfoVisible, setIsInfoVisible] = useState(false);
  
  // Dictionary State
  const [selectedWord, setSelectedWord] = useState<any>(null);
  
  const theme = isDark ? DARK_THEME : LIGHT_THEME;
  const scrollRef = useRef<ScrollView>(null);
  const inputScrollRef = useRef<ScrollView>(null);
  const lastScrollY = useRef(0);
  
  // Scroll Sync Refs
  const isSyncing = useRef(false);

  const {
    inputText,
    setInputText,
    pinyinGroups,
    targetLang,
    setTargetLang,
    isLoading,
    progress,
    handleTranslate,
    clear
  } = useTranslator();

  // Optimized PanResponder for resizing
  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onPanResponderMove: (_, gestureState) => {
        let newHeight = currentTopHeight.current + gestureState.dy;
        if (newHeight < MIN_HEIGHT) newHeight = MIN_HEIGHT;
        if (newHeight > MAX_HEIGHT) newHeight = MAX_HEIGHT;
        topHeightAnim.setValue(newHeight);
      },
      onPanResponderRelease: (_, gestureState) => {
        let finalHeight = currentTopHeight.current + gestureState.dy;
        if (finalHeight < MIN_HEIGHT) finalHeight = MIN_HEIGHT;
        if (finalHeight > MAX_HEIGHT) finalHeight = MAX_HEIGHT;
        currentTopHeight.current = finalHeight;
      }
    })
  ).current;

  const toggleTheme = useCallback(() => setIsDark(prev => !prev), []);

  const navigation = useNavigation();
  
  const headerRightComponent = useCallback(() => (
    <View style={styles.headerRightContainer}>
      <ActionIcon 
        icon={Info} 
        onPress={() => setIsInfoVisible(true)} 
        color={theme.text} 
        size={18}
      />
      <ActionIcon 
        icon={Settings} 
        onPress={() => setIsSettingsVisible(true)} 
        color={theme.text} 
      />
      <ActionIcon 
        icon={isDark ? Sun : Moon} 
        onPress={toggleTheme} 
        color={theme.text} 
      />
    </View>
  ), [theme.text, isDark, toggleTheme]);

  useLayoutEffect(() => {
    navigation.setOptions({
      headerTitle: "Traductor Chino",
      headerStyle: { backgroundColor: theme.card },
      headerTitleStyle: { color: theme.text, fontWeight: '800' },
      headerRight: headerRightComponent,
    });
  }, [navigation, theme, headerRightComponent]);



  const handleOutputScroll = (event: any) => {
    const currentOffset = event.nativeEvent.contentOffset.y;
    const isScrollingUp = currentOffset < lastScrollY.current;
    setShowScrollTop(currentOffset > 200 && isScrollingUp);
    lastScrollY.current = currentOffset;
    
    // Sync Output -> Input
    if (!isSyncing.current && inputScrollRef.current) {
        isSyncing.current = true;
        inputScrollRef.current.scrollTo({ y: currentOffset, animated: false });
        setTimeout(() => { isSyncing.current = false; }, 10);
    }
  };

  const handleInputScroll = (event: any) => {
     // Sync Input -> Output
     if (!isSyncing.current && scrollRef.current) {
        isSyncing.current = true;
        scrollRef.current.scrollTo({ y: event.nativeEvent.contentOffset.y, animated: false });
        setTimeout(() => { isSyncing.current = false; }, 10);
    }
  };

  const scrollToTop = () => {
    scrollRef.current?.scrollTo({ y: 0, animated: true });
    inputScrollRef.current?.scrollTo({ y: 0, animated: true });
  };

  const hasResults = pinyinGroups.length > 0;

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]} edges={['bottom', 'left', 'right']}>
      <StatusBar barStyle={isDark ? "light-content" : "dark-content"} />
      
      <KeyboardAvoidingView 
        behavior={Platform.OS === 'ios' ? 'padding' : undefined}
        style={{ flex: 1 }}
      >
        {progress > 0 && (
          <View style={[styles.progressContainer, { backgroundColor: theme.background }]}>
            <View style={[styles.progressBar, { width: `${progress}%` }]} />
          </View>
        )}

        <View style={styles.splitWrapper}>
          {/* Top Card (Input) */}
          <Animated.View style={[styles.card, styles.topCard, { 
            backgroundColor: theme.card, 
            borderColor: theme.border, 
            height: isInputCollapsed ? 70 : topHeightAnim,
          }]}>
            <View style={styles.cardHeader}>
              <TouchableOpacity 
                style={styles.collapseTrigger} 
                onPress={() => setIsInputCollapsed(!isInputCollapsed)}
              >
                <Text style={[styles.cardLabel, { color: theme.textLight }]}>
                  {isInputCollapsed ? 'Modo Simple' : 'Texto en Chino'}
                </Text>
                {isInputCollapsed ? <ChevronDown size={14} color={theme.textLight} /> : <ChevronUp size={14} color={theme.textLight} />}
              </TouchableOpacity>
              
              <View style={styles.headerActions}>
                {hasResults && !isInputCollapsed && (
                  <TouchableOpacity 
                    style={styles.miniTranslateBtn}
                    onPress={() => handleTranslate()}
                    disabled={isLoading}
                  >
                    <Send size={16} color={isLoading ? theme.textLight : COLORS.primary} />
                  </TouchableOpacity>
                )}
                <TouchableOpacity onPress={clear} disabled={!inputText}>
                  <Trash2 size={16} color={inputText ? COLORS.error : theme.textLight} />
                </TouchableOpacity>
              </View>
            </View>
            
            {isInputCollapsed ? (
              <TouchableOpacity onPress={() => setIsInputCollapsed(false)} style={styles.collapsedPreview}>
                <Text numberOfLines={1} style={{ color: theme.text, fontSize: 13, opacity: 0.6, fontStyle: 'italic' }}>
                  {inputText || "Sin texto..."}
                </Text>
              </TouchableOpacity>
            ) : (
              <>
                <ScrollView 
                    ref={inputScrollRef}
                    style={{ flex: 1 }}
                    showsVerticalScrollIndicator={false}
                    onScroll={handleInputScroll}
                    scrollEventThrottle={16}
                >
                    <TextInput
                      style={[styles.input, { color: theme.text, fontSize: fontSize }]}
                      placeholder="Escribe o pega texto..."
                      placeholderTextColor={theme.textLight}
                      multiline
                      scrollEnabled={false}
                      value={inputText}
                      onChangeText={setInputText}
                      textAlignVertical="top"
                    />
                </ScrollView>
                {!hasResults && (
                  <View style={[styles.actionRow, { borderTopColor: theme.border }]}>
                    <LanguageSelector targetLang={targetLang} setTargetLang={setTargetLang} theme={theme} />
                    <TranslateButton isLoading={isLoading} onPress={handleTranslate} onFinish={() => setIsInputCollapsed(true)} disabled={!inputText.trim()} />
                  </View>
                )}
              </>
            )}
          </Animated.View>

          {/* Draggable Divider */}
          {!isInputCollapsed && (
            <View {...panResponder.panHandlers} style={styles.dividerZone}>
              <View style={[styles.dividerHandle, { backgroundColor: theme.border, borderColor: theme.card }]}>
                <GripHorizontal size={16} color={theme.textLight} />
              </View>
            </View>
          )}

          {/* Bottom Card (Results) */}
          <View style={[styles.card, styles.bottomCard, { 
            backgroundColor: theme.card, 
            borderColor: theme.border, 
            flex: 1 
          }]}>
            <View style={styles.cardHeader}>
              <Text style={[styles.cardLabel, { color: theme.textLight }]}>
                Pronunciación y Gloss ({targetLang.toUpperCase()})
              </Text>
              <Languages size={14} color={COLORS.primary} />
            </View>
            
            {hasResults ? (
              <ScrollView 
                ref={scrollRef}
                style={styles.internalScroll}
                contentContainerStyle={styles.resultsContent}
                showsVerticalScrollIndicator={false}
                onScroll={handleOutputScroll}
                scrollEventThrottle={16}
              >
                <View style={styles.pinyinContainer}>
                  {pinyinGroups.map((group, gIdx) => (
                    <View key={`group-${gIdx}-${group.tokens.length}`} style={styles.groupContainer}>
                      <View style={styles.pinyinGroup}>
                        {group.tokens.map((token, tIdx) => (
                          <PinyinCard 
                            key={`token-${gIdx}-${tIdx}`} 
                            token={token} 
                            textColor={theme.text} 
                            fontSizeMultiplier={fontSize / 17}
                            onPress={() => setSelectedWord({ ...token, fullTranslation: group.translation || '' })}
                          />
                        ))}
                      </View>
                      {!!group.translation && (
                        <Text style={[styles.groupTranslation, { color: COLORS.primary, fontSize: fontSize * 0.75 }]}>
                          {group.translation}
                        </Text>
                      )}
                    </View>
                  ))}
                </View>
                
                {/* Credits */}
                <View style={styles.creditsContainer}>
                    <Text style={[styles.creditsText, { color: theme.textLight }]}>
                        Desarrollado por Erick Villon
                    </Text>
                </View>
              </ScrollView>
            ) : (
              <View style={styles.emptyResults}>
                <Languages size={48} color={theme.border} style={{ opacity: 0.5 }} />
                <Text style={[styles.emptyStateText, { color: theme.textLight, fontSize: 14 }]}>
                  Los resultados aparecerán aquí
                </Text>
              </View>
            )}
          </View>
        </View>

        {showScrollTop && (
          <TouchableOpacity 
            style={[styles.scrollTopBtn, { backgroundColor: COLORS.primary }]} 
            onPress={scrollToTop}
          >
            <ArrowUp size={24} color={COLORS.white} />
          </TouchableOpacity>
        )}
      </KeyboardAvoidingView>

      {/* Dictionary Modal */}
      <Modal visible={!!selectedWord} transparent animationType="slide" onRequestClose={() => setSelectedWord(null)}>
        <Pressable style={styles.modalOverlay} onPress={() => setSelectedWord(null)}>
            <View style={[styles.modalContent, { backgroundColor: theme.card }]}>
                <View style={styles.modalHeader}>
                    <View style={styles.modalHeaderTitle}><BookOpen size={20} color={COLORS.primary} /><Text style={[styles.modalTitle, { color: theme.text }]}>Diccionario</Text></View>
                    <TouchableOpacity onPress={() => setSelectedWord(null)}><X size={24} color={theme.textLight} /></TouchableOpacity>
                </View>
                {selectedWord && (
                    <View style={styles.wordDetail}>
                        <View style={styles.wordHero}>
                            <Text style={[styles.bigChar, { color: theme.text }]}>{selectedWord.char}</Text>
                            <View style={styles.wordHeroInfo}>
                                <Text style={styles.bigPinyin}>{selectedWord.pinyin}</Text>
                                <Text style={[styles.wordType, { color: theme.textLight }]}>Kaijin / Palabra</Text>
                            </View>
                        </View>
                        <View style={[styles.detailSection, { borderLeftColor: COLORS.primary }]}>
                            <Text style={[styles.detailLabel, { color: theme.textLight }]}>Significado:</Text>
                            <Text style={[styles.detailText, { color: theme.text }]}>{selectedWord.fullTranslation || "N/A"}</Text>
                        </View>
                        <TouchableOpacity style={[styles.modalBtn, { backgroundColor: COLORS.primary }]} onPress={() => setSelectedWord(null)}>
                            <Text style={styles.modalBtnText}>Entendido</Text>
                        </TouchableOpacity>
                    </View>
                )}
            </View>
        </Pressable>
      </Modal>

      {/* Settings Modal */}
      <Modal visible={isSettingsVisible} transparent animationType="fade" onRequestClose={() => setIsSettingsVisible(false)}>
        <Pressable style={styles.modalOverlay} onPress={() => setIsSettingsVisible(false)}>
            <View style={[styles.settingsContent, { backgroundColor: theme.card }]}>
                <View style={styles.modalHeader}>
                    <View style={styles.modalHeaderTitle}><Type size={20} color={COLORS.primary} /><Text style={[styles.modalTitle, { color: theme.text }]}>Ajustes de Texto</Text></View>
                    <TouchableOpacity onPress={() => setIsSettingsVisible(false)}><X size={24} color={theme.textLight} /></TouchableOpacity>
                </View>
                
                <Text style={[styles.detailLabel, { color: theme.textLight, marginBottom: 16 }]}>Tamaño de letra: {fontSize}px</Text>
                
                <View style={styles.sliderContainer}>
                  <TouchableOpacity onPress={() => setFontSize(prev => Math.max(12, prev - 1))} style={styles.sizeBtn}>
                    <Text style={{ fontSize: 18, color: theme.text }}>A-</Text>
                  </TouchableOpacity>
                  
                  <View style={styles.sliderTrack}>
                    <View style={[styles.sliderFill, { width: `${((fontSize - 12) / 18) * 100}%`, backgroundColor: COLORS.primary }]} />
                  </View>
                  
                  <TouchableOpacity onPress={() => setFontSize(prev => Math.min(30, prev + 1))} style={styles.sizeBtn}>
                    <Text style={{ fontSize: 18, color: theme.text }}>A+</Text>
                  </TouchableOpacity>
                </View>

                <TouchableOpacity 
                    style={[styles.modalBtn, { backgroundColor: COLORS.primary, marginTop: 30 }]} 
                    onPress={() => setIsSettingsVisible(false)}
                >
                    <Text style={styles.modalBtnText}>Guardar</Text>
                </TouchableOpacity>
            </View>
        </Pressable>
      </Modal>
      {/* Info Modal */}
      <Modal visible={isInfoVisible} transparent animationType="fade" onRequestClose={() => setIsInfoVisible(false)}>
        <Pressable style={styles.centeredModalOverlay} onPress={() => setIsInfoVisible(false)}>
            <View style={[styles.infoContent, { backgroundColor: theme.card }]}>
                <View style={styles.modalHeader}>
                    <View style={styles.modalHeaderTitle}><Info size={20} color={COLORS.primary} /><Text style={[styles.modalTitle, { color: theme.text }]}>Información</Text></View>
                    <TouchableOpacity onPress={() => setIsInfoVisible(false)}><X size={24} color={theme.textLight} /></TouchableOpacity>
                </View>
                
                <View style={styles.infoBody}>
                  <View style={[styles.appLogoContainer, { backgroundColor: COLORS.primary + '10' }]}>
                    <Languages size={40} color={COLORS.primary} />
                  </View>
                  <Text style={[styles.appName, { color: theme.text }]}>Traductor Chino v2.0</Text>
                  <Text style={[styles.appVersion, { color: theme.textLight }]}>Versión Estable</Text>
                  
                  <View style={[styles.infoDivider, { backgroundColor: theme.border }]} />
                  
                  <Text style={[styles.developerLabel, { color: theme.textLight }]}>Desarrollado por</Text>
                  <Text style={[styles.developerName, { color: COLORS.primary }]}>Erick Villon</Text>
                  
                  <Text style={[styles.appDescription, { color: theme.textLight }]}>
                    Una herramienta diseñada para facilitar el aprendizaje del chino mandarín mediante traducción interlineal y herramientas didácticas.
                  </Text>
                </View>

                <TouchableOpacity 
                    style={[styles.modalBtn, { backgroundColor: COLORS.primary, marginTop: 20 }]} 
                    onPress={() => setIsInfoVisible(false)}
                >
                    <Text style={styles.modalBtnText}>Cerrar</Text>
                </TouchableOpacity>
            </View>
        </Pressable>
      </Modal>
    </SafeAreaView>
  );
}

// Sub-components
const LanguageSelector = ({ targetLang, setTargetLang, theme }: any) => (
  <View style={[styles.langSelector, { backgroundColor: theme.background }]}>
    <TouchableOpacity style={[styles.langBtn, targetLang === 'es' && styles.langBtnActive]} onPress={() => setTargetLang('es')}>
      <Text style={[styles.langBtnText, targetLang === 'es' && styles.langBtnTextActive]}>ES</Text>
    </TouchableOpacity>
    <TouchableOpacity style={[styles.langBtn, targetLang === 'en' && styles.langBtnActive]} onPress={() => setTargetLang('en')}>
      <Text style={[styles.langBtnText, targetLang === 'en' && styles.langBtnTextActive]}>EN</Text>
    </TouchableOpacity>
  </View>
);

const TranslateButton = ({ isLoading, onPress, onFinish, disabled }: any) => (
  <TouchableOpacity style={styles.translateBtn} onPress={() => { onPress(); onFinish(); }} disabled={isLoading || disabled}>
    <LinearGradient colors={COLORS.gradientPrimary as any} style={styles.gradient} start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}>
      {isLoading ? <ActivityIndicator color={COLORS.white} size="small" /> : <><Text style={styles.translateBtnText}>Traducir</Text><Send size={16} color={COLORS.white} /></>}
    </LinearGradient>
  </TouchableOpacity>
);

const styles = StyleSheet.create({
  container: { flex: 1 },
  splitWrapper: { flex: 1, paddingHorizontal: SPACING.md, paddingBottom: SPACING.md },
  headerRightContainer: { flexDirection: 'row', gap: 4 },
  headerIconBtn: { width: 36, height: 36, borderRadius: 18, justifyContent: 'center', alignItems: 'center' },
  card: { borderRadius: BORDER_RADIUS.lg, padding: SPACING.md, borderWidth: 1, elevation: 2, shadowColor: '#000', shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.1, shadowRadius: 2 },
  topCard: { marginTop: SPACING.md, zIndex: 2 },
  bottomCard: { zIndex: 1 },
  dividerZone: { height: 20, zIndex: 10, marginTop: -10, marginBottom: -10, alignItems: 'center', justifyContent: 'center' },
  dividerHandle: { width: 44, height: 22, borderRadius: 11, borderWidth: 2, alignItems: 'center', justifyContent: 'center', elevation: 4, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.2, shadowRadius: 3 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: SPACING.xs },
  headerActions: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  miniTranslateBtn: { width: 32, height: 32, borderRadius: 16, backgroundColor: 'rgba(37, 99, 235, 0.1)', justifyContent: 'center', alignItems: 'center' },
  collapseTrigger: { flexDirection: 'row', alignItems: 'center', gap: 6, flex: 1 },
  cardLabel: { fontSize: 10, fontWeight: '800', textTransform: 'uppercase', letterSpacing: 1.2 },
  input: { paddingTop: SPACING.xs, fontWeight: '500', lineHeight: 22 },
  collapsedPreview: { paddingVertical: 4 },
  actionRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: SPACING.sm, borderTopWidth: 1, paddingTop: SPACING.sm },
  langSelector: { flexDirection: 'row', borderRadius: BORDER_RADIUS.md, padding: 2 },
  langBtn: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: BORDER_RADIUS.sm },
  langBtnActive: { backgroundColor: COLORS.white, elevation: 1 },
  langBtnText: { fontSize: 11, fontWeight: '800', color: '#64748b' },
  langBtnTextActive: { color: COLORS.primary },
  translateBtn: { borderRadius: BORDER_RADIUS.md, overflow: 'hidden' },
  gradient: { flexDirection: 'row', alignItems: 'center', paddingHorizontal: 14, paddingVertical: 7, gap: 6 },
  translateBtnText: { color: COLORS.white, fontWeight: '700', fontSize: 13 },
  internalScroll: { flex: 1, marginTop: SPACING.xs },
  resultsContent: { paddingBottom: 20 },
  pinyinContainer: { marginTop: 4 },
  pinyinGroup: { flexDirection: 'row', flexWrap: 'wrap' },
  groupContainer: { marginBottom: SPACING.sm },
  groupTranslation: { fontWeight: '600', marginTop: 1, paddingHorizontal: 4, fontStyle: 'italic', lineHeight: 16 },
  creditsContainer: { marginTop: 30, alignItems: 'center', opacity: 0.4 },
  creditsText: { fontSize: 10, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 2 },
  emptyResults: { flex: 1, alignItems: 'center', justifyContent: 'center', opacity: 0.3 },
  emptyStateText: { marginTop: SPACING.sm, fontWeight: '500' },
  progressContainer: { height: 2, width: '100%' },
  progressBar: { height: '100%', backgroundColor: COLORS.primary },
  scrollTopBtn: { position: 'absolute', bottom: 30, right: 30, width: 48, height: 48, borderRadius: 24, justifyContent: 'center', alignItems: 'center', elevation: 5, shadowColor: '#000', shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.3, shadowRadius: 4 },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  centeredModalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'center', alignItems: 'center', padding: SPACING.xl },
  modalContent: { borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: SPACING.lg, minHeight: 300, shadowColor: '#000', shadowOffset: { width: 0, height: -4 }, shadowOpacity: 0.1, shadowRadius: 10, elevation: 20 },
  settingsContent: { borderTopLeftRadius: 24, borderTopRightRadius: 24, padding: SPACING.lg, minHeight: 250 },
  infoContent: { borderRadius: 24, padding: SPACING.lg, width: '100%', maxWidth: 340, shadowColor: '#000', shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.2, shadowRadius: 15, elevation: 25 },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: SPACING.lg },
  modalHeaderTitle: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  modalTitle: { fontSize: 16, fontWeight: '800', textTransform: 'uppercase' },
  wordDetail: { flex: 1 },
  infoBody: { alignItems: 'center', paddingVertical: SPACING.md },
  appLogoContainer: { width: 80, height: 80, borderRadius: 20, justifyContent: 'center', alignItems: 'center', marginBottom: SPACING.md },
  appName: { fontSize: 20, fontWeight: '800', marginBottom: 4 },
  appVersion: { fontSize: 14, fontWeight: '600', marginBottom: SPACING.lg },
  infoDivider: { width: '60%', height: 1, marginBottom: SPACING.lg },
  developerLabel: { fontSize: 12, fontWeight: '700', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 4 },
  developerName: { fontSize: 22, fontWeight: '900', marginBottom: SPACING.md },
  appDescription: { fontSize: 14, textAlign: 'center', lineHeight: 20, paddingHorizontal: SPACING.sm },
  wordHero: { flexDirection: 'row', alignItems: 'center', marginBottom: SPACING.xl, gap: 20 },
  bigChar: { fontSize: 64, fontWeight: 'bold' },
  wordHeroInfo: { flex: 1 },
  bigPinyin: { fontSize: 24, color: COLORS.primary, fontWeight: '700', marginBottom: 4 },
  wordType: { fontSize: 14, fontStyle: 'italic' },
  detailSection: { borderLeftWidth: 4, paddingLeft: 16, marginBottom: SPACING.xl },
  detailLabel: { fontSize: 12, fontWeight: '700', marginBottom: 8, textTransform: 'uppercase' },
  detailText: { fontSize: 18, lineHeight: 26, fontWeight: '500' },
  modalBtn: { height: 50, borderRadius: 12, justifyContent: 'center', alignItems: 'center' },
  modalBtnText: { color: COLORS.white, fontSize: 16, fontWeight: '700' },
  sliderContainer: { flexDirection: 'row', alignItems: 'center', gap: 15 },
  sizeBtn: { padding: 10 },
  sliderTrack: { flex: 1, height: 8, backgroundColor: 'rgba(128,128,128,0.2)', borderRadius: 4, overflow: 'hidden' },
  sliderFill: { height: '100%' },
});
