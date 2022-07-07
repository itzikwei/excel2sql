/* Last modefied against DB version 7.2 */
const	statusCode1 = '<span class="statusCodePlate pStatus',
        statusCode2 = '&nbsp;</span>',
        //statusCode1 = '<span class="statusCodePlate dry',
        //statusCode2 = '">&nbsp;Dry&nbsp;</span>',
        statusCode3 = '<span class="statusCodePlate xray',
        statusCode4 = '">&nbsp;X-ray&nbsp;</span>',
        statusCode5 = '<span class="statusCodePlate inSeed',
        statusCode6 = '">&nbsp;In seed&nbsp;</span>',
        statusCode7 = '<span class="statusCodePlate withSeed',
        statusCode8 = '">&nbsp;With seed&nbsp;</span>'
		;

function plateStatusText(code) {
       switch (code) {
        case "0": return 'Not in CRIMS'; break;
        case "1": return 'Active'; break;
        case "2": return 'Ignored'; break;
        case "3": return 'Done'; break;
        case "4": return 'Dry'; break;
        case "5": return 'Deleted'; break;
        default: return 'undetermined';
       }
}

function updatePlateStatusCode(targets, space){
    var newSpans = targets;
    for (var i = 0;i< newSpans.length;i++){
        var code = newSpans[i].className;
        var offset = code.indexOf('code') + 5;
        newSpans[i].parentNode.insertAdjacentHTML('beforeend',
        	space + 
            statusCode1 + code[offset] + '">&nbsp;' +
            plateStatusText(code[offset]) + statusCode2 +
            statusCode3 + code[offset+1]  + statusCode4 +
            statusCode5 + code[offset+2]  + statusCode6 +
            statusCode7 + code[offset+3]  + statusCode8
        )
    }
}

function updateSoakPlateStatusCode(targets, space){
    var newSpans = targets;
    for (var i = 0;i< newSpans.length;i++){
        var code = newSpans[i].className;
        var offset = code.indexOf('code') + 5;
        newSpans[i].parentNode.insertAdjacentHTML('beforeend',
        	space + 
            '<span class="statusCodePlate pStatus' + code[offset] + 
            '">&nbsp;' + plateStatusText(code[offset]) + '&nbsp;</span>' +
            statusCode3 + code[offset+1]  + statusCode4 +
            statusCode5 + code[offset+2]  + statusCode6
        )
    }
}

/*
function updatePlateStatusCode2(targets, space){	//old
    var newSpans = targets;
    for (var i = 0;i< newSpans.length;i++){
        var code = newSpans[i].className;
        var offset = code.indexOf('code') + 5;
        newSpans[i].parentNode.insertAdjacentHTML('beforeend',
        	space + 
            statusCode1 + code[offset]    + statusCode2 +
            statusCode3 + code[offset+1]  + statusCode4 +
            statusCode5 + code[offset+2]  + statusCode6 +
            statusCode7 + code[offset+3]  + statusCode8
        )
    }
}
*/

/*
function updateSoakPlateStatusCode2(targets, space){	//old
    var newSpans = targets;
    for (var i = 0;i< newSpans.length;i++){
        var code = newSpans[i].className;
        var offset = code.indexOf('code') + 5;
        newSpans[i].parentNode.insertAdjacentHTML('beforeend',
        	space + 
            statusCode1 + code[offset]    + statusCode2 +
            statusCode3 + code[offset+1]  + statusCode4 +
            statusCode5 + code[offset+2]  + statusCode6
        )
    }
}
*/

function updateSEPStatusCode(targets, space){
    var newSpans = targets;
    for (var i = 0;i< newSpans.length;i++){
        var code = newSpans[i].className;
        var offset = code.indexOf('code') + 5;
        newSpans[i].parentNode.insertAdjacentHTML('beforeend',
        	space + 
            statusCode3 + code[offset+1]  + statusCode4
        )
    }
}

