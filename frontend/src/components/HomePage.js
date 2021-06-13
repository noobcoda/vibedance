import React, { Component } from 'react';
import { Grid, Button, ButtonGroup, Typography, TextField } from "@material-ui/core";
import { BrowserRouter as Router, Switch, Route, Link, Redirect } from "react-router-dom"

export default class HomePage extends Component {
    constructor(props) {
        super(props);

        this.state={
            roomCode: "",
            error: "",
            name: "",
        }

        this.handleTextFieldChange = this.handleTextFieldChange.bind(this)
        this.handleNameChange = this.handleNameChange.bind(this)
        this.roomButtonPressed = this.roomButtonPressed.bind(this)
        this.createUser = this.createUser.bind(this)
    }
    handleTextFieldChange(t) {
        this.setState({
            roomCode: t.target.value, 
        })
    }

    handleNameChange(e) {
        this.setState({
            name: e.target.value,
        })
    }

    createUser() {
        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              username: this.state.name,
              code: this.state.roomCode,
            }),
          };
          fetch('/api/create-user',requestOptions)
          .then((response) => {
              if (response.ok) {
                this.props.history.push(`/room/${this.state.roomCode}`);
              }
          })
    }

    //props is the data passed by the router. the ... spreads out the props; prop1 = this, prop2=that etc.
    //we make our own prop that is a call back function
    roomButtonPressed() {
        //will go to backend, check if the room code is valid
        //if valid, we add the user to the database

        const requestOptions = {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              code: this.state.roomCode,
            }),
          };
          fetch("/api/join-room", requestOptions)
            .then((response) => {
              if (response.ok) {
                this.createUser()
              } else {
                this.setState({ error: "Room not found." });
              }
            })
            .catch((error) => {
              console.log(error);
            });
    }

    render() {
        return (
            <Grid container spacing={1}>
                <Grid item xs={12} align="center">
                    <Typography variant="h1" component="h1">
                        VIBE DANCEU!
                    </Typography>
                </Grid>
                <Grid container spacing={3}>
                    <Grid item xs>
                        <TextField
                            label="Name"
                            placeholder="Jenny"
                            variant="outlined"
                            value={this.state.name}
                            onChange = {this.handleNameChange}
                        />
                    </Grid>
                    <Grid item xs>
                        <TextField 
                            error={this.state.error}
                            label="Code"
                            placeholder="ABCDEFGH"
                            value={this.state.roomCode}
                            helperText={this.state.error}
                            variant="outlined"
                            onChange = {this.handleTextFieldChange}
                        />
                    </Grid>
                    <Grid item xs>
                        <Button variant="contained" color="primary" align="center" onClick={this.roomButtonPressed}>
                            JOIN
                        </Button>
                    </Grid>
                </Grid>
                <Grid item xs={12} align="center">
                    <Typography variant="h6" component="h6" align="center">
                        ...or...
                    </Typography>
                    <Button variant="contained" color="primary" align="center" to = "/create" component={Link}>
                        CREATE A ROOM
                    </Button>
                </Grid>
            </Grid>
        );
    }
}