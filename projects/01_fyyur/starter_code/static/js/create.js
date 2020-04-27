export function storeSelectedGenresToWindow() {
  console.log('I am running')
  document.querySelector('select[multiple]').onchange = function (e) {
    let genres = [];
    for (const option of e.target.options) {
      if (option.selected) {
        genres.push(option.value);
      }
    }
    window.genres = genres;
  };
}

export function fetchCreateThenHome(data) {
  const table = window.location.pathname.split('/')[1];//pathname outputs '/table/crud-action' type string
  fetch('/' + table + '/create', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  }).then(response => {
    if (!response.ok) {
      throw Error(response.statusText)
    } else {return response.json()}
  }).then(jsonResponse => {

    let name = getNameFromResponse(jsonResponse);

    alert(table + ' ' + name + ' was successfully listed!');
    window.location.href = "/";
  })
}

export function parseFormFields(event){
  let data = {};
  data['genres'] = window.genres;
  data['state'] = event.target.querySelector('select:not([multiple])').value
  console.log('state value in function:', event.target.querySelector('select:not([multiple])').value)
  const inputs = event.target.querySelectorAll('input');
  for (const input of inputs) {
    if (!!input.value && input.type !== 'submit') {
      const val = input.value
      const key = input.name
      data[key] = val
    }
  }
  return data
}

function getNameFromResponse(jsonResponse) {
  let name;
  if (jsonResponse.hasOwnProperty('venue_name')) {
    name = jsonResponse['venue_name']
  } else { name = jsonResponse['name']}
  return name
}