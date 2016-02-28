function syncstate(){
  $.getJSON("/stat", function(state){
    if (state.on == true) {
      $("#btnon").hide();
      $("#btnoff").show();
    } else {
      $("#btnon").show();
      $("#btnoff").hide();
    }
    $("#dimmer").val(state.dim);
  });
}

$(document).ready(function(){

  syncstate();

  $("#dimmer").on("change",function(){
    $.get("/dim/"+$(this).val(), function(){ syncstate(); } );
  });

  $("#btnon").click(function(){
    $.get("/on", function(){ syncstate(); } );
  });

  $("#btnoff").click(function(){
    $.get("/off", function(){ syncstate(); } );
  });
});
