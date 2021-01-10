/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'lili-coffee-shop.us', // the auth0 domain prefix
    audience: 'coffee-shop', // the audience set for the auth0 app
    clientId: 'BFRNLAUiYUT0B0lMLW6bLG7A93U8nVkc', // the client id generated for the auth0 app
    // callbackURL: 'https://127.0.0.1:5000/login-results' // the base url of the running ionic application. 
    callbackURL: 'http://127.0.0.1:8100'
  }
};

