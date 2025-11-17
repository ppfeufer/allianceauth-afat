/* global afatSettings, _dateRender, fetchGet, DataTable, _removeSearchFromColumnControl */

$(document).ready(() => {
    'use strict';

    /**
     * DataTable :: FAT link list
     */
    fetchGet({url: afatSettings.url.logs})
        .then((data) => {
            const dt = new DataTable($('#afat-logs'), { // eslint-disable-line no-unused-vars
                ...afatSettings.dataTables,
                data: data,
                columns: [
                    {
                        data: {
                            display: (data) => _dateRender(data.log_time.time),
                            sort: (data) => data.log_time.timestamp
                        }
                    },
                    {data: 'log_event'},
                    {data: 'user'},
                    {
                        data: {
                            display: (data) => data.fatlink.html,
                            sort: (data) => data.fatlink.hash
                        }
                    },
                    {data: 'description'}
                ],
                columnDefs: [
                    {
                        targets: 0,
                        columnControl: _removeSearchFromColumnControl()
                    }
                ],
                order: [
                    [0, 'desc']
                ]
            });
        })
        .catch((error) => {
            console.error('Error fetching FAT logs:', error);
        });
});
