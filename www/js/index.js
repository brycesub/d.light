let idletime = 0;

function syncstate() {
  fetch('/stat')
    .then(r => r.json())
    .then(state => {
      const show = id => { document.getElementById(id).style.display = ''; };
      const hide = id => { document.getElementById(id).style.display = 'none'; };
      state.on ? hide('btnon') : show('btnon');
      state.on ? show('btnoff') : hide('btnoff');
      state.alarming ? show('btnsnooze') : hide('btnsnooze');
      state.alarming ? show('btnalarmoff') : hide('btnalarmoff');
      state.alarmset ? hide('btnalarmenable') : show('btnalarmenable');
      state.alarmset ? show('btnalarmdisable') : hide('btnalarmdisable');
      document.getElementById('dimmer').value = state.dim;
      document.getElementById('insnoozetime').value = state.snoozetime;
      document.getElementById('inalarmtime').value = state.alarmtime;
      document.getElementById('inbrightentime').value = state.brightentime;
    });
}

function resettimer() { idletime = 0; }

function idling() {
  if (idletime > 10000) syncstate();
  idletime += 500;
}

document.addEventListener('DOMContentLoaded', () => {
  syncstate();

  const on = (id, event, fn) => document.getElementById(id).addEventListener(event, fn);

  on('dimmer', 'change', function() { fetch('/dim/' + this.value).then(syncstate); });
  on('btnon', 'click', () => fetch('/light/on').then(syncstate));
  on('btnoff', 'click', () => fetch('/light/off').then(syncstate));
  on('btnalarmenable', 'click', () => fetch('/alarm/on').then(syncstate));
  on('btnalarmdisable', 'click', () => fetch('/alarm/off').then(syncstate));
  on('inalarmtime', 'change', function() { fetch('/alarmset/' + this.value).then(syncstate); });
  on('insnoozetime', 'change', function() { fetch('/snoozeset/' + this.value).then(syncstate); });
  on('inbrightentime', 'change', function() { fetch('/brightenset/' + this.value).then(syncstate); });
  on('btnsnooze', 'click', () => fetch('/snooze').then(syncstate));
  on('btnalarmoff', 'click', () => fetch('/alarmoff').then(syncstate));

  document.addEventListener('mousemove', resettimer);
  document.addEventListener('keypress', resettimer);
  setInterval(idling, 500);
});
