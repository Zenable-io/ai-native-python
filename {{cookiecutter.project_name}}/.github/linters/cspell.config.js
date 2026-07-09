'use strict'

let per_repo_dictionary_file;

if (process.env.GITHUB_WORKSPACE) {
  per_repo_dictionary_file = `${process.env.GITHUB_WORKSPACE}/.github/etc/dictionary.txt`;
} else {
  /** Assume it's running local and use .github **/
  per_repo_dictionary_file = '../../.github/etc/dictionary.txt';
}

/** @type { import("@cspell/cspell-types").CSpellUserSettings } */
const cspell = {
  language: 'en',
  dictionaries: [
    'bash',
    'companies',
    'cpp',
    'csharp',
    'css',
    'en-gb',
    'en_US',
    'go',
    'html',
    'latex',
    'misc',
    'node',
    'npm',
    'per-repository dictionary',
    'php',
    'powershell',
    'python',
    'softwareTerms',
    'typescript'
  ],
  dictionaryDefinitions: [
    {
      name: 'per-repository dictionary',
      path: per_repo_dictionary_file,
    }
  ],
  flagWords: [],
  ignoreRegExpList: [],
  minWordLength: 4
}

module.exports = cspell
