const width = 960;
const height = 500;

// Define the projection and path
const projection = geoEqualEarth().scale(150).translate([width / 2, height / 2]);
const path = d3.geoPath(projection);

// Create the SVG element
const svg = d3.select("body").append("svg")
  .attr("width", width)
  .attr("height", height);

// Load the world map data
d3.json("https://raw.githubusercontent.com/d3/d3-geo/master/data/world-110m.json").then(data => {

  // Create the countries path and add it to the SVG element
  const countries = topojson.feature(data, data.objects.countries);
  svg.selectAll(".country")
    .data(countries.features)
    .join("path")
      .attr("class", "country")
      .attr("d", path)
      .attr("fill", "none")
      .attr("stroke", "black")
      .attr("stroke-width", 0.5);

  // Create the graticule path and add it to the SVG element
  const graticule = d3.geoGraticule();
  svg.append("path")
    .datum(graticule)
    .attr("class", "graticule")
    .attr("d", path)
    .attr("fill", "none")
    .attr("stroke", "black")
    .attr("stroke-width", 0.2);
});
