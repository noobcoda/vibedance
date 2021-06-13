import React, { Component } from "react";
import {
  Grid,
  Typography,
  Card,
  IconButton,
  Button,
} from "@material-ui/core";
import PlayArrowIcon from "@material-ui/icons/PlayArrow";
import PauseIcon from "@material-ui/icons/Pause";
import SkipNextIcon from "@material-ui/icons/SkipNext";
import YouTubeVid from "./YoutubeVid";

export default class Player extends Component {
    constructor(props) {
        super(props);

        this.pauseSong = this.pauseSong.bind(this);
        this.playSong = this.playSong.bind(this);
        this.skipSong = this.skipSong.bind(this);
    
    }

    pauseSong() {
        const requestOptions = {
            method: "PUT",
            headers: {"Content Type": "application/json"},
        }
        fetch("/spotify/pause-song",requestOptions);
    }

    playSong() {
        const requestOptions = {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
        };
        fetch("/spotify/play-song", requestOptions);
      }

    skipSong() {
        const requestOptions = {
            method: "POST",
            headers: {"Content Type": "application/json"},
        }
        fetch("/spotify/skip-song",requestOptions);
    }
    
    //below we use div, as we don't want the parent to be the grid. We want the icon buttons to be grouped together
    //this basically renders a music player
    
    //for skip song, we use an arrow function so we don't need to bind the function at the top
    render() {
        return (
            <Card style={{height:"60%"}}>
                <Grid container alignItems="center">
                    <Grid item align="center" xs={4}>
                        <img src={this.props.image_url} height="80%" width="80%"/>
                    </Grid>
                    <Grid item align="center" xs={8}>
                        <Typography component="h5" variant="h5">
                            {this.props.title}
                        </Typography>
                    </Grid>
                    <Grid item align="center" xs={8}>
                        <Typography color="textSecondary" variant="subtitle1">
                            {this.props.artist}
                        </Typography>
                        <div>
                            <IconButton
                                onClick={() => {this.props.is_playing ? this.pauseSong() : this.playSong()}}
                            >
                                {this.props.is_playing ? <PauseIcon /> : <PlayArrowIcon />}
                            </IconButton>
                            <IconButton onClick={this.skipSong}>
                                {this.props.votes} / {this.props.votes_to_skip}
                                <SkipNextIcon />
                            </IconButton>
                        </div>     
                    </Grid>
                </Grid>
            </Card>
        )
    }
}