/* global afatSettings, DataTable, _removeSearchFromColumnControl */

$(document).ready(() => {
    'use strict';

    /**
     * DataTable :: FAT link list
     */
    const dtColumn = {
        time: 0,
        user: 1,
        fatLink: 2,
        description: 3
    };
    const dt = new DataTable($('#afat-logs'), { // eslint-disable-line no-unused-vars
        ...afatSettings.dataTables,
        columnDefs: [
            {
                targets: dtColumn.time,
                columnControl: _removeSearchFromColumnControl()
            }
        ],
        order: [
            [dtColumn.time, 'desc']
        ]
    });
});
