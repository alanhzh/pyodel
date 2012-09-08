function plugin_pyodel_load_workspace(action, target){
  // collapse all workspaces
  jQuery(".collapsible").attr("style", "display:none;");
  // load component
  web2py_component(action, target);
  jQuery("#" + target + " " + ".collapsible").attr("style", "display:block;");
}

function plugin_pyodel_show_hide(target){
  var plugin_pyodel_target = jQuery(target);
  if (plugin_pyodel_target.css("display") == "block"){
    plugin_pyodel_target.css("display", "none");
  }
  else{plugin_pyodel_target.css("display", "block");}
}

function plugin_pyodel_gradebook_url(url){
  url = url.replace("%3Cauth_user.id%3E", jQuery("#plugin_pyodel_bureau_gradebook_form select").val());
  return url;
}

function plugin_pyodel_course_preview(){
  var plugin_pyodel_course_preview_value = this.value;
  jQuery("#plugin_pyodel_course_preview").html("");
  jQuery.each(plugin_pyodel_course_previews, function(i, val){
      if (val[0] == plugin_pyodel_course_preview_value){
        jQuery("#plugin_pyodel_course_preview").html(val[1]);
      }
    });
}
