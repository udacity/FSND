function storeSelectedGenresToWindow() {
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
