/* global afatSettings, moment, console, manageModal */

$(document).ready(() => {
    'use strict';

    const DATETIME_FORMAT = 'YYYY-MMM-DD, HH:mm';

    /**
     * DataTable :: FAT link list
     */
    const linkListTable = $('#link-list').DataTable({
        ajax: {
            url: afatSettings.url.linkList,
            dataSrc: '',
            cache: false
        },
        columns: [
            {data: 'fleet_name'},
            {data: 'fleet_type'},
            {data: 'creator_name'},
            {
                data: 'fleet_time',
                render: {
                    display: (data, type, row) => {
                        return moment(data.time).utc().format(DATETIME_FORMAT);
                    },
                    _: 'timestamp'
                }
            },
            {data: 'fats_number'},

            {
                data: 'actions',
                render: (data, type, row) => {
                    if (afatSettings.permissions.addFatLink === true || afatSettings.permissions.manageAfat === true) {
                        return data;
                    } else {
                        return '';
                    }
                }
            },

            // hidden column
            {data: 'via_esi'},
            {data: 'hash'}
        ],

        columnDefs: [
            {
                targets: [5],
                orderable: false,
                createdCell: (td) => {
                    $(td).addClass('text-right');
                }
            },
            {
                visible: false,
                targets: [6, 7]
            }
        ],

        order: [
            [3, 'desc']
        ],

        filterDropDown: {
            columns: [
                {
                    idx: 1
                },
                {
                    idx: 6,
                    title: afatSettings.translation.dataTable.filter.viaEsi
                }
            ],
            autoSize: false,
            bootstrap: true
        },

        stateSave: true,
        stateDuration: -1
    });

    /**
     * Refresh the datatable information every 60 seconds
     */
    const intervalReloadDatatable = 60000; // ms
    let expectedReloadDatatable = Date.now() + intervalReloadDatatable;

    /**
     * Reload datatable "linkListTable"
     */
    const realoadDataTable = () => {
        const dt = Date.now() - expectedReloadDatatable; // the drift (positive for overshooting)

        if (dt > intervalReloadDatatable) {
            /**
             * Something really bad happened. Maybe the browser (tab) was inactive?
             * Possibly special handling to avoid futile "catch up" run
             */
            window.location.replace(
                window.location.pathname + window.location.search + window.location.hash
            );
        }

        linkListTable.ajax.reload(null, false);

        expectedReloadDatatable += intervalReloadDatatable;

        // take drift into account
        setTimeout(
            realoadDataTable,
            Math.max(0, intervalReloadDatatable - dt)
        );
    };

    setTimeout(
        realoadDataTable,
        intervalReloadDatatable
    );

    /**
     * Modal :: Close ESI fleet
     */
    const cancelEsiFleetModal = $(afatSettings.modal.cancelEsiFleetModal.element);
    manageModal(cancelEsiFleetModal);

    /**
     * Modal :: Delete FAT link
     */
    const deleteFatLinkModal = $(afatSettings.modal.deleteFatLinkModal.element);
    manageModal(deleteFatLinkModal);
});
