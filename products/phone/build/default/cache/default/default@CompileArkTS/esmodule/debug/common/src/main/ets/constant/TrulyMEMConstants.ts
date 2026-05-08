export class Constants {
    static readonly DB_NAME: string = 'trulymem.db';
    static readonly CONFIG_PREF_NAME: string = 'trulymem_config';
    static readonly DEFAULT_BASE_URL: string = 'https://api.deepseek.com';
    static readonly DEFAULT_MODEL: string = 'deepseek-chat';
    static readonly SECURITY_LEVEL: number = 1; // S1
    // Table names
    static readonly TABLE_NODES: string = 'nodes';
    static readonly TABLE_RELATIONS: string = 'relations';
    static readonly TABLE_CHAT: string = 'chat_records';
    // SQL definitions
    static readonly SQL_CREATE_NODES: string = `
        CREATE TABLE IF NOT EXISTS nodes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            type TEXT DEFAULT 'concept',
            mentions INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            updated_at TEXT DEFAULT (datetime('now','localtime'))
        )`;
    static readonly SQL_CREATE_RELATIONS: string = `
        CREATE TABLE IF NOT EXISTS relations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            relation TEXT NOT NULL,
            object_id INTEGER NOT NULL,
            weight REAL DEFAULT 1.0,
            created_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (subject_id) REFERENCES nodes(id) ON DELETE CASCADE,
            FOREIGN KEY (object_id) REFERENCES nodes(id) ON DELETE CASCADE
        )`;
    static readonly SQL_CREATE_CHAT: string = `
        CREATE TABLE IF NOT EXISTS chat_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            tools TEXT,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )`;
}
