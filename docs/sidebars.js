/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {

  docsSidebar: [
    'intro',
    'playground',
    'installation',
    'getting-started',
    'examples',
    'architecture',
    {
      type: 'category',
      label: 'Concepts',
      items: [
        'concepts/autopilots',
        'concepts/policies',
        'concepts/observations',
        'concepts/actions',
        'concepts/steps',
        'concepts/filesystem',
        'concepts/hooks',
        'concepts/plugins',
        'concepts/history',
        'concepts/additional',
      ],
    },
    {
      type: 'category',
      label: 'Walkthroughs',
      items: [
        'walkthroughs/building-plugin',
      ],
    },
    'api',
    'languages',
    'models',
    'configuration',
    {
      type: 'category',
      label: 'References',
      items: [
        'references/telemetry',
        'references/donation',
      ],
    },
    'random',
  ],
};

module.exports = sidebars;