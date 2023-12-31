This project was bootstrapped with [Create React App](https://github.com/facebook/create-react-app).
# Minecraft Server Controller
This is a simple controller using the AWS cli through Flask, with a (very) simple UI built in react. 
I take very little credit for the code written, and instead offer my grattitude to those who's code was absorbed by gpt-4. 

## Usage
First, set the global ip address for the Flask server in `./src/App.tsx`, then set an environment variable with your AWS instance ID named `INSTANCE_ID`. Setup the AWS cli client on your machine, then run the servers. 
 
run `npm start` to get the UI going
and `python3 ./server-contr*` to get the Flask backend going. 

It should be reachable wherever the npm launcher says it is. 

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

### `npm test`

Launches the test runner in the interactive watch mode.\
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run build`

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

See the section about [deployment](https://facebook.github.io/create-react-app/docs/deployment) for more information.
