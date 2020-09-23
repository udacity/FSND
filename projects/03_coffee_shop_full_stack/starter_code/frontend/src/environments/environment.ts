/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'dev-kcrtg2gg.us', // the auth0 domain prefix
    audience: "coffee-shop-endpoint", // the audience set for the auth0 app
    clientId: 'T0WV45x4q8mVNWJmrBSLG6IPQEWTLyOz', // the client id generated for the auth0 app
    callbackURL: 'http://localhost:4200', // the base url of the running ionic application.
  }
};
