/* global afatSettings, moment, manageModal, AFAT_DATETIME_FORMAT */

$(document).ready(() => {
    'use strict';

    const dtLanguage = afatSettings.dataTable.language;

    const linkListTableColumns = [
        {data: 'fleet_name'},
        {data: 'fleet_type'},
        {data: 'doctrine'},
        {data: 'creator_name'},
        {
            data: 'fleet_time',
            render: {
                display: (data) => {
                    return moment(data.time).utc().format(AFAT_DATETIME_FORMAT);
                },
                _: 'timestamp'
            }
        },
        {data: 'fats_number'}
    ];

    const linkListTableColumnDefs = [
        {
            targets: [5],
            createdCell: (td) => {
                $(td).addClass('text-end');
            },
        }
    ];

    if (afatSettings.permissions.addFatLink === true || afatSettings.permissions.manageAfat === true) {
        linkListTableColumns.push(
            {
                data: 'actions',
                render: (data) => {
                    return data;
                }
            },
        );

        linkListTableColumnDefs.push(
            {
                targets: [6],
                orderable: false,
                createdCell: (td) => {
                    $(td).addClass('text-end');
                },
            },
            // Hide the columns, which are only for searching
            {
                targets: [7, 8],
                visible: false
            }
        );
    } else {
        // Hide the columns, which are only for searching
        linkListTableColumnDefs.push({
            targets: [6, 7],
            visible: false
        });
    }

    // Add hidden columns
    linkListTableColumns.push(
        {data: 'via_esi'},
        {data: 'hash'}
    );

    /**
     * DataTable :: FAT link list
     */
    const linkListTable = $('#link-list').DataTable({
        language: dtLanguage,
        ajax: {
            url: afatSettings.url.linkList,
            dataSrc: '',
            cache: false
        },
        columns: linkListTableColumns,
        columnDefs: linkListTableColumnDefs,

        order: [
            [4, 'desc']
        ],

        filterDropDown: {
            columns: [
                {
                    idx: 1
                },
                {
                    idx: 7,
                    title: afatSettings.translation.dataTable.filter.viaEsi
                }
            ],
            autoSize: false,
            bootstrap: true,
            bootstrap_version: 5
        },
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
        const currentPath = window.location.pathname + window.location.search + window.location.hash;

        if (dt > intervalReloadDatatable) {
            /**
             * Something awful happened. Maybe the browser (tab) was inactive?
             * Possibly special handling to avoid futile "catch up" run
             */
            if (currentPath.startsWith('/')) {
                window.location.replace(currentPath);
            } else {
                console.error('Invalid redirect URL');
            }
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
