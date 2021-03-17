export const strict = false;

export const state = () => ({
  expired: undefined, // Tokenの有効期間
  accessToken: undefined, // Cognito Idp 用トークン  (CognitoAccessToken Header)
  idToken: undefined, // API Gateway 用認証トークン  (Authorization Header)
});

export const getters = {
  // 内部保持トークンの有効期限切れを返す
  isExpired: (state) => (dt) => {
    if (!state.expired) return false;
    const now = dt || new Date();
    const unixtime = now.getTime() / 1000;
    return state.expired < unixtime;
  },

  // API Access 時に利用する Header 情報を返す
  headers: (state) => () => {
    return {
      Authorization: state.idToken,
      CognitoAccessToken: state.accessToken,
    };
  },

  // ログイン中か否かを返す
  isLoggedIn: (state) => () => {
    return state.accessToken !== undefined && state.idToken !== undefined;
  },
};
export const mutations = {
  /**
   * store のトークンを更新する
   */
  async update(state, session) {
    if (session) {
      state.expired = session.getIdToken().getExpiration();
      state.accessToken = session.getAccessToken().getJwtToken();
      state.idToken = session.getIdToken().getJwtToken();
    } else {
      state.expired = undefined;
      state.accessToken = undefined;
      state.idToken = undefined;
    }
  },
};

const updateSignedCookie = async (axios, session) => {
  await axios.$get('/api/auth/signedcookie', {
    headers: {
      Authorization: session.getIdToken().getJwtToken(),
    },
  });
};

export const actions = {
  updateSignedCookie: async (context, { axios, session }) => {
    await updateSignedCookie(axios, session);
  },
  update: async ({ commit }, { cognitoAuth, axios }) => {
    const session = await cognitoAuth.getSession();
    if (session) {
      await updateSignedCookie(axios, session);
    }
    commit('update', session);
  },
  logout: ({ commit }, cognitoAuth) => {
    cognitoAuth.logout();
    commit('update', null);
  },
};
