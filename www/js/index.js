$(document).ready(function(){

  $("#dimmer").on("change",function(){
    $.get("/dim/"+$(this).val());
  });

  $("#btnon").click(function(){
    $.get("/on");
  });

  $("#btnoff").click(function(){
    $.get("/off");
  });
});
