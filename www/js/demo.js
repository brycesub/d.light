var dim = 0;
var dir = 1;

function demo() {
  if (dir > 0) {
    dim = dim+1;
  } else {
    dim = dim-1;
  }

  if (dim == 0) {
    dir = 1;
  }
  if (dim == 100) {
    dir = -1;
  }
  $("#demodim").html(dim);
  $.get("/dim/"+dim );
}

$(document).ready(function() {
  setInterval(demo,100);
});
