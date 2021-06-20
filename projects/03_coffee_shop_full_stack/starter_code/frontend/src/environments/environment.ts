/* @TODO replace with your variables
 * ensure all variables on this page match your project
 */

export const environment = {
  production: false,
  apiServerUrl: 'http://127.0.0.1:5000', // the running FLASK api server url
  auth0: {
    url: 'fsnd-saylesc.us', // the auth0 domain prefix
    audience: 'fsnd-java-mocha', // the audience set for the auth0 app
    clientId: 'ubE0GpRBZpycpU8p8gUQBGM9VjIb8Nc8', // the client id generated for the auth0 app
    callbackURL: 'http://127.0.0.1:4200', // the base url of the running ionic application. 
  }
};
