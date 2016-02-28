function syncstate(){
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
  });
}

$(document).ready(function(){

  syncstate();

  $("#dimmer").on("change",function(){
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

  $("#btnsetalarm").click(function(){
    $.get("/alarmset/"+$("#inalarmtime").val(), function(){ syncstate(); } );
  });

  $("#btnsetsnooze").click(function(){
    $.get("/snoozeset/"+$("#insnoozetime").val(), function(){ syncstate(); } );
  });

  $("#btnsnooze").click(function(){
    $.get("/snooze"), function(){ syncstate(); } );
  });

  $("#btnalarmoff").click(function(){
    $.get("/alarmoff", function(){ syncstate(); } );
  });
});
