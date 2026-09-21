import {
  lstatSync,
  mkdirSync,
  readlinkSync,
  symlinkSync,
  unlinkSync,
} from 'fs';
import { fileURLToPath } from 'url';
import { homedir } from 'os';
import { resolve } from 'path';
import { scaffoldTonyDir } from './install-opencode.mjs';

const __dirname = fileURLToPath(new URL('.', import.meta.url));
const SKILLS_SOURCE = resolve(__dirname, '..', 'skills');
const SKILLS_NAME = 'tony';

function skillsTarget(projectDir) {
  if (projectDir) return resolve(projectDir, '.github', 'skills', SKILLS_NAME);
  return resolve(homedir(), '.copilot', 'skills', SKILLS_NAME);
}

function isTonyLink(target) {
  try {
    return lstatSync(target).isSymbolicLink()
      && resolve(resolve(target, '..'), readlinkSync(target)) === SKILLS_SOURCE;
  } catch {
    return false;
  }
}

function ensureTargetAvailable(target) {
  try {
    lstatSync(target);
  } catch (error) {
    if (error.code === 'ENOENT') return;
    throw error;
  }
  if (isTonyLink(target)) return;
  throw new Error(`Cannot install Copilot skills: ${target} already exists and is not managed by Tony.`);
}

function installLink(projectDir) {
  const target = skillsTarget(projectDir);
  ensureTargetAvailable(target);
  if (isTonyLink(target)) {
    console.log(`Tony already installed at ${target}`);
    return;
  }

  mkdirSync(resolve(target, '..'), { recursive: true });
  symlinkSync(SKILLS_SOURCE, target, 'dir');
  console.log(`Installed Tony skills at ${target}`);
}

function removeLink(projectDir) {
  const target = skillsTarget(projectDir);
  try {
    lstatSync(target);
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
    console.log('Tony Copilot skills not found.');
    return;
  }
  if (!isTonyLink(target)) {
    console.error(`Cannot uninstall Copilot skills: ${target} is not a Tony-managed link.`);
    process.exitCode = 1;
    return;
  }

  unlinkSync(target);
  console.log(`Removed Tony skills from ${target}`);
}

export function installCopilot(projectDir) {
  try {
    installLink(projectDir);
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
    return;
  }

  if (projectDir) scaffoldTonyDir(projectDir);
  console.log('Restart Copilot CLI or run `/skills reload` to discover Tony skills.');
}

export function uninstallCopilot(projectDir) {
  removeLink(projectDir);
}
