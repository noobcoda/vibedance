import React, { Component } from "react";
import Room from "./Room";
import CreateRoomPage from "./CreateRoomPage";
import HomePage from "./HomePage";
import Main from "./Main";
import YoutubePlayer from "./YoutubeVid";
import { Grid, Button, ButtonGroup, Typography } from "@material-ui/core";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  Redirect,
} from "react-router-dom";


export default class First extends Component {
    constructor(props) {
      super(props);
      this.state = {
        roomCode: null,
      };
      this.clearRoomCode = this.clearRoomCode.bind(this);
    }

    //we want to make sure the user is redirected to correct room depending if they're already in a session or not
    //component did mount means it's the first time that web app has been loaded on user's screen
    // usually component did mount does not come with async, but as we're performing an asynchronous action we need this
    //without async, we need to wait for everything to happen, before doing anything else
    //but calling an endpoint (which we will do) may take a while, slowing down other operations.
    
    //every time we set state, we re-render the browser. So after async, we do render() again
  
    async componentDidMount() {
      fetch("/api/user-in-room")
        .then((response) => response.json())
        .then((data) => {
          this.setState({
            roomCode: data.code,
          });
        });
    }
  
    renderFirstPage() {
      return (
        <Grid container spacing={3}>
          <Grid item xs={12} align="center">
            <Typography variant="h3" compact="h3">
              VIBE DANCEU!
            </Typography>
          </Grid>
          <Grid item xs={12} align="center">
              <Button color="secondary" to="/start" component={Link}>
                PLAY!
              </Button>
          </Grid>
        </Grid>
      );
    }
    
    //we need this method, because even after we leave the room, the room code is still there and then we re-direct back to a deleted room

    clearRoomCode() {
      this.setState({
        roomCode: null,
      });
    }

    //we return a router that directs us to the correct page
    //for the first one, we have an arrow function; if we have a roomcode already (we use the component did mount function), i.e. not null, then we redirect to that page
    //otherwise, we render the home page 
    render() {
      return (
        <Router>
          <Switch>
            <Route
              exact
              path="/"
              render={() => {
                return this.state.roomCode ? (
                  <Redirect to={`/room/${this.state.roomCode}`} />
                ) : (
                  this.renderFirstPage()
                );
              }}
            />
            <Route path="/start" component={HomePage} />
            <Route path="/create" component={CreateRoomPage} />
            <Route path='/main' component={Main}></Route>
            <Route path="/watch" component={YoutubePlayer}></Route>
            <Route
              path="/room/:roomCode"
              render={(props) => {
                return <Room {...props} leaveRoomCallback={this.clearRoomCode} />;
              }}
            />
          </Switch>
        </Router>
      );
    }
  }