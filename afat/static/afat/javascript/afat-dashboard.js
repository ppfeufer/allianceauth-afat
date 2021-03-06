/* global afatSettings, characters, moment, manageModal */

$(document).ready(function () {
    'use strict';

    const DATETIME_FORMAT = 'YYYY-MMM-DD, HH:mm';

    /**
     * DataTable :: Recent FATs per character
     */
    if (characters.length > 0) {
        let noFatsWarning = '<div class="alert alert-warning" role="alert">' +
            '<p>' + afatSettings.translation.dataTable.noFatsWarning + ' ###CHARACTER_NAME###</p>' +
            '</div>';

        characters.forEach(function (character) {
            $('#recent-fats-character-' + character.charId).DataTable({
                ajax: {
                    url: afatSettings.url.characterFats.replace(
                        '0',
                        character.charId
                    ),
                    dataSrc: '',
                    cache: false
                },
                columns: [
                    {data: 'fleet_name'},
                    {data: 'fleet_type'},
                    {data: 'system'},
                    {data: 'ship_type'},
                    {
                        data: 'fleet_time',
                        render: {
                            display: function (data, type, row) {
                                return moment(data.time).utc().format(
                                    DATETIME_FORMAT
                                );
                            },
                            _: 'timestamp'
                        }
                    }
                ],
                language: {
                    emptyTable: noFatsWarning.replace(
                        '###CHARACTER_NAME###',
                        character.charName
                    )
                },
                paging: false,
                ordering: false,
                searching: false,
                info: false
            });
        });
    }

    /**
     * DataTable :: Recent FAT links
     */
    let noFatlinksWarning = '<div class="alert alert-warning" role="alert">' +
        '<p>' + afatSettings.translation.dataTable.noFatlinksWarning + '</p>' +
        '</div>';

    $('#dashboard-recent-fatlinks').DataTable({
        ajax: {
            url: afatSettings.url.recentFatLinks,
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
                    display: function (data, type, row) {
                        return moment(data.time).utc().format(DATETIME_FORMAT);
                    },
                    _: 'timestamp'
                }
            },
            {
                data: 'actions',
                render: function (data, type, row) {
                    if (afatSettings.permissions.addFatLink === true || afatSettings.permissions.manageAfat === true) {
                        return data;
                    } else {
                        return '';
                    }
                }
            }
        ],
        columnDefs: [
            {
                targets: [4],
                createdCell: function (td) {
                    $(td).addClass('text-right');
                }
            }
        ],
        language: {
            emptyTable: noFatlinksWarning
        },
        paging: false,
        ordering: false,
        searching: false,
        info: false
    });

    /**
     * Modal :: Close ESI fleet
     */
    let cancelEsiFleetModal = $(afatSettings.modal.cancelEsiFleetModal.element);
    manageModal(cancelEsiFleetModal);

    /**
     * Modal :: Delete FAT link
     */
    let deleteFatLinkModal = $(afatSettings.modal.deleteFatLinkModal.element);
    manageModal(deleteFatLinkModal);
});
