"use strict";require(["jquery","underscore","backbone","sa-utils/js/views/LookupEditorView","splunkjs/mvc/simplexml/ready!"],function(a,b,c,d){a("#lookup_editor").text(b("Loading...").t()),new d({el:a("#lookup_editor"),lister:"ess_lookups_list",list_link_title:b("Back to Lookups List").t(),list_link:"ess_lookups_list"}).render()});
