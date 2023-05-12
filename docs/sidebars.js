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
    {
      type: 'category',
      label: 'Concepts',
      items: [
        'concepts/agent',
        'concepts/core',
        'concepts/gui',
        'concepts/history',
        'concepts/ide',
        'concepts/llm',
        'concepts/policy',
        'concepts/sdk',
        'concepts/step',
        'concepts/utilities',
      ],
    },
  ],
};

module.exports = sidebars;