const seekingTalent = document.getElementById('seeking-talent')
const seekingDesc = document.getElementById('seeking-desc')

if(seekingTalent.checked) {
    seekingDesc.className = "form-group"
}

seekingTalent.onclick = function(e) {
    toggleCheck(this)
}

function toggleCheck(check) {
    if(check.checked) {
    seekingDesc.className = "form-group"
    } else {
    seekingDesc.className = "form-group hidden-desc"
    }
}