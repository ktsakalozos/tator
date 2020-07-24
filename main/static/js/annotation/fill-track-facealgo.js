class FillTrackFace {
  constructor(videoDef, algoCanvas) {
    console.info("Processing = " + JSON.stringify(videoDef));
    this._project = algoCanvas.activeLocalization.project;
    this._mediaId = algoCanvas.activeLocalization.media;
    this._width = videoDef.width;
    this._height = videoDef.height;
    this._data = algoCanvas._data;
    this._dataTypes = algoCanvas._data._dataTypes;
    this._newLocalizations = [];

    // Get the currently selected track.
    this._track = algoCanvas._data._trackDb[algoCanvas.activeLocalization.id];

    // Get localizations that match the selected localization's type
    // #TODO There probably is a better way to do this (and the next step) instead
    //       of just grabbing everything.
    let selectedLocalizations = algoCanvas._data._dataByType
                          .get(algoCanvas.activeLocalization.meta);

    // With a list of localizations now curated, cycle through them and figure out
    // which localizations belong to the selected track
    this._localizations = [];
    for (const idx in selectedLocalizations) {
      let currentLocalization = selectedLocalizations[idx];
      if (algoCanvas._data._trackDb[currentLocalization.id]) {
        const sameTrackId = algoCanvas._data._trackDb[currentLocalization.id].id == this._track.id;
        if (sameTrackId) {
          this._localizations.push(currentLocalization);
        }
      }
    }

    // Sort localizations by frame.
    this._localizations.sort((left, right) => {left.frame - right.frame});
  }

  async init() {
    // Create the face detector
    this._face_model = await blazeface.load();
  }

  async processFrame(frameIdx, pixels, canvas) {
    console.info("Processing frame " + frameIdx);
    // Retrieve the most recent localization in the track before this frame.
    let latest = null;
    for (const localization of this._localizations) {
      if (localization.frame <= frameIdx) {
        if (latest) {
          if (localization.frame > latest.frame) {
            latest = localization;
          }
        }
        else {
          latest = localization;
        }
      }
    }

    // If the track contains no localizations from before this frame, take no action.
    if (latest === null) {
      return null;
    }
    this._localization_attributes = latest.attributes;
    this._version = latest.version;
    this._localizationType = latest.meta;

    // The first frame is used as the template localization, to apply to the other localizations
    // generated by this algortihm.
    if (latest.frame == frameIdx) {
      return null;
    }

    // Find those faces
    const returnTensors = false;
    const flipHorizontal = false;
    const annotateBoxes = true;
    const predictions = await this._face_model.estimateFaces(
      canvas, returnTensors, flipHorizontal, annotateBoxes);

    console.log("predictions for frame: " + frameIdx);
    console.log(predictions);

    // For each of the predictions that have probabilites of at least 90%, create a localization.
    // Each localization will be in the same track
    for (const prediction of predictions) {

      if (prediction.probability[0] > 0.9) {

        // Use the topLeft/bottomRight. Although for some reason, there might be
        // negative numbers here which will cause a problem
        var x = prediction.topLeft[0];
        var y = prediction.topLeft[1];

        if (x < 0){
          x = 0;
        }
        if (y < 0){
          y = 0;
        }

        const width = prediction.bottomRight[0] - x;
        const height = prediction.bottomRight[1] - y;

        var newLocalization = {
          media_id: this._mediaId,
          type: Number(this._localizationType.split("_")[1]),
          x: x / this._width,
          y: y / this._height,
          width: width / this._width,
          height: height / this._height,
          frame: frameIdx,
          version: this._version,
        };

        newLocalization = {...newLocalization, ...this._localization_attributes};

        console.log(newLocalization);

        this._newLocalizations.push(newLocalization);
      }
    }

    // Clean up.
    console.log("done processing frame");

    return null;
  }

  finalize() {
    console.info("Done algorithm");

    if (this._newLocalizations.length == 0) {
      console.info("No localizations created by algorithm.")
      return null;
    }

    // Create new localizations.
    const promise = fetchRetry("/rest/Localizations/" + this._project, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "X-CSRFToken": getCookie("csrftoken"),
        "Accept": "application/json",
        "Content-Type": "application/json"
      },
      body: JSON.stringify(this._newLocalizations),
    })
    .then(response => response.json())
    .then(data => {
      // Append new localizations to track.
      fetchRetry("/rest/State/" + this._track.id, {
        method: "PATCH",
        credentials: "same-origin",
        headers: {
          "X-CSRFToken": getCookie("csrftoken"),
          "Accept": "application/json",
          "Content-Type": "application/json"
        },
        body: JSON.stringify({'localization_ids_add': data.id}),
      })
      .then(async () => {
        // Update data after a second.
        await new Promise(r => setTimeout(r, 1000));
        this._data.updateType(this._dataTypes[this._localizationType]);
        this._data.updateType(this._dataTypes[this._track.meta]);
        delete this._face_model;
      });
    });
    return promise;
  }
}

// Eval won't store the 'Algo' class definition globally
// This is actually helpful, we just need a factory method to
// construct it
function algoFactory(videoDef, algoCanvas) {
  return new FillTrackFace(videoDef, algoCanvas);
}
