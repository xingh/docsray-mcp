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
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: [
        'getting-started/installation',
        'getting-started/quickstart',
        'getting-started/configuration',
      ],
    },
    {
      type: 'category',
      label: 'Providers',
      items: [
        'providers/overview',
        'providers/llamaparse',
        'providers/pymupdf',
        'providers/comparison',
      ],
    },
    {
      type: 'category',
      label: 'Tools',
      items: [
        'tools/peek',
        'tools/map',
        'tools/xray',
        'tools/extract',
        'tools/seek',
      ],
    },
    {
      type: 'category',
      label: 'Advanced',
      items: [
        'advanced/caching',
        'advanced/performance',
        'advanced/troubleshooting',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api/tools',
        'api/configuration',
      ],
    },
  ],
};

export default sidebars;