// deprecated since concurrency control implementation
/*
function alterDeleteButtonOnCreation(){
	$('button#deleteObject span.t-Button-label').text('Cancel creation');
	$('button#deleteObject').attr('title','Creation of objects does not take affect until the first time an item is saved');	
}
*/

function object_redirect(page,obj_id,sourcepage=$v('pFlowStepId')){
	apex.navigation.redirect('f?p=' + $v('pFlowId') + ':' + page +
	':' + $v('pInstance') + ':::RP,' + page + ':P' + page + '_OBJ_ID,SOURCE_PAGE:' +
	obj_id + ',' + sourcepage)
}

function plasmid_redirect(plasmid_id, sourcepage=$v('pFlowStepId')){
	apex.navigation.redirect('f?p=' + $v('pFlowId') + ':1001:' +
	$v('pInstance') + ':::RP,1001:P1001_PLASMID_ID:' + plasmid_id)
}


/*
function padZeros(barcode, prefix = "[Bb][tT]|[sS]", zeros = 8){
	re = new RegExp( "(" + prefix + ")(\\d+[1-9])" )
	matching = barcode.match(re)
	if (!matching || matching[0].length != barcode.length) {return null}
	return matching[1].toUpperCase() + matching[2].padStart(zeros,'0')
}
*/

/* return true if "value_to_check" is selected it "select2_item_name", false otherwise */
function select2_check_if_value_selected(select2_item_name, value_to_check)
{
    selected_string = ''
    apex.item(select2_item_name).getValue().forEach(myFunction); 
    function myFunction(item) 
    { 
        selected_item = apex.item(select2_item_name).displayValueFor(item)
        selected_string = selected_string + selected_item
    }
    return selected_string.includes(value_to_check)
}

/* get all checked checkboxes, and return them concatenated as sting with ':' seperator.
   checkbox_p_idx is the checkbox p_idx defined in apex_item. */
function get_checked_items(checkbox_p_idx)
{
	if (!$('input[name=' + checkbox_p_idx + ']').length) {return null};
    var $check_boxes = $('input[name=' + checkbox_p_idx + ']:checked');
    var returned_string = '';
    $check_boxes.each(function(){
     returned_string += ':' + this.value; 
    });
return returned_string.substring(1);
}

/* use the previous function to set 'apex_item' with the selected checkboxes id's */
function set_selected_ids_in_item(checkbox_p_idx, apex_item)
{
	$s(apex_item, get_checked_items(checkbox_p_idx));
	if (!$v(apex_item))
	{
		alert('No items were selected');
	}
}


/* similar to  get_checked_items, but finding all unchecked checkboxes*/
function get_unchecked_items(checkbox_p_idx)
{
	if (!$('input[name=' + checkbox_p_idx + ']').length) {return null};
    var $unchecked_boxes = $('input[name=' + checkbox_p_idx + ']:not(:checked)');
    var returned_string = '';
    $unchecked_boxes.each(function(){
     returned_string += ':' + this.value; 
    });
return returned_string.substring(1);
}


/* This line intended to remove empty panel in Interactive report when table is empty */
/*$('.icon-irr-no-results').closest('.a-IRR-noDataMsg-icon').closest('.a-IRR-noDataMsg').hide()
*/

/* Get all the values of input items having name = p_idx. 
   Return them concatenated as sting with ':' seperator.*/
function get_input_values(p_idx)
{
	if (!$('input[name=' + p_idx + ']').length) {return null};
    var $input = $('input[name=' + p_idx + ']');
    var values = '';
    $input.each(function(){
        values += ':' + this.value; 
    });
	return values.substring(1);
}

/* Get the values of the selected option having name = p_idx. 
   Return them concatenated as sting with ':' seperator.*/
function get_selected_option_values(p_idx)
{
    var $input = $('select[name=' + p_idx + '] option').filter(':selected');
    var values = '';
    $input.each(function(){
        values += ':' +  $(this).val();
    });
	return values.substring(1);
}

/* Get all the values of textarea items having name = p_idx. 
   Return them concatenated as sting with '^' seperator.*/
