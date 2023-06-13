// @ts-check
// Note: type annotations allow type checking and IDEs autocompletion

const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

module.exports = {
  themeConfig: {
    colorMode: {
      defaultMode: 'dark',
      disableSwitch: true,
      respectPrefersColorScheme: false,
    },
  },
};

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'SuperAGI Docs',
  tagline: 'Dev-First  open source framework to build, manage & run autonomous AI agents',
  favicon: 'https://superagi.com/wp-content/uploads/2023/05/Superagi_favicon.png',

  // Set the production url of your site here
  url: 'https://superagi.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/docs/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'TransformerOptimus', // Usually your GitHub org/user name.
  projectName: 'SuperAGI', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internalization, you can use this field to set useful
  // metadata like html lang. For example, if your site is Chinese, you may want
  // to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: '/',
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/TransformerOptimus/SuperAGI/website/',
        },
        blog: {
          showReadingTime: true,
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/TransformerOptimus/SuperAGI/website/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'https://superagi.com/wp-content/uploads/2023/06/Frame-113818.png',
      navbar: {
        title: 'SuperAGI',
        logo: {
          alt: 'My Site Logo',
          src: 'https://superagi.com/wp-content/uploads/2023/06/Frame-113818.png',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Docs',
          },
          {
            href: 'https://github.com/TransformerOptimus/SuperAGI',
            label: 'GitHub Repo',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'More',
            items: [
              {
                label: 'Discussions',
                to: 'https://github.com/TransformerOptimus/SuperAGI/discussions',
              },
              {
                label: 'Releases',
                to: 'https://github.com/TransformerOptimus/SuperAGI/releases',
              },
            ],
          },
          {
            title: 'Community',
            items: [
            
              {
                label: 'Discord',
                href: 'https://discord.gg/dXbRe5BHJC',
              },
              {
                label: 'Twitter',
                href: 'https://twitter.com/_superAGI',
              },
              {
                label: 'Reddit',
                href: 'https://www.reddit.com/r/Super_AGI/',
              },
            ],
          },
          {
            title: 'Important Links',
            items: [
              {
                label: 'SuperAGI.com',
                href: 'https://superagi.com/',
              },
              {
                label: 'GitHub',
                href: 'https://github.com/TransformerOptimus/SuperAGI/',
              },
              {
                label: 'Roadmap',
                href: 'https://github.com/users/TransformerOptimus/projects/1',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} SuperAGI`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
      },
    }),
};

module.exports = config;
