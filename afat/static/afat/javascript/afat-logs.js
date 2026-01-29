/* global afatSettings, DataTable, _removeSearchFromColumnControl */

$(document).ready(() => {
    'use strict';

    /**
     * DataTable :: FAT link list
     */
    const dt = new DataTable($('#afat-logs'), { // eslint-disable-line no-unused-vars
        ...afatSettings.dataTables,
        serverSide: true,
        ajax: afatSettings.url.logs,
        columnDefs: [
            {
                target: 0,
                columnControl: _removeSearchFromColumnControl()
            }
        ],
        order: [
            [0, 'desc']
        ]
    });
});