function get_textarea_values(p_idx)
{
	if (!$('textarea[name=' + p_idx + ']').length) {return null};
    var $input = $('textarea[name=' + p_idx + ']');
    var values = '';
    $input.each(function(){
        values += '^' + this.value; 
    });
	return values.substring(1);
}

/* Get all the values of span items having id = p_idx. 
   Return them concatenated as sting with ':' seperator.*/
function get_span_values(p_idx)
{
	//var $input = $('span[id=' + p_idx + ']');
	var $input = $('span[id^=' + p_idx + ']')
    var values = '';
    $input.each(function(){
        values += ':' + $(this).text();
    });
	return values.substring(1);
}

/* Get the values of pill buttons (radio group) having name = p_idx. 
   Return them concatenated as sting with ':' seperator.*/
function get_pill_buttons_values(p_idx)
{
	var $input = $('span[id^=' + p_idx + ']');
    var values = '';
    $input.each(function(){
		
        values += ':' + $(this).find("a").not(".t-Button--simple").data('assessment'); 
    });
	return values.substring(1);
	
}

/*Display a page level message error*/
function show_page_message_error(msg)
{
	apex.message.showErrors(
		[{
			type: apex.message.TYPE.ERROR,
			location: ["page"],
			message: msg,
			unsafe: false
		}]
	);
}

/* remove some breadcrumbs entries as being clickable */
$('a.t-Breadcrumb-label').each(function(index, element){
	if ($(element).text() == 'Crystallization'  ||
		$(element).text() == 'Maintenance'		||
		$(element).text() == 'Expression'		||
		$(element).text() == 'Purification'		||
		$(element).text() == 'Reports'	) 	
		{
			$(element).parent().text($(element).text()).css('color', 'black');
		
		}
});

/* In tables with 'Download' option to files,
this makes the supported files to be Displayed in new tab, instead of downloaded */
function makeSupportedFilesDisplayable(p_idx){
    var filenames_str = get_input_values(p_idx);
	if (filenames_str === null) {
		return;
	}
	var filenames = filenames_str.split(':');
    var i = 0;
    $('table > tbody > tr').slice(1).each(function(index) {
        var filename = filenames[i];
        i++;
        // in case no file in table we don't want error in 'split'
        if(filename == '-' || filename == '') {return;}

        var file_extension = filename.split('.').pop();
		var link_element = $(this).find('[headers=View]').find('a');
        if (['html','pdf','png','log','txt','js','css','jpg','gif','jgeg','png','svg'].includes(file_extension.toLowerCase())) {
			link_element[0].innerHTML = '<i class="fa fa-eye"></i>' + ' ' + filename;
			// to open the file in new tab
			link_element.attr("target", "_blank");
        }
		else {
			link_element[0].innerHTML = '<i class="fa fa-download"></i>' + ' ' + filename;
		}
    });
}

/* functions used to notify user if collapsible region is empty or filled with rows/columns */
function is_table_empty(){
	return $(this.triggeringElement).find('.nodatafound').length==1;
}
function collapsible_empty(element){
	$(element).find('.a-Collapsible-icon').parent().css("background-color", "#c4c0b3"); /*#fffda8 */
}
function collapsible_not_empty(element){
	$(element).find('.a-Collapsible-icon').parent().css("background-color", "#87aaff");
}

/* There is a bug in the Template "LIMS Right Side Column", that can't be solved, where the "About" 
	section next to the breadcrumb is not aligned to the right, so this solves that */
$('.t-Form-labelContainer').find("label:contains(About this page)").parent().css("text-align", "right");

 $(".allow_only_number").bind("keypress", function (e) {
          var keyCode = e.which ? e.which : e.keyCode;
		  // if it's a digit (0-9) or it's a dot 
          if ((keyCode >= 48 && keyCode <= 57) || keyCode == 46) {
            return true;
          }else{
              return false;
          }
      });

 $(".allow_whole_number").bind("keypress", function (e) {
          var keyCode = e.which ? e.which : e.keyCode;
		  // if it's a digit (0-9) or it's a dot 
          if ((keyCode >= 48 && keyCode <= 57)) {
            return true;
          }else{
              return false;
          }
      });

