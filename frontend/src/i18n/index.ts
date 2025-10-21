import { ru } from './ru';

export const translations = {
  ru,
};

export type Language = keyof typeof translations;

export const defaultLanguage: Language = 'ru';

export function t(key: string): string {
  const keys = key.split('.');
  let value: Record<string, unknown> = translations[defaultLanguage];

  for (const k of keys) {
    value = value?.[k] as Record<string, unknown>;
  }

  return typeof value === 'string' ? value : key;
}

export function tReplace(key: string, replacements: Record<string, string>): string {
  let text = t(key);

  Object.entries(replacements).forEach(([placeholder, value]) => {
    text = text.replace(`{${placeholder}}`, value);
  });

  return text;
}
