import React, { Component } from "react";
import { render } from "react-dom";
import First from './First';
import CreateRoomPage from "./CreateRoomPage";

//react has a bunch of components, and each component can render other components
//entry point to application is first component, which we called App.
export default class App extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (<div className="center"> 
            <First />
            </div>)
    }
}
//look at css file - we defined center

//tutorial 3
//put into id container in index.html
const appDiv = document.getElementById("app")
render(<App />, appDiv);
//now put this into our index.js