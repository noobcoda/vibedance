import React, { Component } from "react";
import { Grid, Button, Typography } from "@material-ui/core";
import CreateRoomPage from "./CreateRoomPage";
import Player from "./Main";
import YoutubePlayer from "./YoutubeVid";

//just before this step, we were in createroompage.js. And we sent all the inputs to the create-api,
//which puts all the data into a database as it's a serializer. now, we have to take data from the database to get the values of guest can pause, who's the host etc.
//this is by sending a request to our backend, by making a new serializer in views.py to get the data


export default class Room extends Component {
  constructor(props) {
        super(props);
        this.state = {
            votesToSkip: 2,
            guestCanPause: false,
            isHost: false,
            hostName: "",
            listOfUsers: [],
            showSettings: false,
            spotifyAuthenticated: false,
            startPressed: false,
            song: {},
            video: {},

        };
      this.roomCode = this.props.match.params.roomCode;
      //if you look at home.js we have :roomCode, the : means it's some sort of parameter
      //here we match "roomCode" variable to the placeholder in :roomCode in the url
      
      this.leaveButtonPressed = this.leaveButtonPressed.bind(this)
      this.updateShowSettings = this.updateShowSettings.bind(this)
      this.renderSettingsPage = this.renderSettingsPage.bind(this)
      this.getRoomDetails = this.getRoomDetails.bind(this)
      this.getUsersInRoom = this.getUsersInRoom.bind(this)
      this.authenticateSpotify = this.authenticateSpotify.bind(this)
      this.renderNormalPage = this.renderNormalPage.bind(this)
      this.renderMainPage = this.renderMainPage.bind(this)
      this.startButtonPressed = this.startButtonPressed.bind(this)
      this.getCurrentSong = this.getCurrentSong.bind(this)
      //now we call the getRoomDetails function
      this.getRoomDetails()
      this.getUsersInRoom()
    }

  //as we're using spotify but web sockets are not allowed we use pooling method
  //component did mount is used because it's a life cycle method. we use this to set intervals
  //(Every second, calls a function)
  //component did mount runs every time a component is loaded

  componentDidMount() {
    this.interval = setInterval(this.getCurrentSong,1000)
    //measured in ms
  }

  //because of interval, we must stop this interval when component unmounts
  componentWillUnmount() {
    clearInterval(this.interval);
  }

  getCurrentSong() {
    fetch('/spotify/current-song')
    .then((response)=>{
        if (!response.ok) {
        return {};
        } else {
        return response.json();
        }
    })
    .then((data)=>{
      if (data.updated) {
        console.log("Hi")
        const requestOptions = {
          method: "POST",
          headers: {"Content-Type": "application/json"},
          body: JSON.stringify({
            artist: data.artist,
            title: data.title,
          }),
        };
        console.log(data.artist,data.title)
        fetch("/youtube/get-dance",requestOptions)
        .then((response) => response.json())
        .then((data)=>{
            this.setState({video:data});
        })
      };
      this.setState({song: data});
    })
  }

  authenticateSpotify() {
    fetch("/spotify/is-authenticated")
      .then((response) => response.json())
      .then((data) => {
        this.setState({ spotifyAuthenticated: data.status });
        console.log(data.status);
        if (!data.status) {
          fetch("/spotify/get-auth-url")
            .then((response) => response.json())
            .then((data) => {
              window.location.replace(data.url);
            });
        }
      });
  }

  getRoomDetails() {
    return fetch("/api/get-room"+"?code="+this.roomCode)
    .then((response) => {
      if (!response.ok) {
        this.props.leaveRoomCallback();
        this.props.history.push("/");
      }
      return response.json();
    })
    .then((data) => {
      this.setState({
        votesToSkip: data.votes_to_skip,
        guestCanPause: data.guest_can_pause,
        isHost: data.is_host,
        hostName: data.host_name,
      });
    });
  }

  getUsersInRoom() {
      fetch('/api/get-users-in-room' + '?code='+this.roomCode)
      .then((response) => response.json())
      .then((data) => {
        this.setState({
          listOfUsers: data.userList
        });
        if (this.state.isHost) {
          this.authenticateSpotify() //we only authenticate after this .then
        }
      })
  }

  //if _ with response, means we don't care what the response is
  leaveButtonPressed() {
      const requestOptions = {
          method: "POST",
          headers: {"Content-Type": "application/json"},
      };
      fetch('/api/leave-room',requestOptions)
      .then((_response) => {
          this.props.leaveRoomCallback();
          this.props.history.push("/");
      })
  }

  updateShowSettings(value) {
    this.setState({
      showSettings: value,
    });
  }

  startButtonPressed(value) {
    this.setState({
      startPressed: value,
    });
  }

  //render this seperately as only the host can see this
  renderSettingsButton() {
    return (
      <Grid item xs={12} align="center">
        <Button variant="contained" color="primary" onClick = {()=>this.updateShowSettings(true)}>
        Settings
        </Button>
      </Grid>
    )
  }

  renderStartButton() {
    return (
      <Grid item xs={12} align="right">
        <Button variant="contained" color="primary" onClick={()=>this.startButtonPressed(true)}>
          Start!
        </Button>
      </Grid>
    )
  }
    
  //callback called whenever room updates. This is PASSED. Only used when required
  //the callback is getRoomDetails as this is the function that changes the state
  //after getting details about the room
  renderSettingsPage() {
    return(
      <Grid container spacing={1}>
        <Grid item xs={12} align="center">
          <CreateRoomPage 
          update={true} 
          votesToSkip={this.state.votesToSkip} 
          guestCanPause={this.state.guestCanPause}
          roomCode={this.roomCode}
          updateCallback={this.getRoomDetails}
          />
        </Grid>
        <Grid item xs={12} align="center">
          <Button variant="contained" color="secondary" onClick={() => this.updateShowSettings(false)}>
            Close
          </Button>
        </Grid>
    </Grid>
    )
  }

  renderMainPage() {

    return(
      <Grid container spacing={1}>
        <Player {...this.state.song}/>
        <YoutubePlayer {...this.state.video}/>
      </Grid>
    )
  }

  renderNormalPage() {
    return (
      <Grid container spacing={1}>
        <Grid item xs={12} align="center">
          <Typography variant="h6" component="h6">
            Host Name: {this.state.hostName.toString()}
          </Typography>
        </Grid>
        <Grid item xs={12} align="center">
          <Typography variant="h6" component="h6">
            People In Room: {this.state.listOfUsers.toString()}
          </Typography>
        </Grid>
        {this.state.isHost ? this.renderStartButton() : null}
      </Grid>
    )
  }

  render() {
    if (this.state.showSettings) {
      return this.renderSettingsPage();
    }
    return (
      <Grid container spacing={1}>
        <Grid item xs={12} align="center">
          <Typography variant="h4" component="h4">
            Code: {this.roomCode}
          </Typography>
        </Grid>
        {this.state.startPressed ? this.renderMainPage() : this.renderNormalPage()}
        {this.state.isHost ? this.renderSettingsButton() : null}
        <Grid item xs={12} align="center">
          <Button
            variant="contained"
            color="secondary"
            onClick={this.leaveButtonPressed}
          >
            Leave Room
          </Button>
        </Grid>
      </Grid>
    );
  }
}