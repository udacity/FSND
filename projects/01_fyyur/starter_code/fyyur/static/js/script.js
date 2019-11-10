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
