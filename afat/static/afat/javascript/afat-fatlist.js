/* global afatSettings, _dateRender, _manageModal, fetchGet, _removeSearchFromColumnControl, _removeColumnControl, DataTable */

$(document).ready(() => {
    'use strict';

    const hasPermissions = afatSettings.permissions.addFatLink || afatSettings.permissions.manageAfat;

    // Base columns configuration
    const linkListTableColumns = [
        {data: 'fleet_name'},
        {data: 'fleet_type'},
        {data: 'doctrine'},
        {data: 'creator_name'},
        {
            data: {
                display: (data) => _dateRender(data.fleet_time.time),
                sort: (data) => data.fleet_time.timestamp
            },
        },
        {data: 'fats_number'},
    ];

    // Add actions column if user has permissions
    if (hasPermissions) {
        linkListTableColumns.push({
            data: 'actions'
        });
    }

    // Column definitions based on permissions
    const linkListTableColumnDefs = [
        {
            targets: [4, 5],
            columnControl: _removeSearchFromColumnControl(),
        },
    ];

    if (hasPermissions) {
        linkListTableColumnDefs.splice(1, 0, {
            target: 6,
            createdCell: (td) => {
                $(td).addClass('text-end');
            },
            columnControl: _removeColumnControl(),
            orderable: false,
            width: 125
        });
    }

    const linkListTable = $('#link-list');
    const RELOAD_INTERVAL = 60000;
    let expectedReloadTime = Date.now() + RELOAD_INTERVAL;

    // Initialize DataTable
    const initializeDataTable = (data) => {
        const dt = new DataTable(linkListTable, { // eslint-disable-line no-unused-vars
            ...afatSettings.dataTables,
            data: data,
            columns: linkListTableColumns,
            columnDefs: linkListTableColumnDefs,
            order: [[4, 'desc']],
        });
    };

    // Reload DataTable data
    const reloadDataTable = () => {
        const drift = Date.now() - expectedReloadTime;

        if (drift > RELOAD_INTERVAL) {
            const currentPath = window.location.pathname + window.location.search + window.location.hash;

            if (currentPath.startsWith('/')) {
                window.location.replace(currentPath);

                return;
            }

            console.error('Invalid redirect URL');
        }

        fetchGet({url: afatSettings.url.linkList})
            .then((newData) => {
                linkListTable.DataTable().clear().rows.add(newData).draw();
            })
            .catch((error) => {
                console.error('Error fetching updated data:', error);
            });

        expectedReloadTime += RELOAD_INTERVAL;

        setTimeout(reloadDataTable, Math.max(0, RELOAD_INTERVAL - drift));
    };

    // Initialize table and auto-reload
    fetchGet({url: afatSettings.url.linkList})
        .then((data) => {
            initializeDataTable(data);

            setTimeout(reloadDataTable, RELOAD_INTERVAL);
        })
        .catch((error) => {
            console.error('Error fetching link list:', error);
        });

    // Initialize modals
    [
        afatSettings.modal.cancelEsiFleetModal.element,
        afatSettings.modal.deleteFatLinkModal.element,
    ].forEach((modalElement) => {
        _manageModal($(modalElement));
    });
});
