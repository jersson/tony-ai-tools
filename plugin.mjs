import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';

const dir = dirname(fileURLToPath(import.meta.url));
const skillsDir = resolve(dir, 'skills');

export default async () => {
  return {
    config: (cfg) => {
      try {
        cfg.skills = cfg.skills || {};
        cfg.skills.paths = cfg.skills.paths || [];
        if (!cfg.skills.paths.includes(skillsDir)) {
          cfg.skills.paths.push(skillsDir);
        }

        cfg.command = cfg.command || {};
        cfg.command.tony = {
          template: 'Load the explore-idea skill and follow its workflow step by step.',
          description: 'Entry point (defaults to explore-idea) — loads global config and helps turn an idea into epics or user stories'
        };
        cfg.command['tony explore-idea'] = {
          template: 'Load the explore-idea skill and follow its workflow step by step.',
          description: 'Entry point — loads global config, captures the idea, and routes to the right skill'
        };
        cfg.command['tony build-knowledge'] = {
          template: 'Load the build-knowledge skill and follow its workflow step by step.',
          description: 'Run the document pipeline — convert, quality-gate, wiki, indexes — and synthesize a cited knowledge base'
        };
        cfg.command['tony create-epic'] = {
          template: 'Load the create-epic skill and follow its workflow step by step.',
          description: 'Understand an idea and shape it into one or more well-formed epics'
        };
        cfg.command['tony create-user-story'] = {
          template: 'Load the create-user-story skill and follow its workflow step by step.',
          description: 'Understand an idea (or epic) and draft user stories validated with INVEST + 3C'
        };

        const globalsDir = resolve(skillsDir, 'globals');
        cfg.permission = cfg.permission || {};
        cfg.permission.external_directory = cfg.permission.external_directory || {};
        cfg.permission.external_directory[`${globalsDir}/**`] = 'allow';
        cfg.permission.external_directory['.tony/**'] = 'allow';
      } catch (err) {
        console.error('[tony/ai-tools] Plugin config error:', err.message);
      }
    }
  };
};
