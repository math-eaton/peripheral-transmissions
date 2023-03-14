// Get all network requests from the developer tools
const requests = performance.getEntriesByType('resource');

// Filter requests that have a type of "media"
const mediaRequests = requests.filter(request => request.initiatorType === 'media');

// Extract the URLs of the media requests
const mediaUrls = mediaRequests.map(request => request.name);

// Output the URLs to the console
console.log(mediaUrls);
