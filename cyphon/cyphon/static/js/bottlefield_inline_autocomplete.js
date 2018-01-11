/**
 * Copyright 2017-2018 Dunbar Security Solutions, Inc.
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

(function($) {
    $(document).ready(function() {

        // save selected bottle to field_name autocomplete widgets,
        // so bottler.bottles.autocomplete.BottleFieldAutocomplete can filter
        // field_name options appropriately
        saveMasterFieldValue('bottle', 'field_name');
        
        // save list of selected field_names to each field_name autocomplete
        // widget, so bottler.bottles.autocomplete.BottleFieldAutocomplete can
        // remove them from available options
        saveSelectedValues('field_name');

    });
} (django.jQuery));