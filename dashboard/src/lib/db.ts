import Database from "better-sqlite3";
import path from "path";

const DB_PATH = process.env.DB_PATH || "../data/coke_geo.db";

let db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (!db) {
    const resolvedPath = path.resolve(process.cwd(), DB_PATH);
    db = new Database(resolvedPath, { readonly: true });
    db.pragma("journal_mode = WAL");
  }
  return db;
}
