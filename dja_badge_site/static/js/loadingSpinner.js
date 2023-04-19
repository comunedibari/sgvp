/**
 * spinner caricamento in corso...
 */

function switchSpinner(switchEnable){
    if(switchEnable){
        document.getElementById("op-loading-node").style.display = "block";
    }else{
        document.getElementById("op-loading-node").style.display = "none";
    }
    
}

window.addEventListener("load", () => {
    switchSpinner(false);
});


function getPdfDocument(url) {
    switchSpinner(true);
    fetch(url, {
      headers: {
        "X-Requested-With": "XMLHttpRequest",
      }
    })
    .then( res => res.blob())
    .then( blob => {
        switchSpinner(false);
        var file = window.URL.createObjectURL(blob);
        window.location.assign(file);
    });
  }
  