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

