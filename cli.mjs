#!/usr/bin/env node

import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { installOpenCode, uninstallOpenCode } from './lib/install.mjs';
import { installClaude, uninstallClaude } from './lib/install-claude.mjs';
import { printBanner, printFooter } from './lib/banner.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const { version } = JSON.parse(readFileSync(join(__dirname, 'package.json'), 'utf-8'));

const args = process.argv.slice(2);
const command = args[0];
const globalFlag = args.includes('--global');

function showHelp() {
  console.log('Usage:');
  console.log('  tony install --opencode                 # repository level (current directory)');
  console.log('  tony install --claude-code [--global]   # repository level; --global installs for all projects');
  console.log('  tony uninstall --opencode');
  console.log('  tony uninstall --claude-code [--global]');
  console.log('  tony --version, -v                      # show version');
}

function rejectOpenCodeGlobal() {
  console.error('--global is not supported with --opencode: OpenCode installs at repository level.');
  process.exitCode = 1;
}

printBanner();

if (command === '--version' || command === '-v') {
  console.log(version);
} else if (command === 'install') {
  if (args.includes('--opencode')) {
    if (globalFlag) {
      rejectOpenCodeGlobal();
    } else {
      installOpenCode(process.cwd());
    }
  } else if (args.includes('--claude-code')) {
    installClaude(globalFlag ? null : process.cwd());
  } else {
    showHelp();
  }
} else if (command === 'uninstall') {
  if (args.includes('--opencode')) {
    if (globalFlag) {
      rejectOpenCodeGlobal();
    } else {
      uninstallOpenCode(process.cwd());
    }
  } else if (args.includes('--claude-code')) {
    uninstallClaude(globalFlag ? null : process.cwd());
  } else {
    showHelp();
  }
} else {
  showHelp();
}

printFooter();
