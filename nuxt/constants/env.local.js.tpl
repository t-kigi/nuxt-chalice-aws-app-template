module.exports = {
  baseUrl: 'http://localhost:3000',
  apiBaseUrl: 'http://localhost:8000',
  cognito: {
    region: 'ap-northeast-1',
    userPoolId: 'ap-northeast-1_**********',
    clientId: '***************************',
  },
  axios: {
    baseUrl: 'http://localhost:8000',
    credentials: true,
  },
};
