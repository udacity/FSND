window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

async function DeleteVenue(event) {
    log('inside DeleteVenue', this, event);
    VenueId = event.target.dataset['id']
    const route = '/venues/' + String(VenueId);
    log('DeleteVenue', this, route);
    log('DeleteVenue csrf_token', this, csrf_token);
    const response = await fetch(String(route), {
        method: 'DELETE',
        body: JSON.stringify(
        {
          'venue_id': VenueId
        }),
        headers:
        {
          'X-CSRFToken': csrf_token,
          'Content-Type': 'application/json'
        }
    }).then( function(response) {
        log('DeleteValue response', this, response);
        return response.json();
    }).then( function(jsonResponse) {
        const destination = window.origin + jsonResponse['url']
        log('DeleteValue jsonResponse', this, jsonResponse);
        log('DeleteValue dest', this, destination);
        window.location = destination;
        return jsonResponse['success'];
    }).catch( function(e) {
     console.log(e);
     return false;
    });
}