/* global moment */

/**
 * Datetime formatting
 *
 * @param format
 * @param locale
 */
$.fn.dataTable.moment = function(format, locale) {
    'use strict';

    const types = $.fn.dataTable.ext.type;

    // Add type detection
    types.detect.unshift(function(d) {
        return moment(d, format, locale, true).isValid() ? 'moment-' + format : null;
    });

    // Add sorting method - use an integer for the sorting
    types.order['moment-' + format + '-pre'] = function(d) {
        return moment(d, format, locale, true).unix();
    };
};
