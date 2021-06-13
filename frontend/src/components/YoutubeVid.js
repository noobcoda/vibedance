import React, { Component } from "react";
import ReactPlayer from 'react-player'

export default class YoutubePlayer extends Component {
    constructor(props) {
        super(props);
    }
    render() {
        return (
            <ReactPlayer url={this.props.url} controls={true}/>
        )
    }
}