let dim = 0;
let dir = 1;

function demo() {
  dim += dir;
  if (dim === 0) dir = 1;
  if (dim === 100) dir = -1;
  document.getElementById('demodim').textContent = dim;
  fetch('/dim/' + dim);
}

document.addEventListener('DOMContentLoaded', () => {
  setInterval(demo, 100);
});
