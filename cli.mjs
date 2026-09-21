#!/usr/bin/env node

import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { installOpenCode, uninstallOpenCode } from './lib/install-opencode.mjs';
import { installClaude, uninstallClaude } from './lib/install-claude.mjs';
import { installCopilot, uninstallCopilot } from './lib/install-copilot.mjs';
import { printBanner, printFooter } from './lib/banner.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const { version } = JSON.parse(readFileSync(join(__dirname, 'package.json'), 'utf-8'));

const args = process.argv.slice(2);
const command = args[0];
const globalFlag = args.includes('--global');
const installTargets = [
  {
    flag: '--opencode',
    install: installOpenCode,
    uninstall: uninstallOpenCode,
    supportsGlobal: false,
    installHelp: 'tony install --opencode                 # repository level (current directory)',
    uninstallHelp: 'tony uninstall --opencode',
  },
  {
    flag: '--claude-code',
    install: installClaude,
    uninstall: uninstallClaude,
    supportsGlobal: true,
    installHelp: 'tony install --claude-code [--global]   # repository level; --global installs for all projects',
    uninstallHelp: 'tony uninstall --claude-code [--global]',
  },
  {
    flag: '--copilot',
    install: installCopilot,
    uninstall: uninstallCopilot,
    supportsGlobal: true,
    installHelp: 'tony install --copilot [--global]       # repository level; --global installs for all projects',
    uninstallHelp: 'tony uninstall --copilot [--global]',
  },
];

function showHelp() {
  console.log('Usage:');
  for (const target of installTargets) {
    console.log(`  ${target.installHelp}`);
  }
  for (const target of installTargets) {
    console.log(`  ${target.uninstallHelp}`);
  }
  console.log('  tony --version, -v                      # show version');
}

function rejectGlobal(target) {
  console.error(`--global is not supported with ${target.flag}: this target installs at repository level.`);
  process.exitCode = 1;
}

printBanner();

if (command === '--version' || command === '-v') {
  console.log(version);
} else {
  const target = installTargets.find(({ flag }) => args.includes(flag));
  const action = command === 'install' || command === 'uninstall' ? command : null;

  if (!target || !action) {
    showHelp();
  } else if (globalFlag && !target.supportsGlobal) {
    rejectGlobal(target);
  } else {
    target[action](globalFlag ? null : process.cwd());
  }
}

printFooter();
