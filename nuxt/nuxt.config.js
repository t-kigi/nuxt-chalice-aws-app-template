import colors from 'vuetify/es5/util/colors';

const environment = process.env.NODE_ENV || 'local';
const envSet = require(`./constants/env.${environment}.js`);

export default {
  // Disable server-side rendering: https://go.nuxtjs.dev/ssr-mode
  ssr: false,

  // environment variable as $config from Nuxt v2.13.0
  publicRuntimeConfig: envSet,

  // Target: https://go.nuxtjs.dev/config-target
  target: 'static',

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    titleTemplate: '%s - nuxt',
    title: 'nuxt',
    htmlAttrs: {
      lang: 'en',
    },
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' },
    ],
    link: [{ rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }],
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [{ src: '~/plugins/cognito.ts', ssr: false }],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/typescript
    '@nuxt/typescript-build',
    // https://go.nuxtjs.dev/vuetify
    '@nuxtjs/vuetify',
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    // https://go.nuxtjs.dev/axios
    '@nuxtjs/axios',
  ],

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  axios: {},

  // Vuetify module configuration: https://go.nuxtjs.dev/config-vuetify
  vuetify: {
    customVariables: ['~/assets/variables.scss'],
    theme: {
      dark: false,
      themes: {
        dark: {
          primary: colors.blue.darken2,
          accent: colors.grey.darken3,
          secondary: colors.amber.darken3,
          info: colors.teal.lighten1,
          warning: colors.amber.base,
          error: colors.deepOrange.accent4,
          success: colors.green.accent3,
        },
        light: {
          primary: colors.blue.darken2,
          accent: colors.grey.darken3,
          secondary: colors.amber.darken3,
          info: colors.teal.lighten1,
          warning: colors.amber.base,
          error: colors.deepOrange.accent4,
          success: colors.green.accent3,
        },
      },
    },
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  build: {},
  router: {
    middleware: ['auth'],
    extendRoutes(routes, resolve) {
      const aliases = [];
      routes.forEach((r) => {
        if (r.chunkName.endsWith('index')) {
          // alias の追加
          const aliasPath = r.path.endsWith('/') ? r.path : `${r.path}/`;
          // index.vue の場合は特別の処理を実施
          if (r.path.endsWith('/')) {
            // root オブジェクトのみ / になる
            r.path += 'index.html';
          } else {
            // それ以外の index.vue は 単純ページに置き換えられるため
            // ディレクトリ以下に index.html を配置するようにする
            r.path += '/index.html';
          }
          aliases.push({
            path: r.path,
            alias: aliasPath,
            component: r.component,
          });
        } else {
          // それ以外はファイル名 + .html の形式になるため
          // パス名を .html 付きに修正
          r.path += '.html';
        }
      });
      // "/" に対する alias の追加
      aliases.forEach((r) => {
        routes.push(r);
      });
    },
  },
  generate: {
    dir: environment === 'production' ? 'dist' : `dist-${environment}`,
    subFolders: false,
  },
  hooks: {
    generate: {
      async page(p) {
        if (p.path.endsWith('.html.html')) {
          p.path = p.path.substr(0, p.path.length - 5);
        }
      },
    },
  },
};
