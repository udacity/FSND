window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};


if (document.getElementById('seeking_venue-0') !== null) {
  document.getElementById('seeking_venue-0').addEventListener('click', () => {
    document.getElementById('seeking_description').style.display = 'block'
  });

  document.getElementById('seeking_venue-1').addEventListener('click', () => {
    document.getElementById('seeking_description').style.display = 'none'
  });
}

if (document.getElementById('seeking_talent-0') !== null) {
  document.getElementById('seeking_talent-0').addEventListener('click', () => {
    document.getElementById('seeking_description').style.display = 'block'
  });

  document.getElementById('seeking_talent-1').addEventListener('click', () => {
    document.getElementById('seeking_description').style.display = 'none'
  });
}

async function deleteVenue(venueId) {
  const result = await fetch('/venues/' + venueId, {
    method: 'DELETE'
  });

  const data = await result.json();

  if (data.status === 200) {
    displayAlert('Venue succesfuly deleted.');
    window.location.replace("http://127.0.0.1:5000/venues");
  } else {
    displayAlert('Failed to delete the venue. It is most likely attached to a show.');
  }
}

function displayAlert(message) {
  const alert = document.getElementById('alert');
  alert.style.display = 'block';
  alert.innerHTML = message
}

function displayAvailabiltyForm() {
  document.getElementById("availability-form").style.display = "block";
}

async function deleteAvailabilitySlot(artist_id, slot_id) {
  const result = await fetch('/availability/' + artist_id + '/' + slot_id,
    { method: 'DELETE' });

  const data = await result.json();

  if (data.status === 200) {
    window.location.replace("http://127.0.0.1:5000/availability/" + artist_id);
  }
}
