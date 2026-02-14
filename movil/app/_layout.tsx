import { Stack } from "expo-router";

export default function RootLayout() {
  return (
    <Stack screenOptions={{ 
      headerTitle: "Traductor Chino",
      headerShadowVisible: false,
      headerStyle: { backgroundColor: '#f8fafc' },
      headerTitleStyle: { fontWeight: '800', color: '#2563eb' }
    }} />
  );
}
