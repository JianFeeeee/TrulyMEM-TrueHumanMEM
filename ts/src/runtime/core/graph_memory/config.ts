export interface TrulyMEMConfig {
  dbPath: string;
  autoSave: boolean;
  debug: boolean;
}

export const DEFAULT_CONFIG: TrulyMEMConfig = {
  dbPath: '.trulymem/graph_memory.db',
  autoSave: true,
  debug: false
};

let globalConfig: TrulyMEMConfig = { ...DEFAULT_CONFIG };

export function initConfig(config: Partial<TrulyMEMConfig> = {}): TrulyMEMConfig {
  globalConfig = { ...DEFAULT_CONFIG, ...config };
  return globalConfig;
}

export function getConfig(): TrulyMEMConfig {
  return globalConfig;
}

export function setDbPath(dbPath: string): void {
  globalConfig.dbPath = dbPath;
}

export function getDbPath(): string {
  return globalConfig.dbPath;
}

export function setAutoSave(autoSave: boolean): void {
  globalConfig.autoSave = autoSave;
}

export function isAutoSave(): boolean {
  return globalConfig.autoSave;
}
