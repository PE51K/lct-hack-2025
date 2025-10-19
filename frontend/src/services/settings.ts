// Service for managing user settings in localStorage

export interface UserSettings {
  defaultPrompt?: string;
  postgresCredentials?: {
    host?: string;
    port?: number;
    database?: string;
    username?: string;
    password?: string;
    schema?: string;
    table?: string;
  };
}

const SETTINGS_KEY = 'etl_user_settings';

export const settingsService = {
  // Get all settings
  getSettings(): UserSettings {
    try {
      const stored = localStorage.getItem(SETTINGS_KEY);
      return stored ? JSON.parse(stored) : {};
    } catch (error) {
      console.error('Error loading settings:', error);
      return {};
    }
  },

  // Save all settings
  saveSettings(settings: UserSettings): void {
    try {
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
    } catch (error) {
      console.error('Error saving settings:', error);
    }
  },

  // Get default prompt
  getDefaultPrompt(): string | undefined {
    return this.getSettings().defaultPrompt;
  },

  // Save default prompt
  saveDefaultPrompt(prompt: string): void {
    const settings = this.getSettings();
    settings.defaultPrompt = prompt;
    this.saveSettings(settings);
  },

  // Get PostgreSQL credentials
  getPostgresCredentials(): UserSettings['postgresCredentials'] {
    return this.getSettings().postgresCredentials;
  },

  // Save PostgreSQL credentials
  savePostgresCredentials(credentials: UserSettings['postgresCredentials']): void {
    const settings = this.getSettings();
    settings.postgresCredentials = credentials;
    this.saveSettings(settings);
  },

  // Clear all settings
  clearSettings(): void {
    localStorage.removeItem(SETTINGS_KEY);
  },
};