/* this functions meant to replace Apex dynamic action "Hide"/ "Show" when there are a lot of items,
   since it is hard to follow in Apex.
   it gets a list of arguments, where each argument is the Apex item name */ 	  
function hide_items(...args){
	var debug_string = 'hide:';
	args.forEach((arg, index) => {
	debug_string = debug_string + ' #' + arg + '_CONTAINER';
	$('#' + arg + '_CONTAINER').hide();
    });
    console.log(debug_string);
}
function show_items(...args){
	var debug_string = 'show:';
	args.forEach((arg, index) => {
	debug_string = debug_string + ' #' + arg + '_CONTAINER';
	$('#' + arg + '_CONTAINER').show();
    });
    console.log(debug_string);
}


/* the next 3 functions are correlated to the drag and drop of rows in tables in order to re-arrange them.
   an example can be found in "cell treatment" project.
   p_idx is a number that identifies the item generated in the workflow table */
function make_sortable(region_ID, p_idx, sorted_ids_page_item) {
  console.log('makeSortable: with region ID'  + region_ID);
  var $report_regions = $("#report_" + region_ID);
  var report_region = $report_regions[0];

   // add DISPLAY_ORDER to TR element (row in the table) so we know the position before the change
  $report_regions.find("[headers='DISPLAY_ORDER']").each(
  function(){ 
        //console.log($(this).get(0).innerHTML);
        $(this).parent().attr('data-id',$(this).get(0).innerHTML);
  });

  // finally make it sortable
  $report_regions.find("table.t-Report-report").sortable({
      cancel: "td[headers!='DERIVED$01'],th",
      cursor: "n-resize",
      items: 'tr',
	  // containment - use to restrict how far the elements can be dragged. in our case the workflow report
      containment: report_region,
      helper: fixHelper,
	  // we define the function "update_display_seq()" for saving the new order
      update: function(event,ui) { update_display_seq(report_region, p_idx, sorted_ids_page_item); }
  }); 
}
/* function to set the new order
   region_ID is the Static ID of the report */
function update_display_seq(region_ID, p_idx, sorted_ids_page_item) {
    //return an array with the "old order" of our lines
    var workflow_ids = get_input_values(p_idx);
    console.log('workflow_ids: ' + workflow_ids);
    $s(sorted_ids_page_item, workflow_ids);
	//run the UPDATE_ORDER process (found in Apex page)
    apex.server.process (
        "UPDATE_ORDER",
        {pageItems: '#' + sorted_ids_page_item},
        {dataType: "text"}
		).done( function( responseData ){
			// if there is a DB error then show the error message
			if (responseData) {
				alert('DB error occurred. Please contact the developers: ' + responseData);
			}
			else {
				apex.event.trigger(region_ID, 'apexrefresh');
			}
		// if the JS (not the SQL command) failed then show error
		}).fail( function( jqXHR, textStatus, errorThrown ){
			alert('Sorting rows failed (Javascript error). Please contact the developers. ' + textStatus + '. ' + errorThrown);
        });
}
// set the width or the TR being dragged to the original width it had
var fixHelper = function(e, ui) {
    ui.children().each(function() {
        $(this).width($(this).width());
    });
    return ui;
};

function update_checkbox_via_ajax(triggering_element, plsql_process_name) {
	var id = triggering_element.attr('value');
	var is_checked = 0;
	if (triggering_element[0].checked){
		is_checked = 1;
	}
	apex.server.process (
		plsql_process_name,
		{x01: id, x02: is_checked},
		{dataType: "text"}
	).done( function( responseData ){
			// if there is a DB error then show the error message
			if (responseData.includes("LIMS error")) {
				alert('DB error occurred. Please contact the developers: ' + responseData);
			}
		// if the JS (not the SQL command) failed then show error
	}).fail( function( jqXHR, textStatus, errorThrown ){
		alert('Javascrupt error. Please contact the developers. ' + textStatus + '. ' + errorThrown);
    });
}