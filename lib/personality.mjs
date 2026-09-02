import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { parseJsonc } from './jsonc.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));

export const PERSONALITY_FILENAME = 'personality.json';

// Allowed configuration parameters. Anything else in the file is unmapped and
// rejected so the config cannot drift from the shape the skills understand.
export const ARCHETYPES = ['evidence-driven', 'speed-to-market', 'customer-vision', 'balanced'];

// Preset option lists. The capture flow has the PO pick from these — they are
// not free-form. Any other value is rejected so a config cannot drift from what
// the skills understand.
export const TONES = ['direct', 'warm', 'concise', 'formal', 'approachable'];
export const WORKING_RULES = ['evidence-first', 'ship-fast', 'user-centered', 'balanced'];

// key -> validator(value) returning a normalized value or throwing.
const SCHEMA = {
  archetype: (v) => {
    if (!ARCHETYPES.includes(v)) {
      throw new TypeError(`personality.archetype must be one of ${ARCHETYPES.join(' | ')}`);
    }
    return v;
  },
  tone: (v) => {
    if (!TONES.includes(v)) {
      throw new TypeError(`personality.tone must be one of ${TONES.join(' | ')}`);
    }
    return v;
  },
  working_rule: (v) => {
    if (!WORKING_RULES.includes(v)) {
      throw new TypeError(`personality.working_rule must be one of ${WORKING_RULES.join(' | ')}`);
    }
    return v;
  },
  updated_at: (v) => {
    if (typeof v !== 'string' || Number.isNaN(Date.parse(v))) {
      throw new TypeError('personality.updated_at must be an ISO-8601 timestamp string');
    }
    return v;
  },
};

const REQUIRED = ['archetype', 'tone', 'working_rule', 'updated_at'];

function personalityPath(projectDir) {
  return resolve(projectDir, '.tony', PERSONALITY_FILENAME);
}

// Parses and validates a personality config. Throws on any unmapped key,
// missing required field, or invalid value — the caller treats an exception
// as a processing error (never silently ignores an unknown parameter).
export function parsePersonality(raw) {
  let data;
  try {
    data = parseJsonc(raw);
  } catch (err) {
    throw new Error(`personality config is not valid JSON/JSONC: ${err.message}`);
  }

  if (typeof data !== 'object' || data === null || Array.isArray(data)) {
    throw new Error('personality config must be a JSON object');
  }

  const unknown = Object.keys(data).filter((k) => !(k in SCHEMA));
  if (unknown.length > 0) {
    throw new Error(
      `personality config has unmapped key(s): ${unknown.join(', ')}. Allowed: ${Object.keys(SCHEMA).join(', ')}`,
    );
  }

  for (const key of REQUIRED) {
    if (!(key in data)) {
      throw new Error(`personality config missing required key: ${key}`);
    }
  }

  const normalized = {};
  for (const [key, validate] of Object.entries(SCHEMA)) {
    if (key in data) normalized[key] = validate(data[key]);
  }
  return normalized;
}

// Loads and validates <project>/<.tony/personality.json. Returns null when the
// file does not exist. Throws a processing error on malformed/unmapped content,
// per the strict-config rule.
export function loadPersonality(projectDir) {
  const filePath = personalityPath(projectDir);
  if (!existsSync(filePath)) return null;
  return parsePersonality(readFileSync(filePath, 'utf-8'));
}

// Writes a validated personality config. Builds .tony/ if missing.
export function savePersonality(projectDir, data) {
  const validated = parsePersonality(JSON.stringify(data));
  const filePath = personalityPath(projectDir);
  mkdirSync(resolve(projectDir, '.tony'), { recursive: true });
  writeFileSync(filePath, JSON.stringify(validated, null, 2) + '\n');
  return { filePath, personality: validated };
}
