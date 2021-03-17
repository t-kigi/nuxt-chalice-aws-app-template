// SPA モードの場合、ミドルウェアはクライアントサイドで
// 最初のリクエスト時と他のルートへ移動したときにそれぞれ呼び出される。
export default async ({ app, route, store, redirect }) => {
  if (route.name === 'logout') {
    // ログアウトページでは何もしない
    return;
  }

  // 必要に応じてトークンを更新する
  if (store.getters['auth/isExpired']) {
    await store.dispatch('auth/update', {
      cognitoAuth: app.$cognito,
      axios: app.$axios,
    });
  }
  const isLoggedIn = store.getters['auth/isLoggedIn']();
  const isMemberPage = (r) => {
    // /m/index.html は alias なので、ここのみ独自に判定
    return r === 'm' || r.startsWith('m-');
  };
  if (!isLoggedIn && isMemberPage(route.name)) {
    // ログインでないのにメンバーページを開いている場合
    redirect('/');
  } else if (isLoggedIn && route.name === 'index') {
    // トップページかつログインしている場合は自動的に移動
    redirect('/m/index.html');
  }
};
