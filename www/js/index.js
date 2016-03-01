var idletime = 0;

function syncstate() {
  $.getJSON("/stat", function(state){
    if (state.on == true) {
      $("#btnon").hide();
      $("#btnoff").show();
    } else {
      $("#btnon").show();
      $("#btnoff").hide();
    }
    if (state.alarming == true) {
      $("#btnsnooze").show();
      $("#btnalarmoff").show();
    } else {
      $("#btnsnooze").hide();
      $("#btnalarmoff").hide();
    }
    if (state.alarmset == true) {
      $("#btnalarmenable").hide();
      $("#btnalarmdisable").show();
    } else {
      $("#btnalarmenable").show();
      $("#btnalarmdisable").hide();
    }
    $("#dimmer").val(state.dim);
    $("#insnoozetime").val(state.snoozetime);
    $("#inalarmtime").val(state.alarmtime);
    $("#inbrightentime").val(state.brightentime);
  });
}

function resettimer() {
  idletime = 0;
}

function idling() {
  if (idletime > 5000) {
    syncstate();
  }
  idletime = idletime + 500;
}

$(document).ready(function() {

  syncstate();

  $("#dimmer").change(function(){
    $.get("/dim/"+$(this).val(), function(){ syncstate(); } );
  });

  $("#btnon").click(function(){
    $.get("/light/on", function(){ syncstate(); } );
  });

  $("#btnoff").click(function(){
    $.get("/light/off", function(){ syncstate(); } );
  });

  $("#btnalarmenable").click(function(){
    $.get("/alarm/on", function(){ syncstate(); } );
  });

  $("#btnalarmdisable").click(function(){
    $.get("/alarm/off", function(){ syncstate(); } );
  });

  $("#inalarmtime").change(function(){
    $.get("/alarmset/"+$(this).val(), function(){ syncstate(); } );
  });

  $("#insnoozetime").change(function(){
    $.get("/snoozeset/"+$(this).val(), function(){ syncstate(); } );
  });

  $("#inbrightentime").change(function(){
    $.get("/brightenset/"+$(this).val(), function(){ syncstate(); } );
  });

  $("#btnsnooze").click(function(){
    $.get("/snooze", function(){ syncstate(); } );
  });

  $("#btnalarmoff").click(function(){
    $.get("/alarmoff", function(){ syncstate(); } );
  });

  resettimer();
  $(this).mousemove(resettimer);
  $(this).keypress(resettimer);
  $(document).focus(syncstate);
  $(document).click(syncstate);

  setInterval(idling,500);
});
