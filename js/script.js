        console.log("PAGE LOADED")
        
        // Width and height of the SVG
        const width = 1280;
        const height = 720;

        // Create the SVG
        const svg = d3.select("body")
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        const initialLatitude = 33.5427;
        const initialLongitude = -117.7854;

        const projection = d3.geoTransverseMercator()
        .scale(15000)
        .rotate([initialLongitude, -initialLatitude]);

        // Define the path generator
        const path = d3.geoPath().projection(projection);

        function updateMap() {
            svg.selectAll("path").attr("d", path);
            svg.selectAll(".point")
                .attr("cx", d => projection(d.geometry.coordinates)[0])
                .attr("cy", d => projection(d.geometry.coordinates)[1]);
        }

        function updateAudioVolumes(scrollPercentage) {
            const audio1 = document.getElementById("audio-1");
            const audio2 = document.getElementById("audio-2");

            audio1.volume = 1 - scrollPercentage;
            audio2.volume = scrollPercentage;
        }

        function fadeInAudio(audioElement, duration) {
            if (audioElement.paused) {
                audioElement.play();
            }
            const startVolume = audioElement.volume;
            const startTime = Date.now();

            function increaseVolume() {
                const elapsed = Date.now() - startTime;
                if (elapsed < duration) {
                audioElement.volume = startVolume + (1 - startVolume) * (elapsed / duration);
                requestAnimationFrame(increaseVolume);
                } else {
                audioElement.volume = 1;
                }
            }

            increaseVolume();
            }

        function fadeOutAudio(audioElement, duration) {
            const startVolume = audioElement.volume;
            const startTime = Date.now();

            function decreaseVolume() {
                const elapsed = Date.now() - startTime;
                if (elapsed < duration) {
                audioElement.volume = startVolume * (1 - elapsed / duration);
                requestAnimationFrame(decreaseVolume);
                } else {
                audioElement.volume = 0;
                audioElement.pause();
                }
            }

            decreaseVolume();
            }

        function clipToBoundingBox(feature, boundingBox) {
            const clipped = turf.bboxClip(feature, boundingBox);
            if (clipped.geometry.type === 'GeometryCollection' && clipped.geometry.geometries.length === 0) {
                return null;
            }
            return clipped;
        }

        function updateProjectionCenter(center) {
            const screenCenter = [width, height];
            const centerInProjection = projection(center);
            const translate = projection.translate();
            const newTranslate = [
                translate[0] - (centerInProjection[0] - screenCenter[0]),
                translate[1] - (centerInProjection[1] - screenCenter[1]),
            ];
            projection.translate(newTranslate);
        }

        // Load the GeoJSON data
        Promise.all([
            d3.json("data/USMX_finalStationPoint.json"),
            d3.json("data/USMX_finalStationLine_DISSOLVE.json"),
            d3.json("data/ne_50m_land.json"),
            d3.json("data/USMX_40_buffers.json"),
            d3.json("data/ne_110m_graticules_10.json")
        ]).then(([points, lines, coastline, buffers, graticule]) => {

            // Calculate the bounding box of the line features
            const linesBoundingBox = turf.bbox(lines);

            // Expand the bounding box in degrees in each direction
            const expandedBoundingBox = [
                linesBoundingBox[0] - 7, // min longitude
                linesBoundingBox[1] - 7, // min latitude
                linesBoundingBox[2] + 7, // max longitude
                linesBoundingBox[3] + 7, // max latitude
            ];

            // Clip the coastline features
            coastline.features = coastline.features
                .map(feature => clipToBoundingBox(feature, expandedBoundingBox))
                .filter(feature => feature !== null);

            // Clip the graticule features
            graticule.features = graticule.features
                .map(feature => clipToBoundingBox(feature, expandedBoundingBox))
                .filter(feature => feature !== null);

            // Create the linear gradient
            const linearGradient = svg.append("defs")
                .append("linearGradient")
                .attr("id", "coast-gradient")
                .attr("x1", "0%")
                .attr("y1", "0%")
                .attr("x2", "0%")
                .attr("y2", "100%");

            linearGradient.append("stop")
                .attr("offset", "0%")
                .attr("stop-color", "rgb(0, 0, 255)") // Modify colors as needed
                .attr("stop-opacity", 1);

            linearGradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", "rgb(255, 255, 255)") // Modify colors as needed
                .attr("stop-opacity", 1);

            // Draw the coastline
            svg.append("g")
                .selectAll("path")
                .data(coastline.features)
                .enter()
                .append("path")
                .attr("d", path)
                .attr("class", "coast");

            // Draw the coastline gradient
            // svg.append("g")
            //     .selectAll("path")
            //     .data(coastline.features)
            //     .enter()
            //     .append("path")
            //     .attr("d", path)
            //     .attr("fill", "url(#coast-gradient)");

            // Draw the graticule
            svg.append("g")
                .selectAll("path")
                .data(graticule.features)
                .enter()
                .append("path")
                .attr("d", path)
                .attr("class", "graticule");

            // Load the buffer polygons and their associated audio files
            const bufferAudioElements = {};

            buffers.features.forEach(buffer => {
                const id = buffer.properties.id;
                const audioElement = document.createElement("audio");
                audioElement.loop = true;
                const sourceElement = document.createElement("source");
                sourceElement.src = `audio/${id}.mp3`;
                sourceElement.type = "audio/mpeg";
                audioElement.appendChild(sourceElement);
                bufferAudioElements[id] = audioElement;
                document.body.appendChild(audioElement);
            });

            // Create the radial gradient
            const radialGradient = svg.append("defs")
                .append("radialGradient")
                .attr("id", "buffer-gradient")
                .attr("cx", "50%")
                .attr("cy", "50%")
                .attr("r", "50%")
                .attr("fx", "50%")
                .attr("fy", "50%");

            radialGradient.append("stop")
                .attr("offset", "0%")
                .attr("stop-color", "rgba(255, 0, 220, .6)")
                .attr("stop-opacity", 1);

            radialGradient.append("stop")
            .attr("offset", "50%")
            .attr("stop-color", "rgb(255, 0, 255, .4)")
            .attr("stop-opacity", 1);

            radialGradient.append("stop")
                .attr("offset", "100%")
                .attr("stop-color", "rgb(255, 0, 255, 0)")
                .attr("stop-opacity", 1);

            // Draw the buffers
            svg.append("g")
                .selectAll("path")
                .data(buffers.features)
                .enter()
                .append("path")
                .attr("d", path)
                .attr('fill', 'url(#buffer-gradient)')
                .attr("class", "buffer");
            
            // Draw the radio lines
            const lineGroup = svg.append("g")
                .selectAll("path")
                .data(lines.features)
                .enter()
                .append("path")
                .attr("d", path)
                .attr("class", "line");

            // Hide the lines initially
            lineGroup.each(function(d, i) {
                const path = d3.select(this);
                const length = path.node().getTotalLength();

                path.attr("stroke-dasharray", length + " " + length)
                    .attr("stroke-dashoffset", length);
            });

            // Draw the points
            svg.append("g")
                .selectAll("circle")
                .data(points.features)
                .enter()
                .append("circle")
                .attr("class", "point")
                .attr("cx", d => projection(d.geometry.coordinates)[0])
                .attr("cy", d => projection(d.geometry.coordinates)[1])
                .attr("r", 4);
                
            // Create scrolling audio element
            const scrollAudioElement = document.createElement("audio");
            scrollAudioElement.loop = true;
            const scrollSourceElement = document.createElement("source");
            scrollSourceElement.src = "audio/pinkNoise.mp3";
            scrollSourceElement.type = "audio/mpeg";
            scrollAudioElement.appendChild(scrollSourceElement);
            document.body.appendChild(scrollAudioElement);

            // Create gap audio element
            const gapAudioElement = document.createElement("audio");
            gapAudioElement.loop = true;
            const gapSourceElement = document.createElement("source");
            gapSourceElement.src = "audio/gap.mp3";
            gapSourceElement.type = "audio/mpeg";
            gapAudioElement.appendChild(gapSourceElement);
            document.body.appendChild(gapAudioElement);

            let gapAudioFadeInterval;
            function fadeInGapAudio() {
                if (gapAudioFadeInterval) {
                    clearInterval(gapAudioFadeInterval);
                }
                gapAudioFadeInterval = setInterval(() => {
                    gapAudioElement.volume = Math.min(gapAudioElement.volume + 0.05, 1);
                    if (gapAudioElement.volume === 1) {
                        clearInterval(gapAudioFadeInterval);
                    }
                }, 20);
                
            }

            function fadeOutGapAudio() {
                if (gapAudioFadeInterval) {
                    clearInterval(gapAudioFadeInterval);
                }
                gapAudioFadeInterval = setInterval(() => {
                    gapAudioElement.volume = Math.max(gapAudioElement.volume - 0.05, 0);
                    if (gapAudioElement.volume === 0) {
                        clearInterval(gapAudioFadeInterval);
                        gapAudioElement.pause();
                    }
                }, 20);
            }


            // Debounce scrolling audio
            function debounce(func, wait) {
            let timeout;
            return function(...args) {
                const context = this;
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(context, args), wait);
            };
        }

            // Define the total scroll height based on the number of line segments
            const totalLineLength = lines.features.reduce((total, feature) => {
                return total + turf.length(feature);
            }, 0);


            // Set the scroll height based on the total line length
            const scrollHeight = totalLineLength * 25;
            document.querySelector('.scroll-container').style.height = `${scrollHeight}px`;

            // Store the last scroll position and timestamp
            let lastScrollPosition = 0;
            let lastScrollTimestamp = 0;

            // Reproject the map when the user scrolls
            function updateMapOnScroll() {
                const currentScrollPercentage = window.pageYOffset / (document.body.scrollHeight - window.innerHeight);

                // Fade in the scroll audio when the user starts scrolling
                fadeInAudio(scrollAudioElement, 20); // 20ms fade-in duration

                // Reveal more of the line as the user scrolls
                let visibleLinePoints = [];
                lineGroup.each(function(d, i) {
                    const path = d3.select(this);
                    const length = path.node().getTotalLength();

                    const currentOffset = length * currentScrollPercentage;
                    path.attr("stroke-dasharray", length + " " + length)
                        .attr("stroke-dashoffset", length - currentOffset);

                    const visibleLineLength = length - currentOffset;
                    if (visibleLineLength > 0) {
                        const startPoint = path.node().getPointAtLength(0);
                        const endPoint = path.node().getPointAtLength(currentOffset);
                        visibleLinePoints.push([startPoint.x, startPoint.y], [endPoint.x, endPoint.y]);
                    }
                });

                // Calculate the bounding box and center of the visible line segment
                if (visibleLinePoints.length > 0) {
                    const visibleLine = turf.lineString(visibleLinePoints);

                // Find the endpoint of the visible line segment
                const endpoint = visibleLinePoints[visibleLinePoints.length - 1];

                // Convert the endpoint coordinates to latitude and longitude
                const endpointLatLng = projection.invert(endpoint);
                const endpointLatitude = endpointLatLng[1];
                const endpointLongitude = endpointLatLng[0];

                // Calculate the initial scale based on the visible line points
                const initialScale = 11000;

                // Find the most northerly and most southerly latitude points in the points.features array
                const latitudes = points.features.map(point => point.geometry.coordinates[1]);
                const mostNortherlyLatitude = Math.max(...latitudes);
                const mostSoutherlyLatitude = Math.min(...latitudes);

                // Interpolate the latitude based on the scroll percentage
                const interpolatedLatitude = (mostNortherlyLatitude + 2) - (mostNortherlyLatitude - (mostSoutherlyLatitude - 3)) * (currentScrollPercentage*.5);

                // Update the map projection to center on the endpoint of the visible line segment
                projection
                    .rotate([-endpointLongitude, -interpolatedLatitude])
                    .translate([(width * 0.1) / Math.cos((90 - endpointLatitude) * Math.PI / 180), height / 2])
                    .scale(initialScale); // Set the scale to the initialScale constant

                // Update the h2 element with the latitude and longitude
                const coordinatesDisplay = document.getElementById("latlong-display");
                coordinatesDisplay.textContent = `${endpointLatitude.toFixed(4)}, ${endpointLongitude.toFixed(4)}`;

                // Redraw the map with the updated projection
                updateMap();

                }

                // Determine when the animated line intersects a buffer polygon
                const endpoint = turf.point(visibleLinePoints[visibleLinePoints.length - 1]);
                // const endpointLatLng = endpoint.geometry.coordinates
                let isInBuffer = false;
                //TODO: THIS ISN'T CORRECT
                console.log(isInBuffer)


                buffers.features.forEach(buffer => {
                    const id = buffer.properties.id;
                    const audioElement = bufferAudioElements[id];
                    // console.log(endpointLatLng)

                    if (turf.booleanPointInPolygon(endpoint, buffer)) {
                        const bufferCenter = turf.center(buffer);
                        const distanceToCenter = turf.distance(endpoint, bufferCenter);
                        const maxDistance = turf.length(turf.lineString(buffer.geometry.coordinates[0])) / 2;
                        const volume = 1 - Math.log(distanceToCenter / maxDistance + 1) / Math.log(2);

                        isInBuffer = true;

                        audioElement.volume = volume;
                        if (audioElement.paused) {
                            audioElement.play();
                        }
                    } else {
                        audioElement.pause();
                        audioElement.currentTime = 0;
                    }
                });

                if (!isInBuffer) {
                    fadeInGapAudio();
                    if (gapAudioElement.paused) {
                        gapAudioElement.play();
                    }
                } else {
                    fadeOutGapAudio();
                }

                
            scrollAudioElement.playbackRate = 1;

        }

    // Attach the function to the scroll event
    window.addEventListener('scroll', updateMapOnScroll, {
        passive: true
    });

    // Add an event listener to pause the scroll audio when the user stops scrolling
    window.addEventListener('scroll', debounce(() => {
        fadeOutAudio(scrollAudioElement, 20); // 20ms fade-out duration
        }, 100));

    // Call updateMapOnScroll with initial scroll percentage of 1%
    updateMapOnScroll(0.01);
});

// Add this function to handle the button click
function START() {
    const startButton = document.getElementById("startButton");
    startButton.style.display = "none"; // Hide the start button

    const scrollAudioElement = document.getElementById("scrollAudio");
    scrollAudioElement.play(); // Play the scroll audio element
}

// Add an event listener for the button click
document.getElementById("startButton").addEventListener("click", START);