import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { existsSync, mkdirSync, writeFileSync } from 'fs';
import { findConfigDir, readConfig, writeConfig } from './config.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));

function pluginPath() {
  return resolve(__dirname, '..', 'plugin.mjs');
}

// Creates <project>/.tony/raw-documents/ so the drop point exists from
// minute zero. Idempotent; never touches existing content.
export function scaffoldTonyDir(projectDir) {
  const rawDocuments = resolve(projectDir || process.cwd(), '.tony', 'raw-documents');
  const created = !existsSync(rawDocuments);
  mkdirSync(rawDocuments, { recursive: true });

  const gitkeep = resolve(rawDocuments, '.gitkeep');
  if (!existsSync(gitkeep)) {
    writeFileSync(gitkeep, '');
  }

  if (created) {
    console.log(`Scaffolded ${rawDocuments} — drop source documents there for /tony build-knowledge`);
  }
}

function alreadyInstalled(plugin, data) {
  const entries = data.plugin || [];
  for (const entry of entries) {
    if (entry === plugin) return true;
    if (entry.includes('@tony/ai-tools') || entry.includes('tony-ai-tools')) return true;
  }
  return false;
}

export function installOpenCode(projectDir) {
  const configDir = findConfigDir(projectDir) || projectDir;
  const plugin = pluginPath();
  const existing = readConfig(configDir);

  if (existing) {
    if (alreadyInstalled(plugin, existing.data)) {
      console.log(`Tony already installed in ${existing.filePath}`);
      scaffoldTonyDir(configDir);
      return;
    }

    existing.data.plugin = existing.data.plugin || [];
    existing.data.plugin.push(plugin);

    const result = writeConfig(configDir, existing.data);
    if (result.converted) {
      console.log(`Tony plugin added — converted ${existing.filePath} -> ${result.filePath}`);
    } else {
      console.log(`Tony plugin added to ${result.filePath}`);
    }
  } else {
    writeConfig(configDir, { plugin: [plugin] });
    console.log(`Created ${resolve(configDir, 'opencode.json')} with Tony plugin`);
  }

  scaffoldTonyDir(configDir);
}

export function uninstallOpenCode(projectDir) {
  const configDir = findConfigDir(projectDir) || projectDir;
  const plugin = pluginPath();
  const existing = readConfig(configDir);

  if (!existing) {
    console.log('No opencode config found.');
    return;
  }

  const entries = existing.data.plugin || [];
  const idx = entries.indexOf(plugin);
  if (idx === -1) {
    console.log('Tony plugin not found in config.');
    return;
  }

  entries.splice(idx, 1);
  existing.data.plugin = entries.length ? entries : undefined;

  writeConfig(configDir, existing.data);
  console.log(`Tony plugin removed from ${existing.filePath}`);
}
