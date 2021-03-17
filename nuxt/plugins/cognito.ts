// Amazon Cognito を使った認証機構
import { Context, NuxtAppOptions } from '@nuxt/types';
import {
  CognitoUserPool,
  CognitoUser,
  AuthenticationDetails,
  IAuthenticationCallback,
  CognitoUserSession,
} from 'amazon-cognito-identity-js';

interface CognitoAuthConfig {
  userPoolId: string;
  clientId: string;
}

interface ApiHeader {
  Authorization: string;
  CognitoAccessToken: string;
}

export class CognitoAuth {
  app: NuxtAppOptions;
  userPool: CognitoUserPool;

  constructor(app: NuxtAppOptions, cognito: CognitoAuthConfig) {
    this.app = app;
    this.userPool = new CognitoUserPool({
      UserPoolId: cognito.userPoolId,
      ClientId: cognito.clientId,
    });
  }

  /**
   * Cognito へのログインを実施する
   */
  login(username: string, password: string, newPassword?: string) {
    const cognitoUser = new CognitoUser({
      Username: username,
      Pool: this.userPool,
    });
    const authenticationDetails = new AuthenticationDetails({
      Username: username,
      Password: password,
    });
    return new Promise((resolve, reject) => {
      const authCallback: IAuthenticationCallback = {
        onSuccess: (session) => {
          resolve({
            type: 'success',
            session,
          });
        },
        onFailure: (err) => {
          reject(err);
        },
        newPasswordRequired: (userAttributes, requiredAttributes) => {
          if (newPassword) {
            cognitoUser.completeNewPasswordChallenge(
              newPassword,
              {},
              authCallback
            );
          } else {
            resolve({
              type: 'newPasswordRequired',
              userAttributes,
              requiredAttributes,
            });
          }
        },
      };
      cognitoUser.authenticateUser(authenticationDetails, authCallback);
    });
  }

  /**
   * ログアウト
   */
  logout(): void {
    this.userPool.getCurrentUser()?.signOut();
  }

  /**
   * 最新のセッションを取得して返す
   */
  getSession(): Promise<CognitoUserSession | null> {
    const cognitoUser: CognitoUser | null = this.userPool.getCurrentUser();
    return new Promise((resolve, reject) => {
      if (cognitoUser === null) {
        resolve(null);
        return;
      }
      // 最新のセッションを取得する
      cognitoUser.getSession(
        (err: Error, session: CognitoUserSession | null) => {
          if (err || !session || !session.isValid()) {
            resolve(null);
          } else {
            resolve(session);
          }
        }
      );
    });
  }

  headers(): Promise<ApiHeader> {
    return new Promise(async (resolve, reject) => {
      const store = this.app.store;
      if (!store) return reject('store not found');
      if (store.getters['auth/isExpired']()) {
        // 更新をかける
        await store.dispatch('auth/update', {
          cognitoAuth: this,
          axios: this.app.$axios,
        });
      }
      resolve(store.getters['auth/headers']());
    });
  }
}

export default ({ app }: Context, inject: (key: string, ref: any) => void) => {
  inject('cognito', new CognitoAuth(app, app.$config.cognito));
};
