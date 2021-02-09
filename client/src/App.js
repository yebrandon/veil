import React, { Component } from 'react';
import Webcam from 'react-webcam';
import banner from './assets/img/veil.png';
import './App.css';

class App extends Component {
	constructor(props) {
		super(props);
		this.state = { capture: null, labels: null, faces: null };
	}

	// Retrieve face images and classification labels using capture
	analyzeImg(img) {
		const postOptions = {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ b64Str: img })
		};
		const getOptions = {
			method: 'GET',
			headers: { 'Content-Type': 'application/json' }
		};

		fetch('http://localhost:8000/analyze-capture', postOptions)
			.then((response) => response.json())
			.then((labelData) => {
				this.setState({ labels: labelData });
				fetch('http://localhost:8000/get-imgs', getOptions)
					.then((response) => response.json())
					.then((facesData) => {
						this.setState({ faces: facesData });
					});
			});
	}

	// Capture webcam frame and start mask detection
	detectMasks() {
		let capture = this.refs.webcam.getScreenshot();
		this.setState({ capture: capture }, () => {
			console.log(this.state.capture);
			this.analyzeImg(this.state.capture);
		});
	}

	// Display detected faces and classifications
	showResults() {
		if (this.state.faces && this.state.labels) {
			let results = [];

			for (let [key, val] of Object.entries(this.state.labels)) {
				let labelStr = '';
				let confidenceStr =
					'Confidence: ' +
					(val.confidence * 100).toString().substring(0, 6) +
					'%'; // Parse confidence to readable percentage

				if (val.match === 'no_mask_training_set') {
					labelStr = 'No Mask Detected';
				} else {
					labelStr = 'Mask Detected';
				}
				results.push(
					<div className='result'>
						<img
							id='face'
							src={
								'data:image/jpg;base64,' + this.state.faces[key]
							}
						/>
						{labelStr}
						<br />
						{confidenceStr}
					</div>
				);
			}

			return results;
		}
	}

	render() {
		return (
			<div id='container'>
				<img id='banner' src={banner} />
				<Webcam
					id='webcam'
					screenshotFormat={'image/png'}
					ref='webcam'
				/>
				{this.state.capture ? (
					<img id='capture' src={this.state.capture} />
				) : null}
				<button id='capture-btn' onClick={this.detectMasks.bind(this)}>
					Detect Masks
				</button>
				{this.state.labels && this.state.faces
					? this.showResults()
					: null}
			</div>
		);
	}
}

export default App;
