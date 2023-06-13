import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/docs/markdown-page',
    component: ComponentCreator('/docs/markdown-page', '221'),
    exact: true
  },
  {
    path: '/docs/',
    component: ComponentCreator('/docs/', '559'),
    routes: [
      {
        path: '/docs/',
        component: ComponentCreator('/docs/', '2bf'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/Installation Guide/gitcode',
        component: ComponentCreator('/docs/Installation Guide/gitcode', '28d'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/Installation Guide/local',
        component: ComponentCreator('/docs/Installation Guide/local', 'e59'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/Tools/coding_tool',
        component: ComponentCreator('/docs/Tools/coding_tool', '0f0'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/Tools/email',
        component: ComponentCreator('/docs/Tools/email', 'f59'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/Tools/google_search',
        component: ComponentCreator('/docs/Tools/google_search', 'd78'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/Tools/google_serp',
        component: ComponentCreator('/docs/Tools/google_serp', 'dc0'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/Tools/image_generation',
        component: ComponentCreator('/docs/Tools/image_generation', '947'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/Tools/jira',
        component: ComponentCreator('/docs/Tools/jira', '16b'),
        exact: true,
        sidebar: "tutorialSidebar"
      },
      {
        path: '/docs/Tools/webscraper',
        component: ComponentCreator('/docs/Tools/webscraper', 'e39'),
        exact: true,
        sidebar: "tutorialSidebar"
      }
    ]
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
