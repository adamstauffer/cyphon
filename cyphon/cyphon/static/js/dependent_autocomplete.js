/**
 * Copyright 2017 Dunbar Security Solutions, Inc.
 * 
 * This file is part of Cyphon Engine.
 * 
 * Cyphon Engine is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * Cyphon Engine is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with Cyphon Engine. If not, see <http://www.gnu.org/licenses/>.
 */

/**
 * Functions for refining the behavior of Django Automplete Light fields to
 * allow for conditional options.
 */


/**
 * Passes the selected value of a master field to the autocomplete widget of a
 * dependent field, so it can be used to filter choices.
 * 
 * @param {string} master_field    The name of the field used for filtering
 * @param {string} dependent_field The name of the field to be filtered
 * @return {undefined}
 */
function saveMasterFieldValue(masterField, dependentField) {
    var inline = '-' + masterField;
    var selector = '[name='+masterField+'], [name$='+inline+']';

    // NOTE: use name$= selector to catch inline objects that include a prefix
    $('body').delegate(selector, 'change', function() {
        var $dependentSelects = $('[name$='+dependentField+']');
        var $dependentWidgets = $dependentSelects
                                .parents('.autocomplete-light-widget');
        var value = $(this).val();
        $dependentWidgets.each(function(){
            var widget = $(this).yourlabsWidget();
            widget.autocomplete.data[masterField] = value;
        });
    });

    // trigger change when function is first called (e.g., on page load)
    $(selector).change();

    // if a new dependent field is dynamically added, trigger a change
    // in the masterField so the new dependent field is updated
    $('body').bind('DOMNodeInserted', function(e) {
        var $element = $(e.target);
        var $newDependent = $element.find('[name$='+dependentField+']');
        if ($newDependent.length > 0) {
            $(selector).change();  
        }
    });
}


/**
 * Manually fires the onchange event for a DOM element.
 * 
 * @param  {string} element   the DOM element for which to fire the event
 */
function manuallyTriggerChange(element) {
    if ('createEvent' in document) {
        var evt = document.createEvent('HTMLEvents');
        evt.initEvent('change', false, true);
        element.dispatchEvent(evt);
    } else {
        element.fireEvent('onchange');   
    } 
}


/**
 * Sets the value of a dependent field according to whether or not a master
 * field has a certain value.
 * 
 * @param {string} fieldset         A CSS selector that identifies each 
 *                                      fieldset in which a pair of master and
 *                                      dependent fields are found
 * @param {string} masterField      A CSS selector that identifies a master
 *                                      field within a fieldset
 * @param {string} masterValue      The possible value for the master field
 *                                      that, if selected, should cause the
 *                                      dependent field to be set to the
 *                                      conditional value
 * @param {string} dependentField   A CSS selector that identifies a dependent
 *                                      field within a fieldset
 * @param {string} conditionalValue The value that should be selected for the
 *                                      dependent field if the master field is
 *                                      set to the masterValue
 * @param {string} defaultValue     The value that should be selected for the
 *                                      dependent field if the master field is
 *                                      NOT set to the masterValue
 * @return {undefined}
 */
function setDependentField(fieldset, masterField, masterValue,
                        dependentField, conditionalValue, defaultValue) {

    $('body').delegate(masterField, 'change', function() {
        var value;        
        var $dField = $(this).parents(fieldset).find(dependentField+' select');

        // determine if a masterValue was selected
        var $deck = $(this).find('.deck:contains('+masterValue+')');
        var condIsTrue = $deck.length > 0;

        // find the value of the appropriate dependentField option
        if (condIsTrue) {
            value = $dField.find('option:contains('+conditionalValue+')').val();
        } else {
            value = $dField.find('option:contains('+defaultValue+')').val();
        }

        // set the dependentField with the fetched value
        $dField.val(value);

        // jQuery change() doesn't seem to work here, so manually fire the
        // onchange event to make the lookup tool visible in the object_id field
        manuallyTriggerChange($dField[0]);
    });

    // trigger change when function first called (e.g., on page load)
    $(masterField).change();
}


/**
 * Returns the values of form fields with names sharing a common root. Can be
 * used to determine which options have been selected among a set of inline
 * forms.
 * 
 * @param  {string} field   "Ends-with" substring matching the name(s) of the
 *                              form field(s) from which values should be
 *                              collected
 * @return {array}          An array containing the values of the form fields
 */
function getSelectedValues(field) {
    var selectedValues = [];
    $('[name$='+field+']').each(function() {
        var value = $(this).val();
        if (value) {
            selectedValues.push(value[0]);
        }
    });
    return selectedValues;
}


/**
 * Collects selected values for a set of form fields whose names share a common
 * root, and saves the array of values to each field's autocomplete widget.
 * Can be used to keep track of which options have already been selected for a
 * particular field in a set of inline forms.
 * 
 * @param  {string} field   "Ends-with" substring matching the name(s) of the
 *                              form field(s) from which values should be
 *                              collected
 * @return {undefined}
 */
function saveSelectedValues(field) {
    var selector = '[name$='+field+']';

    $('body').delegate(selector, 'change', function() {
        var $selects = $(selector);
        var $widgets = $selects
                        .parents('.autocomplete-light-widget');
        $widgets.each(function(){
            var widget = $(this).yourlabsWidget();
            var values = getSelectedValues(field);
            widget.autocomplete.data[field + '_list'] = JSON.stringify(values);
        });
    });

    // trigger change when function is first called (e.g., on page load)
    $(selector).change();

    // if a new field is dynamically added, trigger a change event
    // so it's updated with the list of selected values
    $('body').bind('DOMNodeInserted', function(e) {
        var $element = $(e.target);
        var $newDependent = $element.find(selector);
        if ($newDependent.length > 0) {
            $newDependent.change();
        }
    });
}
