/* global afatSettings, moment, AFAT_DATETIME_FORMAT */

$(document).ready(() => {
    'use strict';

    const dtLanguage = afatSettings.dataTable.language;

    /**
     * DataTable :: FAT link list
     */
    $('#afat-logs').DataTable({
        language: dtLanguage,
        ajax: {
            url: afatSettings.url.logs,
            dataSrc: '',
            cache: false
        },
        columns: [
            {
                data: 'log_time',
                render: {
                    display: (data) => {
                        return moment(data.time).utc().format(AFAT_DATETIME_FORMAT);
                    },
                    _: 'timestamp'
                }
            },
            {data: 'log_event'},
            {data: 'user'},
            {
                data: 'fatlink',
                render: {
                    display: 'html',
                    _: 'hash'
                }
            },
            {data: 'description'}
        ],

        order: [
            [0, 'desc']
        ],

        filterDropDown: {
            columns: [
                {
                    idx: 1
                },
                {
                    idx: 2
                }
            ],
            autoSize: false,
            bootstrap: true,
            bootstrap_version: 5
        },

        stateSave: true,
        stateDuration: -1
    });
});
