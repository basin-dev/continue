import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/__docusaurus/debug',
    component: ComponentCreator('/__docusaurus/debug', 'aa1'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/config',
    component: ComponentCreator('/__docusaurus/debug/config', 'b68'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/content',
    component: ComponentCreator('/__docusaurus/debug/content', '880'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/globalData',
    component: ComponentCreator('/__docusaurus/debug/globalData', '5e5'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/metadata',
    component: ComponentCreator('/__docusaurus/debug/metadata', '4fa'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/registry',
    component: ComponentCreator('/__docusaurus/debug/registry', '056'),
    exact: true
  },
  {
    path: '/__docusaurus/debug/routes',
    component: ComponentCreator('/__docusaurus/debug/routes', '845'),
    exact: true
  },
  {
    path: '/blog',
    component: ComponentCreator('/blog', '7bb'),
    exact: true
  },
  {
    path: '/blog/archive',
    component: ComponentCreator('/blog/archive', '5ee'),
    exact: true
  },
  {
    path: '/blog/first-blog-post',
    component: ComponentCreator('/blog/first-blog-post', '921'),
    exact: true
  },
  {
    path: '/blog/long-blog-post',
    component: ComponentCreator('/blog/long-blog-post', '6c1'),
    exact: true
  },
  {
    path: '/blog/mdx-blog-post',
    component: ComponentCreator('/blog/mdx-blog-post', '835'),
    exact: true
  },
  {
    path: '/blog/tags',
    component: ComponentCreator('/blog/tags', 'f86'),
    exact: true
  },
  {
    path: '/blog/tags/docusaurus',
    component: ComponentCreator('/blog/tags/docusaurus', '3ed'),
    exact: true
  },
  {
    path: '/blog/tags/facebook',
    component: ComponentCreator('/blog/tags/facebook', 'd05'),
    exact: true
  },
  {
    path: '/blog/tags/hello',
    component: ComponentCreator('/blog/tags/hello', '0b6'),
    exact: true
  },
  {
    path: '/blog/tags/hola',
    component: ComponentCreator('/blog/tags/hola', 'c81'),
    exact: true
  },
  {
    path: '/blog/welcome',
    component: ComponentCreator('/blog/welcome', '749'),
    exact: true
  },
  {
    path: '/markdown-page',
    component: ComponentCreator('/markdown-page', 'e4d'),
    exact: true
  },
  {
    path: '/docs',
    component: ComponentCreator('/docs', '838'),
    routes: [
      {
        path: '/docs/category/concepts',
        component: ComponentCreator('/docs/category/concepts', 'ab6'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/category/tutorial---extras',
        component: ComponentCreator('/docs/category/tutorial---extras', 'f09'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/concepts/actions',
        component: ComponentCreator('/docs/concepts/actions', '093'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/concepts/agents',
        component: ComponentCreator('/docs/concepts/agents', '518'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/concepts/filesystem',
        component: ComponentCreator('/docs/concepts/filesystem', '314'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/concepts/hooks',
        component: ComponentCreator('/docs/concepts/hooks', 'b0e'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/concepts/markdown-features',
        component: ComponentCreator('/docs/concepts/markdown-features', '039'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/concepts/notes',
        component: ComponentCreator('/docs/concepts/notes', '732'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/concepts/other',
        component: ComponentCreator('/docs/concepts/other', '2fc'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/concepts/resources',
        component: ComponentCreator('/docs/concepts/resources', 'df4'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/concepts/workflows',
        component: ComponentCreator('/docs/concepts/workflows', '778'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/intro',
        component: ComponentCreator('/docs/intro', 'aed'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/tutorial-extras/manage-docs-versions',
        component: ComponentCreator('/docs/tutorial-extras/manage-docs-versions', 'fdd'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/tutorial-extras/translate-your-site',
        component: ComponentCreator('/docs/tutorial-extras/translate-your-site', '2d7'),
        exact: true,
        sidebar: "tutorialSidebar"
      }
    ]
  },
  {
    path: '/',
    component: ComponentCreator('/', 'f2f'),
    exact: true
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
